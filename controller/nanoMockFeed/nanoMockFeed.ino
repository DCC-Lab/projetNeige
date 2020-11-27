// Simulate PD nano by sending an array of 4 values at max rate

int c = 0;
int uniqueID = 2;

void setup() {
  Serial.begin(115200);
}

void loop() {
  Serial.println(String(uniqueID) + ',' + String(c) + ',' + String(c*2) + ',' + String(c*3) + ',' + String(c*4) + ',' + String(25) + ',' + String(65));
  c = (c + 1) % 100;
}
