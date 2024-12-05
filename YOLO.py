import cv2
import numpy as np
import torch
from torch import amp
from PIL import ImageGrab
import serial
import time
import keyboard
from win32api import GetSystemMetrics
import requests
import os
class ValorantDetectorBot:
    def __init__(self, toggle_key='f6', target_classes=None):
        self.SCREEN_WIDTH = GetSystemMetrics(0)
        self.SCREEN_HEIGHT = GetSystemMetrics(1)  
        self.REGION_WIDTH = 60 
        self.REGION_HEIGHT = 102 
        
        # settings
        self.is_enabled = False
        self.toggle_key = toggle_key
        self.CONFIDENCE_THRESHOLD = 0.5
        self.MIN_TIME_BETWEEN_DETECTIONS = 0.5
        self.target_classes = target_classes or ['enemy', 'enemy_head', 'weapon']
        self.arduino = self.setup_arduino()
        
        if not self.arduino:
            raise RuntimeError("Failed to initialize Arduino")

        
        self.model = self.load_valorant_model()
        if not self.model:
            if self.arduino:
                self.arduino.close()
            raise RuntimeError("Failed to load YOLO model")

        keyboard.add_hotkey(self.toggle_key, self.toggle_program)
        print(f"Toggle key set to {toggle_key}. Press to enable/disable.")
        
    def load_valorant_model(self):
        try:
            model_url = 'https://github.com/Krushu24365/valorant_yolodetectionmodel/raw/valyolov5/winvalorant.pt'
            response = requests.get(model_url)
            
            if response.status_code != 200:
                raise ValueError(f"Failed to download model. Status code: {response.status_code}")
            with open('valorant_model.pt', 'wb') as f:
                f.write(response.content)
                
            model = torch.hub.load('ultralytics/yolov5', 'custom', path='valorant_model.pt')
            
            
            model.conf = self.CONFIDENCE_THRESHOLD  
            model.iou = 0.45
            
            print("Valorant YOLO model loaded successfully!")
            return model
        
        except Exception as e:
            print(f"Error loading Valorant YOLO model: {e}")
            return None

    def setup_arduino(self):
        try:
            # List all available ports
            import serial.tools.list_ports
            ports = list(serial.tools.list_ports.comports())
            print("Available ports:")
            for p in ports:
                print(f"  {p}")
            
            # Adjust COM port as needed
            arduino = serial.Serial('COM8', 9600, timeout=1)
            print(f"Connected to {arduino.name}")
            time.sleep(2)
            return arduino
        
        except Exception as e:
            print(f"Error connecting to Arduino: {e}")
            return None

    def capture_screen(self):
        screen_x = (self.SCREEN_WIDTH - self.REGION_WIDTH) // 2
        screen_y = (self.SCREEN_HEIGHT - self.REGION_HEIGHT) // 2
        
        region = (
            screen_x,
            screen_y,
            screen_x + self.REGION_WIDTH,
            screen_y + self.REGION_HEIGHT
        )
        return np.array(ImageGrab.grab(bbox=region))

    def detect_objects(self, image):
     with torch.amp.autocast(device_type='cuda'):
        results = self.model(image)
        detections = results.pandas().xyxy[0]
        if self.target_classes:
            detections = detections[detections['name'].isin(self.target_classes)]
        valid_detections = detections[detections['confidence'] >= self.CONFIDENCE_THRESHOLD]
        return not valid_detections.empty, valid_detections
        

    def toggle_program(self):
        self.is_enabled = not self.is_enabled
        print(f"Program {'ENABLED' if self.is_enabled else 'DISABLED'}")

    def run(self):
        if not self.model or not self.arduino:
            print("Failed to initialize model or Arduino. Exiting.")
            return
        
        print(f"Bot started. Press {self.toggle_key} to toggle. Press Ctrl+C to exit.")
        last_detection_time = 0
        
        try:
            while True:
                
                if not self.is_enabled:
                    time.sleep(0.01)
                    continue
                
                current_time = time.time()
                screen = self.capture_screen()
            
                with torch.amp.autocast('cuda'):
                    detected, detection_details = self.detect_objects(screen)
                
                if detected:
                    if current_time - last_detection_time >= self.MIN_TIME_BETWEEN_DETECTIONS:
                        print("Valorant Objects detected:")
                        for _, row in detection_details.iterrows():
                            print(f"  {row['name']} (Confidence: {row['confidence']:.1f})")
                        
                        # Send signal to Arduino
                        self.arduino.write(b'1')
                        
                        # Read response from Arduino
                        response = self.arduino.readline().decode().strip()
                        if response:
                            print(f"Arduino response: {response}")
                        
                        last_detection_time = current_time
                
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            print("\nBot stopped.")
        finally:
            if self.arduino:
                self.arduino.close()

def main():
    bot = ValorantDetectorBot()
    bot.run()

if __name__ == "__main__":
    main()