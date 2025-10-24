#include <ESP8266WiFi.h>
#include <EEPROM.h>
#include <WiFiManager.h>
#include "Adafruit_Thermal.h"
#include "SoftwareSerial.h"
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>

#define RX_PIN 3 
#define TX_PIN 1 

const char* serverName = "API_URL_HERE/get_records/?key=API_KEY_HERE";


WiFiClientSecure espClient;


const int ssidAddress = 0;
const int passwordAddress = 64;

bool apMode = false; 

SoftwareSerial mySerial(RX_PIN, TX_PIN); 
Adafruit_Thermal printer(&mySerial);

unsigned long lastRequestTime = 0;
const long requestInterval = 120000;

void setup() {
  mySerial.begin(9600);
  printer.begin();
  printer.reset();
  printer.setDefault();
  espClient.setInsecure();
  
  connectToWiFi();
}

void loop() {
  if (!apMode && WiFi.status() == WL_CONNECTED) {
    if (millis() - lastRequestTime > requestInterval) {
      lastRequestTime = millis();
      getRecordsFromAPI();
    }
  }
}

void getRecordsFromAPI() {
  HTTPClient http;  
  http.begin(espClient, serverName);  

  int httpResponseCode = http.GET();  

  if (httpResponseCode > 0) { 
    String payload = http.getString(); 

    Serial.println("Response from /get_records/:");
    Serial.println(payload);

    StaticJsonDocument<1024> doc;
    DeserializationError error = deserializeJson(doc, payload);

    if (error) {
      Serial.print(F("deserializeJson() failed: "));
      Serial.println(error.f_str());
      return;
    }

    JsonArray messages = doc["messages"];
    Serial.println("Messages:");
    for (JsonVariant value : messages) {
      Serial.println(value.as<String>());
      printer.println(value.as<String>());
      printer.println();
      printer.feed(1);
      printer.sleep();
    }
    
  } else {
    Serial.print("Error in HTTP request, code: ");
    Serial.println(httpResponseCode);
  }

  http.end();
}

// void callback(char* topic, byte* payload, unsigned int length) {
//   Serial.print("Message received on topic: ");
//   Serial.println(topic);
//   Serial.print("Message: ");
//   String result = "";
  
//   for (int i = 0; i < length; i++) {
//     result += char(payload[i]);
//     Serial.print((char)payload[i]);
//   }
//   printer.println(result);
//   printer.println();
//   printer.println();
//   printer.feed(1);
//   printer.sleep();
//   Serial.println();
// }

// void reconnect() {
//   while (!client.connected()) {
//     Serial.println("Reconnecting to MQTT server...");
//     if (client.connect("ArduinoClient")) {
//       Serial.println("Connected to MQTT server");
//       client.subscribe(mqttTopic);
//     } else {
//       Serial.print("Failed to connect to MQTT server, rc=");
//       Serial.print(client.state());
//       Serial.println(" Retrying in 5 seconds...");
//       delay(5000);
//     }
//   }
// }

void connectToWiFi() {
  char ssidBuffer[64];      
  char passwordBuffer[64];

  EEPROM.get(ssidAddress, ssidBuffer);
  EEPROM.get(passwordAddress, passwordBuffer);

  WiFiManager wifiManager;
  wifiManager.autoConnect("FaxPortal"); // captive portal

  String newSSID = WiFi.SSID();
  String newPassword = WiFi.psk();

  newSSID.toCharArray(ssidBuffer, 64);
  newPassword.toCharArray(passwordBuffer, 64);
  EEPROM.put(ssidAddress, ssidBuffer);
  EEPROM.put(passwordAddress, passwordBuffer);
  EEPROM.commit();

  apMode = false;

  Serial.println("Connected to WiFi");

  // client.setServer(mqttServer, mqttPort);
  // client.setCallback(callback);
  // reconnect();
}

