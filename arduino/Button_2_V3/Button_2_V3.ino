#include <ESP8266WiFi.h>

// Vergroot MQTT packet size (zet dit vóór PubSubClient.h!)
#define MQTT_MAX_PACKET_SIZE 512
#include <PubSubClient.h>

#include <Adafruit_NeoPixel.h>
#include <ArduinoJson.h>

// ====================== DEVICE ======================
#define DEVICE_ID "02"   // uniek per button (bv btn-01, btn-02...)

// ====================== WIFI ======================
const char* ssid     = "The-Mona";
const char* password = "mona1234";

// ====================== MQTT ======================
const char* mqtt_server = "192.168.69.69";
const int   mqtt_port   = 1883;

WiFiClient espClient;
PubSubClient client(espClient);

// Topics (volgens contract)
String TOPIC_CMD_DEVICE = String("mona/buttons/") + DEVICE_ID + "/cmd";
const char* TOPIC_CMD_ALL = "mona/buttons/all/cmd";

String TOPIC_EVENT = String("mona/buttons/") + DEVICE_ID + "/event";
String TOPIC_STATE = String("mona/buttons/") + DEVICE_ID + "/state";

// ====================== NEOPIXEL ======================
#define LED_PIN   D4
#define NUMPIXELS 7
Adafruit_NeoPixel pixels(NUMPIXELS, LED_PIN, NEO_GRB + NEO_KHZ800);

uint8_t brightness = 255; // 0..255

// ====================== BUTTON ======================
#define BUTTON_PIN D1  // NO between D1 and GND, INPUT_PULLUP

bool buttonLatched = false;
const unsigned long DEBOUNCE_MS = 80;
unsigned long lastPressMs = 0;

// ====================== FLASH STATE (non-blocking) ======================
bool flashing = false;
bool flashOn = false;
unsigned long nextToggleMs = 0;

uint16_t flashIntervalMs = 120;
int togglesLeft = 0;      // times * 2
uint32_t flashColor = 0;

bool flashMask[NUMPIXELS];  // which leds flash

// ====================== UTILS ======================
void publishJson(const String& topic, JsonDocument& doc) {
  char buffer[MQTT_MAX_PACKET_SIZE];
  size_t n = serializeJson(doc, buffer, sizeof(buffer));
  client.publish(topic.c_str(), buffer, n);
}

void setAll(uint8_t r, uint8_t g, uint8_t b) {
  pixels.fill(pixels.Color(r, g, b));
  pixels.show();
}

void setOne(int i, uint8_t r, uint8_t g, uint8_t b) {
  if (i < 0 || i >= NUMPIXELS) return;
  pixels.setPixelColor(i, pixels.Color(r, g, b));
  pixels.show();
}

void stopFlash(bool clearLeds = false) {
  flashing = false;
  flashOn = false;
  togglesLeft = 0;
  if (clearLeds) {
    pixels.clear();
    pixels.show();
  }
}

void applyFlashFrame(bool on) {
  uint32_t c = on ? flashColor : 0;
  for (int i = 0; i < NUMPIXELS; i++) {
    if (flashMask[i]) pixels.setPixelColor(i, c);
  }
  pixels.show();
}

// ====================== STATE / EVENTS ======================
void sendEvent(const char* eventType) {
  StaticJsonDocument<192> doc;
  doc["id"] = DEVICE_ID;
  doc["event"] = eventType;
  doc["ip"] = WiFi.localIP().toString();
  publishJson(TOPIC_EVENT, doc);
}

void sendState() {
  StaticJsonDocument<256> doc;
  doc["id"] = DEVICE_ID;
  doc["brightness"] = brightness;
  doc["flashing"] = flashing;
  doc["flash_interval_ms"] = flashIntervalMs;
  doc["mixer"] = "neopixel"; // placeholder for consistent UI if you want
  // NOTE: je kan hier later batterij toevoegen, rssi, etc.
  doc["rssi"] = WiFi.RSSI();
  publishJson(TOPIC_STATE, doc);
}

// ====================== WIFI ======================
void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("📡 Connecting to WiFi: ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(400);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("✅ WiFi connected. IP: ");
  Serial.println(WiFi.localIP());
}

