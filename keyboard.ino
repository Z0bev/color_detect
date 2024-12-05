#include <Keyboard.h>

void setup() {
  Serial.begin(9600);
  // Initialize keyboard control
  Keyboard.begin();
}

void loop() {
  if (Serial.available() > 0) {
    char signal = Serial.read();
    
    if (signal == '1') {
      // Type the '@' character
      Keyboard.press('@');
      delay(3);  // Short delay to simulate key press
      Keyboard.release('@');
      delay(3);  // Delay before allowing the next input
    }
  }
  
  delay(1);  // Small delay to prevent serial buffer issues
}
