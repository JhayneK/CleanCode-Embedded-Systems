#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

const int sensorPin = A0;
const float offset = -10.0;

void setup() {
  Serial.begin(115200);
  delay(1000);
}

void loop() {
  int analogValue = analogRead(sensorPin);
  
  // Conversão da leitura analógica para temperatura em Celsius
  float temperatura = (analogValue * 3.3 / 1024.0) * 100.0;

  temperatura += offset;

  Serial.printf("%.2f\n", temperatura);

  delay(500);
}

