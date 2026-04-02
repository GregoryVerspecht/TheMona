#pragma once

#include <ESP8266WiFi.h>
#define MQTT_MAX_PACKET_SIZE 512
#include <PubSubClient.h>
#include <Adafruit_NeoPixel.h>
#include <ArduinoJson.h>

// ====================== MQTT TOPICS ======================
WiFiClient espClient;
PubSubClient client(espClient);

String TOPIC_CMD_DEVICE = String("mona/buttons/") + DEVICE_ID + "/cmd";
const char* TOPIC_CMD_ALL = "mona/buttons/all/cmd";
String TOPIC_EVENT = String("mona/buttons/") + DEVICE_ID + "/event";
String TOPIC_STATE = String("mona/buttons/") + DEVICE_ID + "/state";

// ====================== NEOPIXEL ======================
Adafruit_NeoPixel pixels(NUMPIXELS, LED_PIN, NEO_GRB + NEO_KHZ800);
uint8_t brightness = 255;

// ====================== BUTTON ======================
bool buttonLatched = false;
const unsigned long DEBOUNCE_MS = 80;
unsigned long lastPressMs = 0;

// ====================== FLASH STATE ======================
bool flashing = false;
bool flashOn = false;
unsigned long nextToggleMs = 0;
uint16_t flashIntervalMs = 120;
int togglesLeft = 0;
uint32_t flashColor = 0;
bool flashMask[NUMPIXELS];

// ====================== HEARTBEAT ======================
const unsigned long HEARTBEAT_MS = 15000;
unsigned long lastHeartbeatMs = 0;

// ====================== BATTERY ======================
int readBatteryPercent() {
  if (!BATTERY_ENABLED) return -1;
  int raw = analogRead(A0);
  float vPin  = (raw / 1023.0f) * BATTERY_VREF;
  float vBatt = vPin / BATTERY_DIVIDER;
  int pct = (int)((vBatt - BATTERY_V_EMPTY) / (BATTERY_V_FULL - BATTERY_V_EMPTY) * 100.0f);
  return constrain(pct, 0, 100);
}

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
  flashing    = false;
  flashOn     = false;
  togglesLeft = 0;
  if (clearLeds) { pixels.clear(); pixels.show(); }
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
  StaticJsonDocument<384> doc;
  doc["id"]    = DEVICE_ID;
  doc["event"] = eventType;
  doc["ip"]    = WiFi.localIP().toString();
  publishJson(TOPIC_EVENT, doc);
}

void sendState() {
  StaticJsonDocument<384> doc;
  doc["id"]                = DEVICE_ID;
  doc["brightness"]        = brightness;
  doc["flashing"]          = flashing;
  doc["flash_interval_ms"] = flashIntervalMs;
  doc["rssi"]              = WiFi.RSSI();
  doc["ip"]                = WiFi.localIP().toString();
  int batt = readBatteryPercent();
  if (batt >= 0) doc["battery"] = batt;
  publishJson(TOPIC_STATE, doc);
}

// ====================== WIFI ======================
void setup_wifi() {
  pixels.fill(pixels.Color(40, 40, 0));  // geel = verbinden
  pixels.show();

  Serial.print("Connecting to WiFi: ");
  Serial.println(WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(400);
    Serial.print(".");
  }
  Serial.print("\nWiFi connected. IP: ");
  Serial.println(WiFi.localIP());

  for (int i = 0; i < 2; i++) {
    pixels.fill(pixels.Color(0, 60, 0)); pixels.show(); delay(200);
    pixels.clear();                       pixels.show(); delay(200);
  }
}

