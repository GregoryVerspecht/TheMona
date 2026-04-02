# Button — Hardware & Protocol Documentatie

Elke knop is een **ESP8266** met 7 **NeoPixel** LEDs en één drukknop. Ze communiceren via **MQTT** over het lokale WiFi-netwerk (SSID: `The-Mona`).

---

## Hardware

| Component | Pin | Details |
|-----------|-----|---------|
| NeoPixel ring | D4 | 7 LEDs, NEO_GRB + NEO_KHZ800 |
| Drukknop | D1 | NO (Normally Open), INPUT_PULLUP — knop verbindt D1 met GND |

- **Debounce**: 80ms
- **Brightness**: 0–255 (default 255), via NeoPixel `setBrightness()`
- **Flash**: niet-blokkerend via state machine in `loop()`

---

## WiFi & MQTT

| Instelling | Waarde |
|------------|--------|
| SSID | `The-Mona` |
| Password | `mona1234` |
| MQTT broker | `192.168.69.69:1883` |
| Client ID | `mona-{DEVICE_ID}` (bv. `mona-01`) |

---

## MQTT Topics

Elke knop heeft een uniek `DEVICE_ID` (bv. `01`–`06`).

| Topic | Richting | Beschrijving |
|-------|----------|--------------|
| `mona/buttons/{id}/cmd` | Pi → Knop | Commando's naar één knop |
| `mona/buttons/all/cmd` | Pi → Alle | Broadcast naar alle knoppen tegelijk |
| `mona/buttons/{id}/event` | Knop → Pi | Knopgebeurtenissen (PRESSED, CONNECTED) |
| `mona/buttons/{id}/state` | Knop → Pi | Huidige status van de knop |

---

## Inkomende commando's (Pi → Knop)

Alle payloads zijn JSON. Optioneel `brightness` veld (0–255) werkt bij elk commando.

### `fill` — Alle LEDs zelfde kleur
```json
{
  "type": "fill",
  "r": 0, "g": 255, "b": 0,
  "brightness": 200
}
```
Stopt een eventuele flash. Zet alle 7 LEDs op de opgegeven kleur.

---

### `flash` — Knipperen (non-blocking)
```json
{
  "type": "flash",
  "r": 255, "g": 0, "b": 0,
  "interval_ms": 120,
  "times": 6,
  "brightness": 200,
  "mask": [0, 1, 2]
}
```
| Veld | Default | Bereik | Beschrijving |
|------|---------|--------|--------------|
| `r/g/b` | 255/255/255 | 0–255 | Kleur tijdens flash |
| `interval_ms` | 120 | 20–5000 | Tijd per toggle (ms) |
| `times` | 6 | 1–100 | Aantal keer knipperen |
| `mask` | _(alle LEDs)_ | array van 0–6 | Welke LEDs knipperen |

Flash werkt niet-blokkerend via een state machine. Na afloop gaan de betrokken LEDs uit.

---

### `leds_set` — Individuele LEDs instellen
```json
{
  "type": "leds_set",
  "brightness": 150,
  "leds": [
    {"i": 0, "r": 255, "g": 0, "b": 0},
    {"i": 3, "r": 0, "g": 0, "b": 255}
  ]
}
```
Stel tot 7 individuele LEDs in (index 0–6). Stopt flash.

---

### `led_set` — Één LED instellen
```json
{
  "type": "led_set",
  "i": 2,
  "r": 0, "g": 255, "b": 0
}
```

---

### `stop` — Stop flash / LEDs uitzetten
```json
{
  "type": "stop",
  "clear": true
}
```
`clear: true` zet alle LEDs uit. `clear: false` pauzeert de flash maar laat de laatste staat staan.

---

### `request_state` — Status opvragen
```json
{ "type": "request_state" }
```
Knop antwoordt met een state-bericht op `mona/buttons/{id}/state`.

---

## Uitgaande berichten (Knop → Pi)

### Event (op `mona/buttons/{id}/event`)
```json
{
  "id": "01",
  "event": "PRESSED",
  "ip": "192.168.69.x"
}
```
| Event | Wanneer |
|-------|---------|
| `CONNECTED` | Bij (her)verbinding met MQTT |
| `PRESSED` | Knop ingedrukt (na debounce van 80ms) |

---

### State (op `mona/buttons/{id}/state`)
```json
{
  "id": "01",
  "brightness": 200,
  "flashing": false,
  "flash_interval_ms": 120,
  "rssi": -62,
  "mixer": "neopixel"
}
```
State wordt gestuurd na elk commando en na `request_state`.

---

## ButtonRegistry (Pi-kant)

De Pi houdt een live registry bij van alle knoppen in memory (`ButtonRegistry`). Velden per knop:

| Veld | Type | Beschrijving |
|------|------|--------------|
| `id` | str | Device ID (bv. `01`) |
| `connected` | bool | Ooit CONNECTED event ontvangen |
| `last_seen` | datetime | Laatste MQTT-bericht |
| `last_event` | str | Laatste event (`PRESSED`, `CONNECTED`, ...) |
| `last_press` | datetime | Tijdstip laatste druk |
| `brightness` | int | Huidige helderheid (uit state) |
| `flashing` | bool | Momenteel aan het flashen |
| `flash_interval_ms` | int | Flash interval (ms) |
| `rssi` | int | WiFi signaalsterkte (dBm) |
| `ip` | str | IP-adres van de knop |

---

## API Endpoints (Pi)

| Method | URL | Beschrijving |
|--------|-----|--------------|
| GET | `/api/v1/buttons` | Alle knoppen uit de registry |
| GET | `/api/v1/buttons/{id}` | Één knop |
| POST | `/api/v1/buttons/{id}/fill` | Fill kleur sturen |
| POST | `/api/v1/buttons/{id}/flash` | Flash sturen |
| POST | `/api/v1/buttons/{id}/leds` | Individuele LEDs instellen |
| POST | `/api/v1/buttons/{id}/stop` | Stop flash / clear |
| POST | `/api/v1/buttons/{id}/request-state` | State opvragen |
| POST | `/api/v1/buttons/all/fill` | Fill naar alle knoppen |
| POST | `/api/v1/buttons/all/flash` | Flash naar alle knoppen |
| POST | `/api/v1/buttons/all/stop` | Stop alle knoppen |

---

## Device IDs

| Bestand | DEVICE_ID |
|---------|-----------|
| Button_1_V3.ino | `01` |
| Button_2_V3.ino | `02` |
| Button_3_V3.ino | `03` |
| Button_4_V3.ino | `04` |
| Button_5_V3.ino | `05` |
| Button_6_V3.ino | `06` |

---

## Verbindingsstroom

```
Boot → WiFi verbinden → MQTT verbinden
     → subscribe mona/buttons/{id}/cmd
     → subscribe mona/buttons/all/cmd
     → publish CONNECTED event
     → publish huidige state
     → loop: button polling + flash state machine + MQTT loop
```

Bij MQTT-disconnect: automatisch herverbinden (blocking, 5s retry).

---

## Opmerkingen

- **Geen batterijmeting** in huidige firmware — `battery` veld is niet aanwezig in state. Het `rssi` veld geeft wel een indicatie van WiFi-bereik.
- **Flash eindigt altijd uit** — na afloop van flash gaan de betrokken LEDs altijd uit, ook als er voor de flash een kleur stond.
- **Brightness persistent per sessie** — brightness wordt bijgehouden in memory maar reset bij reboot van de knop.
- **MQTT_MAX_PACKET_SIZE 512** — JSON payloads mogen max ~500 bytes zijn. Bij grote `leds_set` arrays (7 leds) zit je al snel aan de limiet.
