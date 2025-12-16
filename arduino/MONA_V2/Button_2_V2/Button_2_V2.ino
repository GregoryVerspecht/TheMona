#include <ESP8266WiFi.h>

// Vergroot MQTT packet size (zet dit vóór PubSubClient.h!)
#define MQTT_MAX_PACKET_SIZE 512
#include <PubSubClient.h>

#include <Adafruit_NeoPixel.h>
#include <ArduinoJson.h>

// ========= Uniek nummer per ESP =========
#define ESP_NUMBER 2  // ← wijzig per device

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
int brightness = 255;   // 0–255

// ========= Drukknop =========
#define BUTTON D1            // NO, tussen D1 en GND, INPUT_PULLUP
bool buttonLatched = false;  // edge detectie
const unsigned long DEBOUNCE_MS = 80;
unsigned long lastPressMs = 0;

// ========= Status =========
int batteryLevel = 100; // placeholder

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
}

// ========= Helpers =========
bool isCmdForMeOrBroadcast(const JsonVariant& idField) {
  // Toegestaan:
  //  - géén id → broadcast
  //  - id == ESP_NUMBER (int)
  //  - id == "ALL" (string) → broadcast
  if (idField.isNull()) return true;
  if (idField.is<int>()) return idField.as<int>() == ESP_NUMBER;
  if (idField.is<const char*>()) {
    const char* s = idField.as<const char*>();
    return (strcmp(s, "ALL") == 0);
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

  // Veilig kopiëren naar 0-terminated buffer
  static char msg[MQTT_MAX_PACKET_SIZE];
  unsigned int n = min(length, (unsigned int) (sizeof(msg) - 1));
  memcpy(msg, payload, n);
  msg[n] = '\0';
  Serial.println("📜 Payload:");
  Serial.println(msg);

  // JSON-parsing (ruimer buffer)
  StaticJsonDocument<512> doc;
  DeserializationError err = deserializeJson(doc, msg);
  if (err) {
    Serial.print("❌ JSON parsing mislukt: ");
    Serial.println(err.c_str());
    return;
  }

  // Status request topic afhandelen (optioneel: via payload)
  if (String(topic) == TOPIC_REQ_STATUS) {
    // Als er een id is en niet voor ons/broadcast → negeren
    if (!isCmdForMeOrBroadcast(doc["id"])) {
      Serial.println("⏩ Statusrequest niet voor deze ESP.");
      return;
    }
    sendStatusUpdate();
    return;
  }

  // Alleen commands op 'neopixel/set' verwerken
  if (String(topic) != TOPIC_CMD) return;

  // Filter op id/broadcast
  if (!isCmdForMeOrBroadcast(doc["id"])) {
    Serial.println("⏩ Command niet voor deze ESP.");
    return;
  }

  // Brightness (optioneel)
  if (doc.containsKey("brightness")) {
    int br = doc["brightness"].as<int>();
    br = constrain(br, 0, 255);
    brightness = br;
    pixels.setBrightness(brightness);
  }

  // 1) Mode op alle LEDs via led="ON"/"OFF"
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

  // 2) Specifieke pixel aanpassen: verwacht numerieke 'led' + r,g,b
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
    String clientId = String("esp8266-") + String(ESP_NUMBER);
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

  pinMode(BUTTON, INPUT_PULLUP); // intern pull-up
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Knop met debounce (LOW = ingedrukt)
  bool pressed = (digitalRead(BUTTON) == LOW);
  unsigned long now = millis();

  if (pressed && !buttonLatched && (now - lastPressMs >= DEBOUNCE_MS)) {
    buttonLatched = true;
    lastPressMs = now;

    Serial.println("🎛️ Knop ingedrukt → PRESSED publiceren");
    sendButtonPress();
    // Geen lokale blink! Server (Flask) bepaalt LED-gedrag.
  } else if (!pressed) {
    buttonLatched = false;
  }
}

// ========= Publish helpers =========
void sendButtonPress() {
  StaticJsonDocument<128> doc;
  doc["id"] = ESP_NUMBER;
  doc["event"] = "PRESSED";
  publishJson(TOPIC_BTN_STATUS, doc);
}

void sendLedStatus(const char* eventType) {
  StaticJsonDocument<128> doc;
  doc["id"] = ESP_NUMBER;
  doc["event"] = eventType;
  doc["brightness"] = brightness;
  publishJson(TOPIC_LED_STATUS, doc);
}

void sendConnectedMessage() {
  StaticJsonDocument<128> doc;
  doc["id"] = ESP_NUMBER;
  doc["status"] = "connected";
  publishJson(TOPIC_BTN_STATUS, doc);
}

void sendStatusUpdate() {
  StaticJsonDocument<128> doc;
  doc["id"] = ESP_NUMBER;
  doc["status"] = "connected";
  doc["battery"] = batteryLevel;
  publishJson(TOPIC_BTN_STATUS, doc);
}
