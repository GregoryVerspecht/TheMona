import RPi.GPIO as GPIO
import pygame
import board
import neopixel
import time

# GPIO-pinnen configuratie
BUTTON_PINS = [17, 27, 22, 5, 6, 13]  # GPIO-pinnen voor de knoppen
LED_PIN = 18  # GPIO-pin waarop de LED is aangesloten

# NeoPixel configuratie
LED_COUNT = 14        # Aantal LEDs in de strip/ring
NEOPIXEL_PIN = board.D18   # GPIO-pin waarop de NeoPixel datalijn is aangesloten
LED_BRIGHTNESS = 0.25  # Helderheid (tussen 0.0 en 1.0)
LED_ORDER = neopixel.GRB  # LED-kleurvolgorde

# Geluidsbestanden voor elke knop
SOUND_FILES = [
    "./PeppaPigRev02.wav",  # Geluid voor knop 1
    "./PeppaPigRev02.wav",  # Geluid voor knop 2
    "./PeppaPigRev02.wav",  # Geluid voor knop 3
    "./PeppaPigRev02.wav",  # Geluid voor knop 4
    "./PeppaPigRev02.wav",  # Geluid voor knop 5
    "./PeppaPigRev02.wav"   # Geluid voor knop 6
]

# GPIO setup
GPIO.setmode(GPIO.BCM)
for pin in BUTTON_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Pull-up weerstand
GPIO.setup(LED_PIN, GPIO.OUT)

# NeoPixel setup
pixels = neopixel.NeoPixel(NEOPIXEL_PIN, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False, pixel_order=LED_ORDER)

# Pygame setup voor geluid
pygame.mixer.init()

def play_sound_and_light(button_index):
    """
    Speel een geluid af en laat de LED en NeoPixels reageren.
    
    :param button_index: Index van de knop die is ingedrukt.
    """
    # Zet de LED aan
    GPIO.output(LED_PIN, GPIO.HIGH)

    # Laad en speel het bijbehorende geluid af
    pygame.mixer.music.load(SOUND_FILES[button_index])
    pygame.mixer.music.play()

    # Laat de NeoPixels oplichten in een specifieke kleur
    color = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255)][button_index]
    pixels.fill(color)
    pixels.show()

    # Wacht tot het geluid is afgelopen
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

    # Zet alles uit
    GPIO.output(LED_PIN, GPIO.LOW)
    pixels.fill((0, 0, 0))
    pixels.show()

def rainbow_cycle(wait, cycles=1):
    """Maak een regenboogeffect."""
    for _ in range(cycles):
        for j in range(255):
            for i in range(LED_COUNT):
                pixel_index = (i * 256 // LED_COUNT) + j
                pixels[i] = wheel(pixel_index & 255)
            pixels.show()
            time.sleep(wait)

def wheel(pos):
    """Bereken kleuren voor een regenboogeffect."""
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    else:
        pos -= 170
        return (pos * 3, 0, 255 - pos * 3)

# Hoofdprogramma
try:
    print("Druk op een knop om een actie uit te voeren.")
    while True:
        for i, pin in enumerate(BUTTON_PINS):
            if GPIO.input(pin) == GPIO.LOW:  # Knop ingedrukt
                print("Knop ingedrukt.")
                if i < 1:  # Knop 1 t/m 5 spelen geluid en LED-kleur
                    play_sound_and_light(i)
                elif i == 2:  # Knop 6 start regenboogeffect
                    rainbow_cycle(0.01, cycles=3)
                time.sleep(0.5)  # Anti-bounce tijd
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Programma gestopt.")

finally:
    GPIO.cleanup()
    print("GPIO vrijgegeven.")
