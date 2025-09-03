from flask import Flask, jsonify, request
import paho.mqtt.client as mqtt
import json
import time
import threading

# ==== (Optioneel) Sound ====
# Vereist: pygame (pip install pygame)
SOUND_FILE = "/home/mona/the-mona/static/assets/sounds/lizard-button.mp3"
SOUND_ENABLED = True

try:
    import pygame
    pygame.mixer.init()
    _sound_obj = pygame.mixer.Sound(SOUND_FILE)
    _sound_ready = True
    print(f"🔊 Sound geladen: {SOUND_FILE}")
except Exception as e:
    _sound_obj = None
    _sound_ready = False
    if SOUND_ENABLED:
        print(f"⚠️ Sound uitgeschakeld (kon niet initialiseren/laden): {e}")

def play_click_sound():
    """Speel 1 sound asynchroon af (niet-blokkerend)."""
    if SOUND_ENABLED and _sound_ready and _sound_obj is not None:
        try:
            _sound_obj.play()
        except Exception as e:
            print(f"⚠️ Kon sound niet afspelen: {e}")

# =========================
# Flask App Setup
# =========================
app = Flask(__name__)

# =========================
# MQTT Configuratie
# =========================
MQTT_BROKER = "192.168.69.69"
MQTT_TOPIC_RGB = "neopixel/set"
MQTT_TOPIC_BUTTONS = "esp/status"

mqtt_client = mqtt.Client()

# =========================
# ESP's en Modes
# =========================
ESP_IDS = [1, 2, 3, 4, 5, 6]  # De ESP's die we willen aansturen

MODES = {
    "static_red":   (255, 0,   0),
    "static_green": (0,   255, 0),
    "static_blue":  (0,   0,   255),
}

IDLE_MODE = "static_blue"  # In rust blijft alles blauw

# =========================
# Knipper-instellingen
# =========================
FLASH_PERIOD = 0.2          # 0.5s aan, 0.5s uit
FLASH_DURATION = 0.5        # 5 seconden per klik

# Thread-safe state voor knipperen
_flash_lock = threading.Lock()
_flash_thread = None
_flash_end_at = 0.0         # epoch-tijd tot wanneer we blijven knipperen
_flash_anchor_id = None     # ESP-ID die statisch groen blijft tijdens knipperen

# =========================
# LED Hulpfuncties
# =========================
def set_rgb_color(esp_id, r, g, b, brightness=100):
    command = {
        "id": esp_id,
        "led": "ON" if (r or g or b) else "OFF",
        "r": r,
        "g": g,
        "b": b,
        "brightness": brightness,
    }
    mqtt_client.publish(MQTT_TOPIC_RGB, json.dumps(command))
    print(f"📡 LED naar ESP {esp_id}: R:{r} G:{g} B:{b} (brightness {brightness})")

def set_rgb_mode(mode):
    """Statische mode instellen voor ALLE ESP's (idle/blauw e.d.)."""
    if mode not in MODES:
        print(f"❌ Onbekende mode: {mode}")
        return
    r, g, b = MODES[mode]
    for esp_id in ESP_IDS:
        set_rgb_color(esp_id, r, g, b)
    print(f"✅ Mode ingesteld: {mode} (R:{r}, G:{g}, B:{b})")

def _set_all_off():
    for esp_id in ESP_IDS:
        set_rgb_color(esp_id, 0, 0, 0)

def _set_all_idle():
    r, g, b = MODES[IDLE_MODE]
    for esp_id in ESP_IDS:
        set_rgb_color(esp_id, r, g, b)

def _set_anchor_green(anchor_id):
    """Zet enkel de anchor (indrukker) statisch groen."""
    if anchor_id in ESP_IDS:
        set_rgb_color(anchor_id, 0, 255, 0)

def _set_non_anchor(anchor_id, r, g, b):
    """Zet alle niet-anchor ESP's op (r,g,b)."""
    for esp_id in ESP_IDS:
        if esp_id != anchor_id:
            set_rgb_color(esp_id, r, g, b)

