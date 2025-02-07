import paho as mqtt
import time
import json

# MQTT Configuratie
MQTT_BROKER = "192.168.69.69"
MQTT_TOPIC = "neopixel/set"

client = mqtt.Client()
client.connect(MQTT_BROKER, 1883, 60)

def flash_section(led_indices, color, duration):
    """Laat een sectie LEDs aanzetten en vervolgens uitzetten."""
    msg = json.dumps({"r": color[0], "g": color[1], "b": color[2]})
    client.publish(MQTT_TOPIC, msg)
    time.sleep(duration)
    
    msg = json.dumps({"r": 0, "g": 0, "b": 0})  # LED uit
    client.publish(MQTT_TOPIC, msg)
    time.sleep(duration)

def alternating_flash(color, flash_speed, cycles):
    """Laat linker- en rechtersecties afwisselend knipperen."""
    left_section = [1, 2, 3, 4, 5, 6, 7]
    right_section = [0, 8, 9, 10, 11, 12, 13]
    
    for _ in range(cycles):
        flash_section(left_section, color, flash_speed)
        flash_section(right_section, color, flash_speed)

try:
    while True:
        alternating_flash((0, 0, 255), flash_speed=0.1, cycles=5)
        time.sleep(0.5)
except KeyboardInterrupt:
    print("❌ Flash-modus gestopt.")
    msg = json.dumps({"r": 0, "g": 0, "b": 0})  # LEDs uit
    client.publish(MQTT_TOPIC, msg)
