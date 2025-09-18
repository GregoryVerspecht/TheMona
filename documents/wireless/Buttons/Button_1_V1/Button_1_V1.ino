#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <Adafruit_NeoPixel.h>
#include <ArduinoJson.h>

// ====== CONFIG ======
const char* WIFI_SSID = "The-Mona";
const char* WIFI_PASS = "mona1234";
const char* MQTT_HOST = "192.168.69.69";
const uint16_t MQTT_PORT = 1883;

#define PIN D4
#define NUMPIXELS 7
#define BUTTON D1                // knop naar GND, intern pull-up
#define HEARTBEAT_MS 15000
#define DEBOUNCE_MS 80

// ====== GLOBALS ======
WiFiClient espClient;
PubSubClient mqtt(espClient);
Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

char deviceId[16];               // bijv "btn1" of chipid
char tp_status[64];
char tp_hb[64];
char tp_events[64];
char tp_cmd_rgb[64];
char tp_cmd_flash[64];
char tp_cmd_rgb_all[64];

unsigned long lastHeartbeat = 0;
unsigned long lastButtonChange = 0;
bool lastButtonState = HIGH;     // pull-up: HIGH = niet ingedrukt
int brightness = 255;

// ====== HELPERS ======
String colorToHex(uint8_t r, uint8_t g, uint8_t b) {
  char buf[8];
  snprintf(buf, sizeof(buf), "#%02X%02X%02X", r, g, b);
  return String(buf);
}

void neopixelSetAll(uint8_t r, uint8_t g, uint8_t b, int bright=-1) {
  if (bright >= 0) { brightness = constrain(bright, 0, 255); pixels.setBrightness(brightness); }
  for (int i=0;i<NUMPIXELS;i++) pixels.setPixelColor(i, pixels.Color(r,g,b));
  pixels.show();
}

void neopixelClear() {
  pixels.clear(); pixels.show();
}

// ====== MQTT PUBLISHES ======
void pub_json(const char* topic, const JsonDocument& doc, bool retain=false, int qos=1) {
  char buf[256];
  size_t n = serializeJson(doc, buf, sizeof(buf));
  mqtt.publish(topic, buf, retain);
}

void publish_status(bool online) {
  StaticJsonDocument<256> doc;
  doc["online"] = online;
  doc["fw"] = "1.0.0";
  JsonArray caps = doc.createNestedArray("capabilities");
  caps.add("rgb");
  caps.add("press");
  doc["mac"] = WiFi.macAddress();
  pub_json(tp_status, doc, /*retain=*/true);
}

void publish_heartbeat() {
  StaticJsonDocument<64> doc;
  doc["ts"] = (long) (millis()/1000);
  pub_json(tp_hb, doc, false, 0);
}

void publish_press_event() {
  StaticJsonDocument<128> doc;
  doc["type"] = "press";
  doc["ts"] = (long) (millis()/1000);
  pub_json(tp_events, doc, false, 1);
}

// ====== MQTT CALLBACK ======
void handle_cmd_rgb(const JsonDocument& doc) {
  const char* hex = doc["color"] | "#FFFFFF";
  String s(hex);
  // parse #RRGGBB
  uint8_t r=255,g=255,b=255;
  if (s.length()==7 && s[0]=='#') {
    r = strtoul(s.substring(1,3).c_str(), NULL, 16);
    g = strtoul(s.substring(3,5).c_str(), NULL, 16);
    b = strtoul(s.substring(5,7).c_str(), NULL, 16);
  }
  const char* mode = doc["mode"] | "solid";
  int duration = doc["duration_ms"] | 500;

  if (strcmp(mode,"solid")==0) {
    neopixelSetAll(r,g,b);
    if (duration>0) { delay(duration); neopixelClear(); }
  } else if (strcmp(mode,"pulse")==0) {
    // eenvoudige pulse: aan/uit 2x
    for (int i=0;i<2;i++){ neopixelSetAll(r,g,b); delay(duration/2); neopixelClear(); delay(duration/2); }
  } else {
    neopixelSetAll(r,g,b);
  }
}

void handle_cmd_flash(const JsonDocument& doc) {
  const char* hex = doc["color"] | "#FF0000";
  String s(hex);
  uint8_t r=255,g=0,b=0;
  if (s.length()==7 && s[0]=='#') {
    r = strtoul(s.substring(1,3).c_str(), NULL, 16);
    g = strtoul(s.substring(3,5).c_str(), NULL, 16);
    b = strtoul(s.substring(5,7).c_str(), NULL, 16);
  }
  int times = doc["times"] | 3;
  int period = doc["period_ms"] | 200;

  for (int i=0;i<times;i++){
    neopixelSetAll(r,g,b);
    delay(period/2);
    neopixelClear();
    delay(period/2);
  }
}

