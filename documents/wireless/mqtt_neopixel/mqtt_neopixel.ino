#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <Adafruit_NeoPixel.h>
#include <ArduinoJson.h>

// **Wi-Fi instellingen**
const char* ssid = "The-Mona";     
const char* password = "mona1234";

// **MQTT Broker instellingen**
const char* mqtt_server = "192.168.69.69";

WiFiClient espClient;
PubSubClient client(espClient);

// **Neopixel Instellingen**
#define PIN D4         
#define NUMPIXELS 7    

Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

int brightness = 255; // Standaard maximale helderheid (0-255)

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
  
  char message[length + 1];
  strncpy(message, (char*)payload, length);
  message[length] = '\0';
  
  Serial.println(message);

  // **JSON-parsing**
  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, message);
  if (error) {
    Serial.println("JSON parsing mislukt!");
    return;
  }

  // **Controleer of een helderheid is meegegeven**
  if (doc.containsKey("brightness")) {
    brightness = doc["brightness"];
    brightness = constrain(brightness, 0, 255); // Limiteer binnen 0-255
    pixels.setBrightness(brightness);
    Serial.print("Helderheid ingesteld op: ");
    Serial.println(brightness);
  }

  // **Controleer of alle LEDs dezelfde kleur moeten krijgen**
  if (doc.containsKey("all") && doc["all"] == true) {
    int r = doc["r"];
    int g = doc["g"];
    int b = doc["b"];
    
    Serial.println("Alle LEDs instellen op één kleur...");
    pixels.fill(pixels.Color(r, g, b));
    pixels.show();
    
    // **Stuur bevestiging terug naar MQTT**
    StaticJsonDocument<128> response;
    response["all"] = true;
    response["r"] = r;
    response["g"] = g;
    response["b"] = b;
    response["brightness"] = brightness;
    response["status"] = "OK"; 
    
    char buffer[128];
    serializeJson(response, buffer);
    client.publish("neopixel/status", buffer);
    
    return; // Stop hier, want "all" heeft prioriteit
  }

  // **Als "all" niet is ontvangen, pas dan slechts één LED aan**
  int led = doc["led"];
  int r = doc["r"];
  int g = doc["g"];
  int b = doc["b"];

  if (led < 0 || led >= NUMPIXELS) {
    Serial.println("⚠️ Ongeldige LED index!");
    return;
  }

  // **Stel de individuele LED in**
  pixels.setPixelColor(led, pixels.Color(r, g, b));
  pixels.show();

  // **Stuur bevestiging terug naar MQTT**
  StaticJsonDocument<128> response;
  response["led"] = led;
  response["r"] = r;
  response["g"] = g;
  response["b"] = b;
  response["brightness"] = brightness;
  response["status"] = "OK"; 
  
  char buffer[128];
  serializeJson(response, buffer);
  client.publish("neopixel/status", buffer);

  Serial.println("✅ LED-update bevestigd via MQTT!");
}


// **Herstel MQTT verbinding indien verbroken**
void reconnect() {
  while (!client.connected()) {
    Serial.print("Verbinden met MQTT...");
    if (client.connect("WemosD1Mini")) {
      Serial.println("Verbonden!");
      client.subscribe("neopixel/set"); // Luisteren naar het juiste topic
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
  
  pixels.begin(); 
  pixels.clear(); 

  // **Stel standaard kleur en helderheid in**
  pixels.setBrightness(brightness); 
  for (int i = 0; i < NUMPIXELS; i++) {
    pixels.setPixelColor(i, pixels.Color(255, 0, 0)); // Rood
  }
  pixels.show();
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}
