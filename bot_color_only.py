import pyautogui
import numpy as np
import cv2
from PIL import ImageGrab
import serial
import time
import keyboard  
class ColorClickerBot:
    def __init__(self, toggle_key='f6'):
        # Setup Arduino
        self.arduino = self.setup_arduino()
        
        # Toggle switch
        self.is_enabled = False
        self.toggle_key = toggle_key
        
        # Setup toggle key listener
        keyboard.add_hotkey(self.toggle_key, self.toggle_program)
        print(f"Toggle key set to {toggle_key}. Press to enable/disable.")
        
        # Color detection parameters
        self.TARGET_COLOR = (128, 0, 128)  # PRPL
        self.REGION_SIZE = 5
        self.MIN_TIME_BETWEEN_CLICKS = 0.001

    def setup_arduino(self):
        """Setup serial communication with Arduino Leonardo"""
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
 
    def get_screen_center(self):
        """Capture the center region of the screen"""
        screen_width, screen_height = pyautogui.size()
        center_x = screen_width // 2
        center_y = screen_height // 2
        
        region = (
            center_x - self.REGION_SIZE//2,
            center_y - self.REGION_SIZE//2,
            center_x + self.REGION_SIZE//2,
            center_y + self.REGION_SIZE//2
        )
        
        return ImageGrab.grab(bbox=region)

    def detect_color(self, image):
        """Detect if target color is present in image"""
        img_np = np.array(image)
        
        # Convert target_color to HSV
        target_hsv = cv2.cvtColor(np.uint8([[self.TARGET_COLOR]]), cv2.COLOR_RGB2HSV)[0][0]
        
        # Convert image to HSV
        img_hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)
        
        # Create color mask
        lower = np.array([target_hsv[0] - 15, 30, 30])
        upper = np.array([target_hsv[0] + 15, 255, 255])
        mask = cv2.inRange(img_hsv, lower, upper)
        
        # Calculate percentage of matching pixels
        match_percentage = (np.sum(mask) / 255) / mask.size * 100
        return match_percentage > 5, match_percentage

    def toggle_program(self):
        """Toggle program on/off"""
        self.is_enabled = not self.is_enabled
        print(f"Program {'ENABLED' if self.is_enabled else 'DISABLED'}")

    def run(self):
        """Main bot loop"""
        if not self.arduino:
            return
        
        print(f"Bot started. Press {self.toggle_key} to toggle. Press Ctrl+C to exit.")
        
        last_detection_time = 0
        
        try:
            while True:
                # Check if program is enabled
                if not self.is_enabled:
                    time.sleep(0.01)
                    continue
                
                current_time = time.time()
                
                # Capture center of screen
                screen = self.get_screen_center()
                
                # Check for color
                detected, match_percent = self.detect_color(screen)
                
                if detected:
                    if current_time - last_detection_time >= self.MIN_TIME_BETWEEN_CLICKS:
                        print(f"Color detected! Match: {match_percent:.1f}%")
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
    bot = ColorClickerBot()
    bot.run()

if __name__ == "__main__":
    main()