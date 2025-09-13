from flask import Flask, jsonify, request
import paho.mqtt.client as mqtt
import json
import time
import threading  # ✅ Gebruik threading om knipperen asynchroon te maken

# Flask App Setup
app = Flask(__name__)

# MQTT Configuratie
MQTT_BROKER = "192.168.69.69"
MQTT_TOPIC_RGB = "neopixel/set"
MQTT_TOPIC_BUTTONS = "esp/status"

mqtt_client = mqtt.Client()

# **ESP ID's**
ESP_IDS = [1, 2, 3, 4, 5, 6]  # 🚀 De ESP's die we willen aansturen

# **Modes voor ALLE ESPs**
MODES = {
    "static_red": (255, 0, 0),
    "static_green": (0, 255, 0),
    "static_blue": (0, 0, 255),
    "flash_red": (255, 0, 0),
    "flash_green": (0, 255, 0),
    "flash_blue": (0, 0, 255)
}

# **Threading fix: Zorgt ervoor dat er niet meerdere flash-loops tegelijk draaien**
flash_active = False

# **MQTT Callback: Luistert naar knoppen**
def on_message(client, userdata, message):
    payload = message.payload.decode("utf-8")
    print(f"📩 MQTT Bericht ontvangen: {payload}")

    try:
        data = json.loads(payload)

        if "event" in data and data["event"] == "PRESSED":
            esp_id = data.get("id", "Unknown")

            # **ESP 1-3 → Statische mode (Rood, Groen, Blauw)**
            if esp_id == 1:
                print("🚀 Mode: Alle ESPs worden ROOD")
                set_rgb_mode("static_red")
            elif esp_id == 2:
                print("🚀 Mode: Alle ESPs worden GROEN")
                set_rgb_mode("static_green")
            elif esp_id == 3:
                print("🚀 Mode: Alle ESPs worden BLAUW")
                set_rgb_mode("static_blue")

            # **ESP 4-6 → Knipper mode (Rood, Groen, Blauw)**
            elif esp_id == 4:
                print("🚀 Mode: Alle ESPs knipperen ROOD")
                start_flashing("flash_red")
            elif esp_id == 5:
                print("🚀 Mode: Alle ESPs knipperen GROEN")
                start_flashing("flash_green")
            elif esp_id == 6:
                print("🚀 Mode: Alle ESPs knipperen BLAUW")
                start_flashing("flash_blue")

    except json.JSONDecodeError:
        print("❌ Ongeldig JSON-formaat ontvangen!")

# **Setup MQTT-client**
def setup_mqtt():
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_BROKER, 1883, 60)
    mqtt_client.subscribe(MQTT_TOPIC_BUTTONS)
    mqtt_client.loop_start()

# **Mode instellen voor ALLE ESPs**
def set_rgb_mode(mode):
    global flash_active
    flash_active = False  # 🚨 Stop knipperen als een statische mode wordt gekozen
    if mode in MODES:
        r, g, b = MODES[mode]
        for esp_id in ESP_IDS:
            set_rgb_color(esp_id, r, g, b)
        print(f"✅ Mode ingesteld: {mode} (R:{r}, G:{g}, B:{b})")

# **Asynchroon starten van de knippermodus**
def start_flashing(mode):
    global flash_active
    if flash_active:
        return  # ✅ Voorkom dubbele knipper-processen

    flash_active = True
    thread = threading.Thread(target=flash_rgb_mode, args=(mode,))
    thread.start()

# **Knipper-modus voor ALLE ESPs (5 seconden)**
def flash_rgb_mode(mode):
    global flash_active
    if mode in MODES:
        r, g, b = MODES[mode]
        start_time = time.time()

        while flash_active and (time.time() - start_time) < 5:  # ✅ Stop na 5 seconden
            for esp_id in ESP_IDS:
                set_rgb_color(esp_id, r, g, b)
            time.sleep(0.5)
            for esp_id in ESP_IDS:
                set_rgb_color(esp_id, 0, 0, 0)  # LEDs uit
            time.sleep(0.5)

        flash_active = False  # ✅ Knippermodus gestopt
        print(f"✅ Knippermodus afgerond: {mode} (R:{r}, G:{g}, B:{b})")

# **Stuur RGB-kleur naar een specifieke ESP**
def set_rgb_color(esp_id, r, g, b, brightness=100):
    command = {
        "id": esp_id,
        "led": "ON",
        "r": r,
        "g": g,
        "b": b,
        "brightness": brightness
    }
    mqtt_client.publish(MQTT_TOPIC_RGB, json.dumps(command))
    print(f"📡 LED-kleur gestuurd naar ESP {esp_id}: R:{r}, G:{g}, B:{b}")

@app.route("/")
def index():
    return jsonify({"status": "success", "message": "Flask MQTT RGB Controller"})

@app.route("/reset", methods=["POST"])
def reset_color():
    """ Reset alle LEDs naar blauw """
    set_rgb_mode("static_blue")
    return jsonify({"status": "success", "message": "LEDs op blauw gezet"})

@app.route("/set_color", methods=["POST"])
def set_color():
    """ Handmatig een kleur instellen via een POST request """
    data = request.json
    esp_id = data.get("id", None)
    r = data.get("r", 0)
    g = data.get("g", 0)
    b = data.get("b", 0)
    brightness = data.get("brightness", 100)

    if esp_id in ESP_IDS:
        set_rgb_color(esp_id, r, g, b, brightness)
        return jsonify({"status": "success", "message": f"LEDs ingesteld op R:{r} G:{g} B:{b} voor ESP {esp_id}"})
    else:
        return jsonify({"status": "error", "message": "Ongeldige ESP ID"}), 400

if __name__ == "__main__":
    setup_mqtt()
    print("🚀 MQTT gestart, zet alle LEDs op blauw!")
    set_rgb_mode("static_blue")  # Zet alle ESP's op blauw bij opstart
    app.run(host="0.0.0.0", port=8443)
