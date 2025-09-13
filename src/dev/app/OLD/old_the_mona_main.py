from flask import Flask, jsonify, request
from flask_cors import CORS
import RPi.GPIO as GPIO
import pygame
import board
import neopixel
import time

# GPIO-instellingen
BUTTON_PINS = [17, 27, 22, 5, 6, 13]
LED_PIN = 18
LED_COUNT = 14
NEOPIXEL_PIN = board.D18
LED_BRIGHTNESS = 0.25
LED_ORDER = neopixel.GRB
SOUND_FILES = ["./", "./PeppaPigRev02.wav", "./meow.wav", "./PeppaPigRev02.wav", "./PeppaPigRev02.wav", "./PeppaPigRev02.wav"]

GPIO.setmode(GPIO.BCM)
for pin in BUTTON_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED_PIN, GPIO.OUT)

pixels = neopixel.NeoPixel(NEOPIXEL_PIN, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False, pixel_order=LED_ORDER)
pygame.mixer.init()

app = Flask(__name__)
CORS(app)

def play_sound(button_index):
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
    GPIO.output(LED_PIN, GPIO.HIGH)
    pygame.mixer.music.load(SOUND_FILES[button_index])
    pygame.mixer.music.play()
    color = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255)][button_index]
    pixels.fill(color)
    pixels.show()
    time.sleep(3)
    GPIO.output(LED_PIN, GPIO.LOW)
    pixels.fill((0, 0, 0))
    pixels.show()

@app.route('/buttons', methods=['GET'])
def check_buttons():
    states = [GPIO.input(pin) == GPIO.LOW for pin in BUTTON_PINS]
    return jsonify({"buttons": states})

@app.route('/play-sound', methods=['POST'])
def trigger_sound():
    data = request.json
    button_index = data.get("button")
    if button_index is not None and 0 <= button_index < len(BUTTON_PINS):
        play_sound(button_index)
        return jsonify({"status": "Sound played", "button": button_index}), 200
    return jsonify({"error": "Invalid button index"}), 400

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5000, debug=True)
    finally:
        GPIO.cleanup()
