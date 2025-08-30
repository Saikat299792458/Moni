#define led 12
#define de 2000
/** Manchester Coding:
*** First two bits indicate if the byte is redundant or not
*** Next 16 bits contain the data
*** Next 1 bit is the ending bit
*** After each byte, the LED must be turned on
*** Each bit sequence must be therefore 19 characters long.
*** Add dynamic transmission capability
*/

void setup() {
  Serial.begin(9600);
  pinMode(led, OUTPUT);
}

void loop() {
  Serial.println("What's Your message?:");
  while (Serial.available() == 0) {}
  String message = Serial.readString();
  Serial.print("Your Message: ");
  Serial.print(message);
  Serial.println("Bit Sequence:");
  bool is_new = true;
  for (int i = 0; i < message.length() - 1; i++)
  {
    char character = message[i];
    for (int k = 0; k < 4; k++)
    {
      digitalWrite(led, LOW);
      delayMicroseconds(de);
      if (is_new)
      {
        digitalWrite(led, HIGH);
        is_new = false;
      }
      delayMicroseconds(de);
      for (int j = 7; j >= 0; j--)
      {
        bool byte = bitRead(character, j);
        Serial.print(byte?"01":"10");
        if (byte)
        {
          digitalWrite(led, LOW);
          delayMicroseconds(de);
          digitalWrite(led, HIGH);
          delayMicroseconds(de);
        }
        else
        {
          digitalWrite(led, HIGH);
          delayMicroseconds(de);
          digitalWrite(led, LOW);
          delayMicroseconds(de);
        }
      }
      digitalWrite(led, LOW);
      delayMicroseconds(de);
      digitalWrite(led, HIGH);
      delay(100); // Decrease to increase speed
    }
    Serial.println();
  }
}
