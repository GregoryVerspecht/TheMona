#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <Adafruit_NeoPixel.h>
#include <ArduinoJson.h>

// **Uniek nummer per ESP**
#define ESP_NUMBER 6  // Verander per ESP

// **Wi-Fi instellingen**
const char* ssid = "The-Mona";
const char* password = "mona1234";

// **MQTT Broker instellingen**
const char* mqtt_server = "192.168.69.69";

#define MQTT_MAX_PACKET_SIZE 256
WiFiClient espClient;
PubSubClient client(espClient);

// **Neopixel Instellingen**
#define PIN D4
#define NUMPIXELS 7
Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

// **Drukknop (NO Contact)**
#define BUTTON D1  // Knop tussen D1 en GND
bool buttonState = false;
int brightness = 255;  // Standaard helderheid (0-255)
int batteryLevel = 100; // Voor toekomstige batterijstatus

// **Wi-Fi setup**
void setup_wifi() {
  delay(10);
  Serial.begin(115200);
  Serial.println("\n📡 Verbinden met WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ WiFi Verbonden!");
}

// **MQTT Callback: ontvangt LED-updates en statusverzoeken**
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("📩 MQTT bericht ontvangen op topic: ");
  Serial.println(topic);

  char message[length + 1];
  strncpy(message, (char*)payload, length);
  message[length] = '\0';

  Serial.println("📜 Bericht: ");
  Serial.println(message);

  // **JSON-parsing**
  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, message);
  if (error) {
    Serial.println("❌ JSON parsing mislukt!");
    return;
  }

  // **Controleer of het bericht voor deze ESP is**
  if (doc.containsKey("id") && doc["id"] != ESP_NUMBER) {
    Serial.println("⏩ Bericht is niet voor deze ESP!");
    return;
  }

  // **Controleer of het een statusverzoek is**
  if (String(topic) == "esp/request_status") {
    sendStatusUpdate();
    return;
  }

  // **Controleer of alle LEDs moeten veranderen**
  if (doc.containsKey("led")) {
    const char* ledCommand = doc["led"];

    if (strcmp(ledCommand, "ON") == 0) {
      int r = doc["r"];
      int g = doc["g"];
      int b = doc["b"];
      if (doc.containsKey("brightness")) {
        brightness = doc["brightness"];
        pixels.setBrightness(brightness);
      }
      pixels.fill(pixels.Color(r, g, b));
      pixels.show();
      Serial.println("🔆 Alle LEDs AAN gezet!");
      sendLedStatus("ON");
      return;
    }

    if (strcmp(ledCommand, "OFF") == 0) {
      pixels.clear();
      pixels.show();
      Serial.println("💡 Alle LEDs UIT gezet!");
      sendLedStatus("OFF");
      return;
    }
  }

  // **Lees LED-instellingen**
  int led = doc["led"];
  int r = doc["r"];
  int g = doc["g"];
  int b = doc["b"];
  if (doc.containsKey("brightness")) {
    brightness = doc["brightness"];
    pixels.setBrightness(brightness);
  }

  // **Pas een specifieke LED aan**
  if (led >= 0 && led < NUMPIXELS) {
    pixels.setPixelColor(led, pixels.Color(r, g, b));
    pixels.show();
    Serial.printf("🔹 LED %d aangepast!\n", led);
  }

  // **Bevestiging terugsturen**
  sendLedStatus("UPDATE");
}

// **Herstel MQTT verbinding indien verbroken**
void reconnect() {
  while (!client.connected()) {
    Serial.print("🔌 Verbinden met MQTT...");
    if (client.connect(String(ESP_NUMBER).c_str())) {  
      Serial.println("✅ Verbonden met MQTT!");
      client.subscribe("neopixel/set");  
      client.subscribe("esp/request_status");  // ✅ Luistert naar statusverzoeken
      sendConnectedMessage();
    } else {
      Serial.print("❌ Fout, rc=");
      Serial.println(client.state());
      Serial.println("⏳ Wachten 5 sec...");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  setup_wifi();

  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

  pixels.begin();
  pixels.clear();
  pixels.setBrightness(brightness);

  // **Drukknop instellen met interne pull-up weerstand**
  pinMode(BUTTON, INPUT_PULLUP);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // **Drukknop controleren**
  if (digitalRead(BUTTON) == LOW && !buttonState) {
    buttonState = true;
    Serial.println("🎛️ Knop ingedrukt!");
    sendButtonPress();
    blinkRed(5000);  // 🔴 Knipperen voor 5 seconden
  } else if (digitalRead(BUTTON) == HIGH) {
    buttonState = false;
  }
}

// **Knipperfunctie: LEDS knipperen rood voor X milliseconden**
void blinkRed(int duration) {
  unsigned long startTime = millis();
  bool state = false;
  
  while (millis() - startTime < duration) {
    if (state) {
      pixels.fill(pixels.Color(255, 0, 0));  // Rood aan
    } else {
      pixels.clear();  // Uit
    }
    pixels.show();
    state = !state;
    delay(500);  // 🔴 Knippert elke 500ms
  }

  pixels.clear();  // LEDs weer uitzetten na knipperen
  pixels.show();
}

// **Functie om knopstatus + LED-status naar MQTT te sturen**
void sendButtonPress() {
  Serial.println("📡 Knopstatus verzenden...");
  StaticJsonDocument<128> doc;
  doc["id"] = ESP_NUMBER;
  doc["event"] = "PRESSED";

  char buffer[128];
  serializeJson(doc, buffer);
  client.publish("esp/status", buffer);
}

// **Functie om LED-status naar MQTT te sturen**
void sendLedStatus(const char* eventType) {
  Serial.println("📡 LED-status verzenden...");
  StaticJsonDocument<128> doc;
  doc["id"] = ESP_NUMBER;
  doc["event"] = eventType;
  doc["brightness"] = brightness;

  char buffer[128];
  serializeJson(doc, buffer);
  client.publish("neopixel/status", buffer);
}

// **Functie om bij opstart te melden dat de ESP verbonden is**
void sendConnectedMessage() {
  Serial.println("📡 Versturen: ESP verbonden");
  StaticJsonDocument<128> doc;
  doc["id"] = ESP_NUMBER;
  doc["status"] = "connected";

  char buffer[128];
  serializeJson(doc, buffer);
  client.publish("esp/status", buffer);
}

// **Functie om status op aanvraag te verzenden**
void sendStatusUpdate() {
  Serial.println("📡 Versturen: ESP status update");
  StaticJsonDocument<128> doc;
  doc["id"] = ESP_NUMBER;
  doc["status"] = "connected";
  doc["battery"] = batteryLevel;  // ❗ Voor toekomstige updates (bijv. batterijstatus)

  char buffer[128];
  serializeJson(doc, buffer);
  client.publish("esp/status", buffer);
}