# =========================
# Flasher (groen knipperen; anchor blijft statisch groen)
# =========================
def _flasher_loop():
    """Draait zolang _flash_end_at in de toekomst ligt; knippert ALLE niet-anchor ESP's groen.
    Anchor blijft statisch groen. Daarna alles terug naar idle (blauw)."""
    global _flash_end_at, _flash_thread, _flash_anchor_id
    on = True
    print(f"🚀 Groene knipper-thread gestart. Anchor = ESP #{_flash_anchor_id}")

    try:
        while True:
            with _flash_lock:
                remaining = _flash_end_at - time.time()
                anchor_id = _flash_anchor_id  # snapshot binnen lock
                if remaining <= 0:
                    break

            if on:
                # Aan: anchor GREEN + anderen GREEN
                _set_anchor_green(anchor_id)
                _set_non_anchor(anchor_id, 0, 255, 0)
            else:
                # Uit: anchor blijft GREEN + anderen UIT
                _set_anchor_green(anchor_id)
                _set_non_anchor(anchor_id, 0, 0, 0)

            on = not on
            time.sleep(FLASH_PERIOD)
    finally:
        # Klaar met knipperen → terug naar idle (blauw) voor iedereen
        _set_all_idle()
        print("✅ Groene knippermodus afgelopen → alles terug naar blauw.")
        with _flash_lock:
            _flash_thread = None  # Markeer thread als gestopt

def start_green_flash_with_anchor(anchor_id):
    """Start of verleng het groene knipperen waarbij 'anchor_id' statisch groen blijft."""
    global _flash_thread, _flash_end_at, _flash_anchor_id

    with _flash_lock:
        if anchor_id in ESP_IDS:
            _flash_anchor_id = anchor_id
        else:
            print(f"⚠️ Anchor-ID {anchor_id} is ongeldig; gebruik laatste geldige anchor: {_flash_anchor_id}")

        # Verleng timer
        _flash_end_at = time.time() + FLASH_DURATION

        # Start flasher indien nodig
        if _flash_thread is None or not _flash_thread.is_alive():
            _flash_thread = threading.Thread(target=_flasher_loop, daemon=True)
            _flash_thread.start()
            print(f"🟢 Knipperen GROEN gestart (anchor ESP #{_flash_anchor_id}).")
        else:
            print(f"🔁 Knipperen GROEN verlengd; anchor nu ESP #{_flash_anchor_id}.")

# =========================
# MQTT Callback & Setup
# =========================
def on_message(client, userdata, message):
    payload = message.payload.decode("utf-8", errors="replace")
    print(f"📩 MQTT Bericht ontvangen: {payload}")
    try:
        data = json.loads(payload)
        if data.get("event") == "PRESSED":
            esp_id = data.get("id")
            # Sound meteen bij elke druk
            play_click_sound()
            # LED-gedrag
            start_green_flash_with_anchor(esp_id)
    except json.JSONDecodeError:
        print("❌ Ongeldig JSON-formaat ontvangen!")

def setup_mqtt():
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_BROKER, 1883, 60)
    mqtt_client.subscribe(MQTT_TOPIC_BUTTONS)
    mqtt_client.loop_start()
    print(f"✅ Verbonden met MQTT broker {MQTT_BROKER}, luisteren op '{MQTT_TOPIC_BUTTONS}'.")

# =========================
# Flask Endpoints
# =========================
@app.route("/")
def index():
    return jsonify({"status": "success", "message": "Idle = blauw. Bij knop: anchor groen (statisch), rest knippert groen + sound."})

@app.route("/reset", methods=["POST"])
def reset_color():
    """Reset alle LEDs naar idle (blauw)."""
    set_rgb_mode(IDLE_MODE)
    return jsonify({"status": "success", "message": "LEDs terug op blauw gezet"})

@app.route("/set_color", methods=["POST"])
def set_color():
    """Handmatig een kleur instellen via een POST request voor 1 ESP."""
    data = request.json or {}
    esp_id = data.get("id")
    r = int(data.get("r", 0))
    g = int(data.get("g", 0))
    b = int(data.get("b", 0))
    brightness = int(data.get("brightness", 100))

    if esp_id in ESP_IDS:
        set_rgb_color(esp_id, r, g, b, brightness)
        return jsonify({"status": "success", "message": f"LEDs ingesteld op R:{r} G:{g} B:{b} voor ESP {esp_id}"})
    else:
        return jsonify({"status": "error", "message": "Ongeldige of ontbrekende ESP ID"}), 400

# =========================
# Main
# =========================
if __name__ == "__main__":
    setup_mqtt()
    print("🚀 MQTT gestart, zet alle LEDs op blauw (idle).")
    set_rgb_mode(IDLE_MODE)  # Idle state = blauw
    app.run(host="0.0.0.0", port=8443)
