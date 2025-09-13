from flask import Flask, render_template, request, jsonify
import subprocess
import os
import signal
import paho.mqtt.client as mqtt
import json

app = Flask(
    __name__,
    template_folder=os.path.join(os.getcwd(), "views"),
    static_folder=os.path.join(os.getcwd(), "static")
)

# MQTT Configuratie
MQTT_BROKER = "192.168.69.69"
MQTT_PORT = 1883
MQTT_TOPIC_BUTTONS = "esp/status"  # ESP publiceert knopstatus hier
MQTT_TOPIC_LEDS = "neopixel/set"  # Flask stuurt LED-commando's naar ESP

mqtt_client = mqtt.Client()

# Actieve processen voor modes
active_process = None


### 📡 **Stap 1: Callback-functie voor MQTT berichten**
def on_message(client, userdata, message):
    print(f"📩 MQTT Bericht ontvangen: {message.topic}")
    payload = message.payload.decode("utf-8")
    print(f"📜 Data: {payload}")

    try:
        data = json.loads(payload)

        if "event" in data and data["event"] == "PRESSED":
            esp_id = data.get("id", "Unknown")
            print(f"🎛️ ESP {esp_id} heeft een knop ingedrukt!")

            # **Actie bij knopdruk**
            handle_button_press(esp_id)

    except json.JSONDecodeError:
        print("❌ Ongeldig JSON-formaat ontvangen!")


### 📡 **Stap 2: Flask start een MQTT-client en luistert naar ESP buttons**
def setup_mqtt():
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.subscribe(MQTT_TOPIC_BUTTONS)
    mqtt_client.loop_start()


### **📡 Stap 3: Reactie op knopdruk**
def handle_button_press(esp_id):
    print(f"🚀 ESP {esp_id} heeft een knop ingedrukt!")

    # **Start een mode bij knopdruk**
    if esp_id == 1:
        start_mode("Squid Game", "game_modes")
    elif esp_id == 2:
        start_mode("Russian Roulette", "game_modes")
    elif esp_id == 3:
        send_rgb_command(esp_id, 255, 0, 0)  # ESP3 knippert rood
    else:
        print("⚠️ Geen actie ingesteld voor deze ESP")


### **📡 Stap 4: Stuur LED-commando naar een ESP**
def send_rgb_command(esp_id, r, g, b, brightness=100):
    command = {
        "id": esp_id,
        "led": "ON",
        "r": r,
        "g": g,
        "b": b,
        "brightness": brightness
    }
    mqtt_client.publish(MQTT_TOPIC_LEDS, json.dumps(command))
    print(f"📡 LED update naar ESP {esp_id}: {command}")


### **🚀 Flask Routes**
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/start", methods=["POST"])
def start_mode():
    global active_process
    mode = request.json.get("mode")
    category = request.json.get("category")

    if category in categories and mode in categories[category]:
        if active_process is not None:
            return jsonify({"status": "error", "message": "A mode is already running"})

        process = subprocess.Popen(["sudo", "python", categories[category][mode]])
        active_process = {"mode": mode, "category": category, "process": process}
        return jsonify({"status": "success", "message": f"{mode} from {category} started"})

    return jsonify({"status": "error", "message": "Invalid mode or category"})


@app.route("/stop", methods=["POST"])
def stop_mode():
    global active_process
    mode = request.json.get("mode")
    category = request.json.get("category")

    if active_process and active_process["mode"] == mode and active_process["category"] == category:
        process = active_process["process"]
        os.kill(process.pid, signal.SIGTERM)
        active_process = None
        return jsonify({"status": "success", "message": f"{mode} from {category} stopped"})

    return jsonify({"status": "error", "message": "Mode not running or invalid"})


if __name__ == "__main__":
    setup_mqtt()
    app.run(host="0.0.0.0", port=8443, ssl_context=("/home/mona/ssl/cert.pem", "/home/mona/ssl/key.pem"))
