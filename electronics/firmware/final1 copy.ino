#define PIN_A3   (17)
#define PIN_A4   (18)
#define PIN_A5   (19)
#define PIN_A6   (20)

int sensorValue1 = 0;
int sensorValue2 = 0;
int sensorValue3 = 0;
int sensorValue4 = 0;
int IDnumber = 1;
String dataString;

static const uint8_t pd1Pin = PIN_A6;
static const uint8_t pd2Pin = PIN_A5;
static const uint8_t pd3Pin = PIN_A4;
static const uint8_t pd4Pin = PIN_A3;

void setup() {
  Serial.begin(115200);
  delay(10);
}

void loop() {
  
  sensorValue1 = analogRead(pd1Pin);
  sensorValue2 = analogRead(pd2Pin);
  sensorValue3 = analogRead(pd3Pin);
  sensorValue4 = analogRead(pd4Pin);
  //ORDRE =  IR-small (PD1) / Blue-small (PD4) / IR-long (PD2) / Blue-long (PD3)
  dataString = String(IDnumber) + "," + String(sensorValue1) + "," + String(sensorValue4) + "," + String(sensorValue2) + "," + String(sensorValue3);
  Serial.println(dataString);
}
