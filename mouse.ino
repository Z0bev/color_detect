#include <Mouse.h>

void setup() {
  Serial.begin(9600);
  // Initialize mouse control
  Mouse.begin();
}

void loop() {
  if (Serial.available() > 0) {
    char signal = Serial.read();
    
    if (signal == '1') {
      // Perform left mouse click
      Mouse.press(MOUSE_LEFT);
      delay(3);  // Short delay for the click
      Mouse.release(MOUSE_LEFT);
      delay(3);  // Delay before allowing next click to prevent double-clicks
    }
  }
  
  delay(1);  // Small delay to prevent serial buffer issues
}