void mqtt_callback(char* topic, byte* payload, unsigned int len) {
  // broadcast all?
  bool isAll = (strcmp(topic, tp_cmd_rgb_all) == 0);

  // parse json
  StaticJsonDocument<256> doc;
  DeserializationError err = deserializeJson(doc, payload, len);
  if (err) { Serial.println(F("JSON parse error")); return; }

  // process
  if (strcmp(topic, tp_cmd_rgb) == 0 || isAll) {
    handle_cmd_rgb(doc);
  } else if (strcmp(topic, tp_cmd_flash) == 0) {
    handle_cmd_flash(doc);
  }
}

// ====== WIFI/MQTT CONNECT ======
void wifi_connect() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print(F("WiFi verbinden"));
  while (WiFi.status() != WL_CONNECTED) { delay(300); Serial.print("."); }
  Serial.print(F("\nWiFi OK, IP=")); Serial.println(WiFi.localIP());
}

void mqtt_connect() {
  // LWT: markeer offline op status retained
  StaticJsonDocument<64> lwt;
  lwt["online"] = false;
  char willPayload[64];
  serializeJson(lwt, willPayload, sizeof(willPayload));

  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setCallback(mqtt_callback);
  while (!mqtt.connected()) {
    Serial.print(F("MQTT verbinden... "));
    // client id uniek maken
    char cid[24]; snprintf(cid, sizeof(cid), "btn-%s", deviceId);
    if (mqtt.connect(cid, nullptr, nullptr, tp_status, /*qos*/1, /*retain*/true, willPayload)) {
      Serial.println(F("OK"));
      mqtt.subscribe(tp_cmd_rgb, 1);
      mqtt.subscribe(tp_cmd_flash, 1);
      mqtt.subscribe(tp_cmd_rgb_all, 1);
      publish_status(true); // online=true retained
    } else {
      Serial.print(F("fail rc=")); Serial.println(mqtt.state());
      delay(2000);
    }
  }
}

// ====== SETUP/LOOP ======
void setup() {
  Serial.begin(115200);

  // device id opbouwen (gebruik chip id of ESP_NUMBER)
  uint32_t chip = ESP.getChipId();
  snprintf(deviceId, sizeof(deviceId), "btn%u", (unsigned)(chip & 0xFF)); // kort id; pas aan naar wens

  // topics maken
  snprintf(tp_status, sizeof(tp_status),   "the-mona/buttons/%s/status",    deviceId);
  snprintf(tp_hb, sizeof(tp_hb),           "the-mona/buttons/%s/heartbeat", deviceId);
  snprintf(tp_events, sizeof(tp_events),   "the-mona/buttons/%s/events",    deviceId);
  snprintf(tp_cmd_rgb, sizeof(tp_cmd_rgb), "the-mona/buttons/%s/cmd/rgb",   deviceId);
  snprintf(tp_cmd_flash,sizeof(tp_cmd_flash),"the-mona/buttons/%s/cmd/flash",deviceId);
  snprintf(tp_cmd_rgb_all,sizeof(tp_cmd_rgb_all),"the-mona/buttons/all/cmd/rgb");

  pixels.begin();
  pixels.clear();
  pixels.setBrightness(brightness);

  pinMode(BUTTON, INPUT_PULLUP);

  wifi_connect();
  mqtt_connect();
  neopixelSetAll(0, 16, 0, 50); // klein groen tikje bij start
  delay(150);
  neopixelClear();
}

void loop() {
  if (!mqtt.connected()) mqtt_connect();
  mqtt.loop();

  // heartbeat
  unsigned long now = millis();
  if (now - lastHeartbeat >= HEARTBEAT_MS) {
    lastHeartbeat = now;
    publish_heartbeat();
  }

  // debounced button
  bool cur = digitalRead(BUTTON);
  if (cur != lastButtonState) {
    lastButtonChange = now;
    lastButtonState = cur;
  }
  if ((now - lastButtonChange) > DEBOUNCE_MS) {
    // LOW = pressed
    static bool prevPressed = false;
    bool pressed = (cur == LOW);
    if (pressed && !prevPressed) {
      publish_press_event();
    }
    prevPressed = pressed;
  }
}
