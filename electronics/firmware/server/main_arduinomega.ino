#include "DHT.h"
#include <SoftwareSerial.h>
#define DHTPIN 7
#define DHTTYPE DHT22 // DHT 22 (AM2302), AM2321

SoftwareSerial toESP(19, 18);
DHT dht(DHTPIN, DHTTYPE);
String str;


void setup() {
  Serial.begin(115200);
  toESP.begin(115200);
  dht.begin();
  delay(2000);
}
void loop()
{
  float h = dht.readHumidity();
  // Read temperature as Celsius (the default)
  float t = dht.readTemperature();
  //  Serial.print("Arduino - H: ");
  //  Serial.print(h);
  //  Serial.println("% ");
  //  Serial.print("Arduino - T: ");
  //  Serial.print(t);
  //  Serial.println("C");
    str = String("coming from arduino: ") + String("H= ") + String(h) + String("%, T= ") + String(t) + String("C");
  //  toESP.print("Humidity: ");
  //  toESP.println(h);
  //  str = toESP.read();
    toESP.println(str);
}
