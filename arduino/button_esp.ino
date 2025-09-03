#include <ESP8266WiFi.h>

// Vergroot MQTT packet size (zet dit vóór PubSubClient.h!)
#define MQTT_MAX_PACKET_SIZE 512
#include <PubSubClient.h>

#include <Adafruit_NeoPixel.h>
#include <ArduinoJson.h>

// ========= Auto-ID generatie =========
// Kies één van deze methodes:

// METHODE 1: Gebruik laatste 2 bytes van MAC adres (meest gebruikelijk)
String getESPId() {
  uint8_t mac[6];
  WiFi.macAddress(mac);
  // Laatste 2 bytes van MAC → hex string
  return String(mac[4], HEX) + String(mac[5], HEX);
}

// METHODE 2: Gebruik Chip ID (uniek per ESP8266)
/*
String getESPId() {
  return String(ESP.getChipId());
}
*/

// METHODE 3: Gebruik Flash Chip ID
/*
String getESPId() {
  return String(ESP.getFlashChipId());
}
*/

// METHODE 4: Korte versie van MAC (alleen laatste byte)
/*
String getESPId() {
  uint8_t mac[6];
  WiFi.macAddress(mac);
  return String(mac[5]);
}
*/

// Globale variabelen
String ESP_ID;        // Wordt runtime bepaald
int ESP_NUMBER;       // Voor backwards compatibility

// ========= Wi-Fi =========
const char* ssid     = "The-Mona";
const char* password = "mona1234";

// ========= MQTT =========
const char* mqtt_server = "192.168.69.69";
WiFiClient espClient;
PubSubClient client(espClient);

// Topics
const char* TOPIC_CMD          = "neopixel/set";
const char* TOPIC_REQ_STATUS   = "esp/request_status";
const char* TOPIC_BTN_STATUS   = "esp/status";
const char* TOPIC_LED_STATUS   = "neopixel/status";

// ========= NeoPixel =========
#define PIN D4
#define NUMPIXELS 7
Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);
int brightness = 255;

// ========= Drukknop =========
#define BUTTON D1
bool buttonLatched = false;
const unsigned long DEBOUNCE_MS = 80;
unsigned long lastPressMs = 0;

// ========= Status =========
int batteryLevel = 100;

// ========= Wi-Fi =========
void setup_wifi() {
  delay(10);
  Serial.begin(115200);
  Serial.println("\n📡 Verbinden met WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(400);
    Serial.print(".");
  }
  Serial.print("\n✅ WiFi Verbonden! IP: ");
  Serial.println(WiFi.localIP());
  
  // Genereer uniek ESP ID na WiFi verbinding
  ESP_ID = getESPId();
  ESP_NUMBER = ESP_ID.toInt(); // Voor backwards compatibility
  
  Serial.print("🆔 ESP ID: ");
  Serial.println(ESP_ID);
  Serial.print("🔢 ESP NUMBER: ");
  Serial.println(ESP_NUMBER);
  
  // Print MAC adres voor debugging
  Serial.print("📶 MAC Adres: ");
  Serial.println(WiFi.macAddress());
}

// ========= Helpers =========
bool isCmdForMeOrBroadcast(const JsonVariant& idField) {
  if (idField.isNull()) return true;
  
  // Check zowel string als int versie van ons ID
  if (idField.is<int>()) {
    return idField.as<int>() == ESP_NUMBER;
  }
  if (idField.is<const char*>()) {
    const char* s = idField.as<const char*>();
    return (strcmp(s, "ALL") == 0 || strcmp(s, ESP_ID.c_str()) == 0);
  }
  return false;
}

void setAllRGB(uint8_t r, uint8_t g, uint8_t b) {
  pixels.fill(pixels.Color(r, g, b));
  pixels.show();
}

void publishJson(const char* topic, JsonDocument& doc) {
  char buffer[256];
  size_t n = serializeJson(doc, buffer, sizeof(buffer));
  client.publish(topic, buffer, n);
}

// ========= MQTT Callback =========
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("📩 MQTT op topic: ");
  Serial.println(topic);

  static char msg[MQTT_MAX_PACKET_SIZE];
  unsigned int n = min(length, (unsigned int) (sizeof(msg) - 1));
  memcpy(msg, payload, n);
  msg[n] = '\0';
  Serial.println("📜 Payload:");
  Serial.println(msg);

  StaticJsonDocument<512> doc;
  DeserializationError err = deserializeJson(doc, msg);
  if (err) {
    Serial.print("❌ JSON parsing mislukt: ");
    Serial.println(err.c_str());
    return;
  }

  if (String(topic) == TOPIC_REQ_STATUS) {
    if (!isCmdForMeOrBroadcast(doc["id"])) {
      Serial.println("⏩ Statusrequest niet voor deze ESP.");
      return;
    }
    sendStatusUpdate();
    return;
  }

  if (String(topic) != TOPIC_CMD) return;

  if (!isCmdForMeOrBroadcast(doc["id"])) {
    Serial.println("⏩ Command niet voor deze ESP.");
    return;
  }

  // Brightness
  if (doc.containsKey("brightness")) {
    int br = doc["brightness"].as<int>();
    br = constrain(br, 0, 255);
    brightness = br;
    pixels.setBrightness(brightness);
  }

  // LED commands
  if (doc.containsKey("led") && doc["led"].is<const char*>()) {
    const char* ledCmd = doc["led"].as<const char*>();
    if (strcmp(ledCmd, "ON") == 0) {
      int r = doc["r"] | 0;
      int g = doc["g"] | 0;
      int b = doc["b"] | 0;
      setAllRGB(r, g, b);
      Serial.println("🔆 Alle LEDs AAN gezet!");
      sendLedStatus("ON");
      return;
    } else if (strcmp(ledCmd, "OFF") == 0) {
      pixels.clear();
      pixels.show();
      Serial.println("💡 Alle LEDs UIT gezet!");
      sendLedStatus("OFF");
      return;
    }
  }

  if (doc.containsKey("led") && doc["led"].is<int>()) {
    int idx = doc["led"].as<int>();
    if (idx >= 0 && idx < NUMPIXELS) {
      int r = doc["r"] | 0;
      int g = doc["g"] | 0;
      int b = doc["b"] | 0;
      pixels.setPixelColor(idx, pixels.Color(r, g, b));
      pixels.show();
      Serial.printf("🔹 LED %d aangepast!\n", idx);
      sendLedStatus("UPDATE");
    }
  }
}

