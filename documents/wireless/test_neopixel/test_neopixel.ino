#include <Adafruit_NeoPixel.h>

#define PIN D4         // GPIO waarop Neopixels zijn aangesloten
#define NUMPIXELS 7    // Aantal LEDs op de ring

Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

void setup() {
  pixels.begin();
  pixels.clear();
  pixels.show();
}

void loop() {
  for (int i = 0; i < NUMPIXELS; i++) {
    pixels.setPixelColor(i, pixels.Color(255, 0, 0)); // Rood
    pixels.show();
    delay(500);  // Wacht 500ms
    pixels.setPixelColor(i, pixels.Color(0, 0, 0)); // LED uit
  }

  for (int i = 0; i < NUMPIXELS; i++) {
    pixels.setPixelColor(i, pixels.Color(0, 255, 0)); // Groen
    pixels.show();
    delay(500);
    pixels.setPixelColor(i, pixels.Color(0, 0, 0));
  }

  for (int i = 0; i < NUMPIXELS; i++) {
    pixels.setPixelColor(i, pixels.Color(0, 0, 255)); // Blauw
    pixels.show();
    delay(500);
    pixels.setPixelColor(i, pixels.Color(0, 0, 0));
  }
}
