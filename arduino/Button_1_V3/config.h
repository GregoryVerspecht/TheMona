#pragma once

// ====================== DEVICE ======================
#define DEVICE_ID "01"

// ====================== WIFI ======================
#define WIFI_SSID     "The-Mona"
#define WIFI_PASSWORD "mona1234"

// ====================== MQTT ======================
#define MQTT_SERVER "192.168.69.69"
#define MQTT_PORT   1883

// ====================== HARDWARE ======================
#define LED_PIN    D4   // NeoPixel data pin
#define NUMPIXELS  7    // Aantal NeoPixels
#define BUTTON_PIN D1   // Drukknop (NO, INPUT_PULLUP — verbindt met GND)

// ====================== BATTERY ======================
// Spanningsdeler schema:  Batterij+ --- 330kΩ --- A0 --- 100kΩ --- GND
// Zet op false als geen spanningsdeler aangesloten is.
#define BATTERY_ENABLED  false
#define BATTERY_VREF     1.0      // Max spanning op A0 (1.0V bare ESP, 3.3V NodeMCU)
#define BATTERY_DIVIDER  0.2326   // R2/(R1+R2): 100k/(330k+100k) = 0.2326
#define BATTERY_V_FULL   4.2      // LiPo volledig
#define BATTERY_V_EMPTY  3.0      // LiPo leeg
