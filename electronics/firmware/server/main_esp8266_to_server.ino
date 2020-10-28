#include <ESP8266WiFi.h>
const char* ssid     = "BELL484";
const char* password = "7DCFEDDE125A";
String data;

const char* host = "192.168.2.30";

void setup() {
  Serial.begin(115200);
  delay(2000);

  // We start by connecting to a WiFi network
  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  delay(1000);

  WiFi.begin(ssid, password);
  delay(1000);

  while (WiFi.status() != WL_CONNECTED) {
    delay(2000);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {

  WiFiClient client;
  const int httpPort = 80;
  if (!client.connect(host, httpPort)) {
    Serial.println("connection failed to server");
    delay(1000);
    return;
  }


  // String data = "pst=temperature>" + String(random(0,100)) +"||humidity>" + String(random(0,100)) + "||data>text";
  data = Serial.read();

  Serial.print("Requesting POST: ");
  // Send request to the server:
  client.println("POST / HTTP/1.1");
  client.println("Host: server_name");            
  client.println("Accept: */*");
  client.println("Content-Type: application/x-www-form-urlencoded");
  client.print("Content-Length: ");
  client.println(data.length());
  client.println();
  client.print(data);

  delay(2000); // Can be changed
  if (client.connected()) {
    client.stop();  // DISCONNECT FROM THE SERVER
  }
  Serial.println();
  Serial.println("closing connection");
  delay(5000);
}
