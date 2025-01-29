#include <ESP8266WiFi.h>
#include <PubSubClient.h>

// Wi-Fi instellingen
const char* ssid = "The-Mona"; // Vervang met jouw Wi-Fi naam
const char* password = "mona1234"; // Vervang met jouw Wi-Fi wachtwoord

// MQTT Broker instellingen
const char* mqtt_server = "192.168.69.69"; // Vervang met IP van jouw MQTT-broker (bijv. Raspberry Pi)

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
  delay(10);
  Serial.println("Verbinden met WiFi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Verbonden met WiFi!");
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Bericht ontvangen op topic: ");
  Serial.print(topic);
  Serial.print(" Berichteninhoud: ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Verbinden met MQTT...");
    if (client.connect("WemosD1Mini")) {
      Serial.println("Verbonden!");
      client.subscribe("test/topic");
    } else {
      Serial.print("Fout, rc=");
      Serial.print(client.state());
      Serial.println(" Wachten 5 sec...");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Stuur een bericht naar MQTT broker
  client.publish("test/topic", "Hallo vanaf Wemos!");
  delay(5000);
}
