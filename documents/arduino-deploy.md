# Arduino ESP8266 — Deploy werkwijze

## Bestandsstructuur

```
arduino/
├── button_logic.h          ← alle logica (NOOIT aanpassen tenzij logica wijzigt)
├── Button_1_V3/
│   ├── Button_1_V3.ino     ← altijd 2 regels, nooit aanpassen
│   └── config.h            ← enige unieke file per knop
├── Button_2_V3/
│   ├── Button_2_V3.ino
│   └── config.h
└── ...
```

---

## Eerste keer instellen (eenmalig per PC)

### 1. Arduino IDE installeren
Download van https://www.arduino.cc/en/software

### 2. ESP8266 board support toevoegen
`File → Preferences → Additional Boards Manager URLs`:
```
http://arduino.esp8266.com/stable/package_esp8266com_index.json
```
Dan: `Tools → Board → Boards Manager → zoek "esp8266" → Install`

### 3. Libraries installeren
`Tools → Manage Libraries` → zoek en installeer:
| Library | Versie |
|---------|--------|
| PubSubClient | laatste |
| Adafruit NeoPixel | laatste |
| ArduinoJson | **6.x** (niet 7!) |

---

## Nieuwe knop flashen (eerste keer)

1. Open `Button_X_V3/config.h` en stel in:
   - `DEVICE_ID` — uniek per knop (`"01"` t/m `"06"`)
   - `WIFI_SSID` / `WIFI_PASSWORD` — netwerknaam en wachtwoord
   - `MQTT_SERVER` — IP van de Pi (`192.168.69.69` via hotspot, `192.168.1.12` via thuis-wifi)
   - `BATTERY_ENABLED` — `false` tenzij spanningsdeler aangesloten

2. Open `Button_X_V3/Button_X_V3.ino` in Arduino IDE  
   → IDE toont automatisch 2 tabbladen: `.ino` en `config`

3. Sluit ESP8266 aan via USB

4. Stel board in:
   - `Tools → Board → ESP8266 → NodeMCU 1.0 (ESP-12E Module)`
   - `Tools → Port → COMx` (de juiste poort)

5. Klik **Upload** (→ pijl)

6. Open `Tools → Serial Monitor` (115200 baud) om te controleren:
   ```
   Connecting to WiFi: The-Mona
   WiFi connected. IP: 192.168.69.x
   Connecting MQTT... connected
   ```
   LEDs: geel tijdens WiFi → groen knippert bij verbonden → blauw tijdens MQTT → uit bij klaar

---

## Logica updaten (alle knoppen tegelijk)

Als je `button_logic.h` aanpast moet je hem eerst naar alle mappen kopiëren, dan alle knoppen flashen:

**Stap 1 — kopieer naar alle mappen** (vanuit Git Bash in de `arduino/` map):
```bash
for i in 1 2 3 4 5 6; do
  cp button_logic.h Button_${i}_V3/button_logic.h
done
```

**Stap 2 — flash alle knoppen:**
1. Open `Button_X_V3/Button_X_V3.ino`
2. Sluit knop aan via USB
3. Klik Upload
4. Herhaal voor alle 6

> **Tip:** je kan meerdere Arduino IDE vensters openhouden, één per knop. Sluit ze één voor één aan en klik Upload.

---

## Alleen één knop updaten

Bv. `config.h` van knop 3 aanpassen (ander netwerk, battery aan):

1. Pas `Button_3_V3/config.h` aan
2. Open `Button_3_V3/Button_3_V3.ino`
3. Sluit knop 3 aan, klik Upload

Andere knoppen hoeven niet opnieuw geflasht te worden.

---

## Troubleshooting

| Symptoom | Oorzaak | Oplossing |
|----------|---------|-----------|
| LEDs blijven geel | WiFi niet gevonden | Check `WIFI_SSID` in config.h, Pi hotspot aan? |
| LEDs blijven blauw | MQTT niet bereikbaar | Check `MQTT_SERVER` IP, Pi aan? |
| Upload mislukt | Verkeerde poort of board | Check `Tools → Port` en `Tools → Board` |
| `JSON parse failed` in Serial Monitor | Payload te groot | `MQTT_MAX_PACKET_SIZE` verhogen in button_logic.h |
| Knop verschijnt niet in frontend | Nooit CONNECTED event gestuurd | Herstart knop, check Serial Monitor |
| Knop staat als offline na een tijdje | Heartbeat werkt niet | Zorg dat MQTT verbonden blijft, check WiFi stabiliteit |

---

## Visuele status LEDs bij opstart

| Kleur | Betekenis |
|-------|-----------|
| Geel | WiFi verbinding bezig |
| Groen knippert (2x) | WiFi verbonden |
| Blauw | MQTT verbinding bezig |
| Uit | Klaar, wacht op commando's |