// ====================== MQTT CALLBACK ======================
void handle_cmd(JsonDocument& doc) {
  const char* type = doc["type"];
  if (!type) return;

  if (doc.containsKey("brightness")) {
    brightness = (uint8_t)constrain(doc["brightness"].as<int>(), 0, 255);
    pixels.setBrightness(brightness);
  }

  if (strcmp(type, "fill") == 0) {
    stopFlash(false);
    setAll(doc["r"] | 0, doc["g"] | 0, doc["b"] | 0);
    sendState();
    return;
  }

  if (strcmp(type, "leds_set") == 0) {
    stopFlash(false);
    if (!doc.containsKey("leds") || !doc["leds"].is<JsonArray>()) return;
    for (JsonObject led : doc["leds"].as<JsonArray>()) {
      int i = led["i"] | -1;
      if (i < 0 || i >= NUMPIXELS) continue;
      pixels.setPixelColor(i, pixels.Color(led["r"] | 0, led["g"] | 0, led["b"] | 0));
    }
    pixels.show();
    sendState();
    return;
  }

  if (strcmp(type, "led_set") == 0) {
    stopFlash(false);
    setOne(doc["i"] | -1, doc["r"] | 0, doc["g"] | 0, doc["b"] | 0);
    sendState();
    return;
  }

  if (strcmp(type, "flash") == 0) {
    stopFlash(false);
    flashColor      = pixels.Color(doc["r"] | 255, doc["g"] | 255, doc["b"] | 255);
    flashIntervalMs = constrain((int)(doc["interval_ms"] | 120), 20, 5000);
    int times       = constrain((int)(doc["times"] | 6), 1, 100);

    for (int i = 0; i < NUMPIXELS; i++) flashMask[i] = true;
    if (doc.containsKey("mask") && doc["mask"].is<JsonArray>()) {
      for (int i = 0; i < NUMPIXELS; i++) flashMask[i] = false;
      for (int idx : doc["mask"].as<JsonArray>()) {
        if (idx >= 0 && idx < NUMPIXELS) flashMask[idx] = true;
      }
    }

    flashing     = true;
    flashOn      = false;
    togglesLeft  = times * 2;
    nextToggleMs = millis();
    sendState();
    return;
  }

  if (strcmp(type, "stop") == 0) {
    stopFlash(doc["clear"] | true);
    sendState();
    return;
  }

  if (strcmp(type, "request_state") == 0) {
    sendState();
    return;
  }
}

void callback(char* topic, byte* payload, unsigned int length) {
  StaticJsonDocument<512> doc;
  DeserializationError err = deserializeJson(doc, payload, length);
  if (err) {
    Serial.print("JSON parse failed: "); Serial.println(err.c_str());
    return;
  }
  handle_cmd(doc);
}

// ====================== MQTT RECONNECT ======================
void reconnect() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi lost, reconnecting...");
    setup_wifi();
  }

  pixels.fill(pixels.Color(0, 0, 40));  // blauw = MQTT verbinden
  pixels.show();

  while (!client.connected()) {
    Serial.print("Connecting MQTT... ");
    String clientId = String("mona-") + DEVICE_ID;

    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      client.subscribe(TOPIC_CMD_DEVICE.c_str());
      client.subscribe(TOPIC_CMD_ALL);
      sendEvent("CONNECTED");
      sendState();
      pixels.clear(); pixels.show();
    } else {
      Serial.print("failed rc="); Serial.print(client.state());
      Serial.println(" retry in 5s");
      delay(5000);
    }
  }
}

// ====================== SETUP / LOOP ======================
void setup() {
  Serial.begin(115200);
  delay(50);

  pixels.begin();
  pixels.clear();
  pixels.setBrightness(brightness);
  pixels.show();

  setup_wifi();

  client.setServer(MQTT_SERVER, MQTT_PORT);
  client.setCallback(callback);

  pinMode(BUTTON_PIN, INPUT_PULLUP);
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();

  unsigned long now = millis();

  // ---- button debounce ----
  bool pressed = (digitalRead(BUTTON_PIN) == LOW);
  if (pressed && !buttonLatched && (now - lastPressMs >= DEBOUNCE_MS)) {
    buttonLatched = true;
    lastPressMs   = now;
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
      applyFlashFrame(false);
      sendState();
    }
  }

  // ---- heartbeat ----
  if (now - lastHeartbeatMs >= HEARTBEAT_MS) {
    lastHeartbeatMs = now;
    sendState();
  }
}
