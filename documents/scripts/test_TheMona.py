import RPi.GPIO as GPIO
import pygame
import time

# GPIO configuratie
LED_PIN = 18  # GPIO-pin waarop de LED is aangesloten

# Geluidsbestand
SOUND_FILE = "./PeppaPigRev02.wav"  # Vervang met het pad naar je geluidsbestand

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

# Pygame setup voor geluid
pygame.mixer.init()
pygame.mixer.music.load(SOUND_FILE)

try:
    # Zet de LED aan
    GPIO.output(LED_PIN, GPIO.HIGH)
    print("LED is aan.")

    # Speel het geluid af
    print("Geluid wordt afgespeeld.")
    pygame.mixer.music.play()

    # Wacht tot het geluid klaar is
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Programma onderbroken.")

finally:
    # Zet de LED uit en maak GPIO schoon
    GPIO.output(LED_PIN, GPIO.LOW)
    GPIO.cleanup()
    print("LED uit en GPIO vrijgegeven.")