// ========= MQTT (re)connect =========
void reconnect() {
  while (!client.connected()) {
    Serial.print("🔌 Verbinden met MQTT...");
    String clientId = String("esp8266-") + ESP_ID;  // Gebruik auto-generated ID
    if (client.connect(clientId.c_str())) {
      Serial.println("✅ Verbonden met MQTT!");
      client.subscribe(TOPIC_CMD);
      client.subscribe(TOPIC_REQ_STATUS);
      sendConnectedMessage();
    } else {
      Serial.print("❌ Fout, rc=");
      Serial.println(client.state());
      Serial.println("⏳ Wachten 5 sec...");
      delay(5000);
    }
  }
}

// ========= Setup/Loop =========
void setup() {
  Serial.begin(115200);
  setup_wifi();

  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

  pixels.begin();
  pixels.clear();
  pixels.setBrightness(brightness);
  pixels.show();

  pinMode(BUTTON, INPUT_PULLUP);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  bool pressed = (digitalRead(BUTTON) == LOW);
  unsigned long now = millis();

  if (pressed && !buttonLatched && (now - lastPressMs >= DEBOUNCE_MS)) {
    buttonLatched = true;
    lastPressMs = now;
    Serial.println("🎛️ Knop ingedrukt → PRESSED publiceren");
    sendButtonPress();
  } else if (!pressed) {
    buttonLatched = false;
  }
}

// ========= Publish helpers =========
void sendButtonPress() {
  StaticJsonDocument<128> doc;
  doc["id"] = ESP_ID;  // Gebruik string ID
  doc["mac"] = WiFi.macAddress();  // Extra info voor identificatie
  doc["event"] = "PRESSED";
  publishJson(TOPIC_BTN_STATUS, doc);
}

void sendLedStatus(const char* eventType) {
  StaticJsonDocument<128> doc;
  doc["id"] = ESP_ID;
  doc["mac"] = WiFi.macAddress();
  doc["event"] = eventType;
  doc["brightness"] = brightness;
  publishJson(TOPIC_LED_STATUS, doc);
}

void sendConnectedMessage() {
  StaticJsonDocument<128> doc;
  doc["id"] = ESP_ID;
  doc["mac"] = WiFi.macAddress();
  doc["chip_id"] = ESP.getChipId();  // Extra hardware info
  doc["status"] = "connected";
  publishJson(TOPIC_BTN_STATUS, doc);
}

void sendStatusUpdate() {
  StaticJsonDocument<256> doc;
  doc["id"] = ESP_ID;
  doc["mac"] = WiFi.macAddress();
  doc["chip_id"] = ESP.getChipId();
  doc["status"] = "connected";
  doc["battery"] = batteryLevel;
  doc["uptime"] = millis() - bootTime;
  doc["free_heap"] = ESP.getFreeHeap();
  doc["wifi_rssi"] = WiFi.RSSI();
  publishJson(TOPIC_BTN_STATUS, doc);
}

void sendDiscoveryResponse() {
  StaticJsonDocument<512> doc;
  doc["id"] = ESP_ID;
  doc["mac"] = WiFi.macAddress();
  doc["chip_id"] = ESP.getChipId();
  doc["flash_id"] = ESP.getFlashChipId();
  doc["ip"] = WiFi.localIP().toString();
  doc["rssi"] = WiFi.RSSI();
  doc["uptime"] = millis() - bootTime;
  doc["free_heap"] = ESP.getFreeHeap();
  doc["cpu_freq"] = ESP.getCpuFreqMHz();
  doc["flash_size"] = ESP.getFlashChipRealSize();
  doc["sdk_version"] = ESP.getSdkVersion();
  doc["boot_version"] = ESP.getBootVersion();
  doc["battery"] = batteryLevel;
  doc["brightness"] = brightness;
  doc["num_pixels"] = NUMPIXELS;
  doc["device_type"] = "neopixel_controller";
  doc["firmware_version"] = "1.0";
  doc["timestamp"] = millis();
  
  publishJson(TOPIC_DISCOVERY, doc);
  Serial.println("🔍 Discovery response verzonden");
}

void sendHeartbeat() {
  StaticJsonDocument<256> doc;
  doc["id"] = ESP_ID;
  doc["timestamp"] = millis();
  doc["uptime"] = millis() - bootTime;
  doc["free_heap"] = ESP.getFreeHeap();
  doc["wifi_rssi"] = WiFi.RSSI();
  doc["battery"] = batteryLevel;
  doc["status"] = "alive";
  
  publishJson(TOPIC_HEARTBEAT, doc);
  Serial.println("💓 Heartbeat verzonden");
}