// ====================== MQTT CALLBACK ======================
void handle_cmd(JsonDocument& doc) {
  const char* type = doc["type"];
  if (!type) return;

  // brightness optional
  if (doc.containsKey("brightness")) {
    int br = doc["brightness"].as<int>();
    br = constrain(br, 0, 255);
    brightness = (uint8_t)br;
    pixels.setBrightness(brightness);
  }

  // ---- fill ----
  if (strcmp(type, "fill") == 0) {
    stopFlash(false);
    uint8_t r = doc["r"] | 0;
    uint8_t g = doc["g"] | 0;
    uint8_t b = doc["b"] | 0;
    setAll(r, g, b);
    sendState();
    return;
  }

  // ---- leds_set (array of {i,r,g,b}) ----
  if (strcmp(type, "leds_set") == 0) {
    stopFlash(false);

    if (!doc.containsKey("leds") || !doc["leds"].is<JsonArray>()) return;
    JsonArray arr = doc["leds"].as<JsonArray>();

    for (JsonObject led : arr) {
      int i = led["i"] | -1;
      if (i < 0 || i >= NUMPIXELS) continue;
      uint8_t r = led["r"] | 0;
      uint8_t g = led["g"] | 0;
      uint8_t b = led["b"] | 0;
      pixels.setPixelColor(i, pixels.Color(r, g, b));
    }
    pixels.show();
    sendState();
    return;
  }

  // ---- led_set (single) ----
  if (strcmp(type, "led_set") == 0) {
    stopFlash(false);
    int i = doc["i"] | -1;
    uint8_t r = doc["r"] | 0;
    uint8_t g = doc["g"] | 0;
    uint8_t b = doc["b"] | 0;
    setOne(i, r, g, b);
    sendState();
    return;
  }

  // ---- flash (non-blocking) ----
  if (strcmp(type, "flash") == 0) {
    stopFlash(false);

    uint8_t r = doc["r"] | 255;
    uint8_t g = doc["g"] | 255;
    uint8_t b = doc["b"] | 255;
    flashColor = pixels.Color(r, g, b);

    flashIntervalMs = doc["interval_ms"] | 120;
    flashIntervalMs = constrain(flashIntervalMs, 20, 5000);

    int times = doc["times"] | 6;
    times = constrain(times, 1, 100);

    // default: all leds
    for (int i = 0; i < NUMPIXELS; i++) flashMask[i] = true;

    // optional mask array [0..6]
    if (doc.containsKey("mask") && doc["mask"].is<JsonArray>()) {
      for (int i = 0; i < NUMPIXELS; i++) flashMask[i] = false;
      for (int idx : doc["mask"].as<JsonArray>()) {
        if (idx >= 0 && idx < NUMPIXELS) flashMask[idx] = true;
      }
    }

    flashing = true;
    flashOn = false;
    togglesLeft = times * 2;
    nextToggleMs = millis(); // start immediately

    sendState();
    return;
  }

  // ---- stop (stop flash, optional clear) ----
  if (strcmp(type, "stop") == 0) {
    bool clear = doc["clear"] | true;
    stopFlash(clear);
    sendState();
    return;
  }

  // ---- request_state ----
  if (strcmp(type, "request_state") == 0) {
    sendState();
    return;
  }
}

void callback(char* topic, byte* payload, unsigned int length) {
  // parse JSON
  StaticJsonDocument<512> doc;
  DeserializationError err = deserializeJson(doc, payload, length);
  if (err) {
    Serial.print("❌ JSON parse failed: ");
    Serial.println(err.c_str());
    return;
  }

  // We subscribe on device topic + broadcast topic, so both are "for us"
  handle_cmd(doc);
}

// ====================== MQTT CONNECT ======================
void reconnect() {
  while (!client.connected()) {
    Serial.print("🔌 Connecting MQTT... ");
    String clientId = String("mona-") + DEVICE_ID;

    if (client.connect(clientId.c_str())) {
      Serial.println("✅ MQTT connected");

      client.subscribe(TOPIC_CMD_DEVICE.c_str());
      client.subscribe(TOPIC_CMD_ALL);

      sendEvent("CONNECTED");
      sendState();
    } else {
      Serial.print("❌ failed rc=");
      Serial.print(client.state());
      Serial.println(" retry in 5s");
      delay(5000);
    }
  }
}

// ====================== SETUP/LOOP ======================
void setup() {
  Serial.begin(115200);
  delay(50);

  setup_wifi();

  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  pixels.begin();
  pixels.clear();
  pixels.setBrightness(brightness);
  pixels.show();

  pinMode(BUTTON_PIN, INPUT_PULLUP);
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();

  // ---- button debounce ----
  bool pressed = (digitalRead(BUTTON_PIN) == LOW);
  unsigned long now = millis();

  if (pressed && !buttonLatched && (now - lastPressMs >= DEBOUNCE_MS)) {
    buttonLatched = true;
    lastPressMs = now;

    sendEvent("PRESSED");
  } else if (!pressed) {
    buttonLatched = false;
  }

  // ---- flash state machine ----
  if (flashing && now >= nextToggleMs) {
    flashOn = !flashOn;
    applyFlashFrame(flashOn);

    togglesLeft--;
    nextToggleMs = now + flashIntervalMs;

    if (togglesLeft <= 0) {
      flashing = false;
      // einde flash -> leds uit (kan je ook "leave on" maken)
      applyFlashFrame(false);
      sendState();
    }
  }
}
