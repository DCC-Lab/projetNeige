
void setup() {
  Serial.begin(115200);
}

void loop() {
  // read the input on analog pin 0:
  int sensorValue1 = analogRead(A6);
  int sensorValue2 = analogRead(A5);
  int sensorValue3 = analogRead(A4);
  int sensorValue4 = analogRead(A3);
  Serial.print("PD1:");
  Serial.print(sensorValue1);
  Serial.print("PD2:");
  Serial.print(sensorValue2);
  Serial.print("PD3:");
  Serial.print(sensorValue3);
  Serial.print("PD4:");
  Serial.print(sensorValue4);
  Serial.print("\n");
  delay(3);
}
