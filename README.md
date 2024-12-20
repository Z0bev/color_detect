# YOLO Object Detection System

A computer vision-based detection system using YOLO object detection and Arduino integration for input simulation.

# Project Structure
- `YOLO.py` - Main detection script using YOLOv5
- `bot_color_only.py` - Alternative color-based detection script
- `mouse.ino` - Arduino mouse control script
- `keyboard.ino` - Arduino keyboard control script

# Requirements
- Python 3.x
- PyTorch
- OpenCV
- Arduino Leonardo board

# Required Python packages:
```
opencv-python
torch
```

# Setup
1. Install the required Python packages
2. Upload either `mouse.ino` or `keyboard.ino` to your Arduino Leonardo board
3. Connect the Arduino to your computer and note the COM port
4. Adjust the COM port in the code if needed (default is COM8)

# Usage
Run the main detection script:
- Press F6 to toggle the detection system on/off
- Press Ctrl+C to exit the program

# Configuration
Key parameters in ValorantDetectorBot:
- `CONFIDENCE_THRESHOLD`: Detection confidence threshold (default: 0.5)
- `MIN_TIME_BETWEEN_DETECTIONS`: Minimum time between detections (default: 0.5s)
- `target_classes`: List of classes to detect (default: ['enemy', 'enemy_head', 'weapon'])

# Warning
This tool is for educational purposes only. Using automation tools in competitive games may violate terms of service and result in account bans.
