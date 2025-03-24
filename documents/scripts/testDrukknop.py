import RPi.GPIO as GPIO
import pygame
import time

# GPIO-pinnen
BUTTON_PIN = 17  # GPIO-pin waarop de knop is aangesloten
LED_PIN = 18     # GPIO-pin waarop de LED is aangesloten

# Geluidsbestand
SOUND_FILE = "./PeppaPigRev02.wav"  # Vervang met het pad naar je geluidsbestand

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Pull-up weerstand
GPIO.setup(LED_PIN, GPIO.OUT)

# Pygame setup voor geluid
pygame.mixer.init()
pygame.mixer.music.load(SOUND_FILE)

# Functie om geluid af te spelen en LED aan te zetten
def play_sound_and_light():
    # Zet de LED aan
    GPIO.output(LED_PIN, GPIO.HIGH)
    print("LED aan, geluid start.")

    # Speel het geluid af
    pygame.mixer.music.play()

    # Wacht tot het geluid is afgelopen
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

    # Zet de LED uit na afloop
    GPIO.output(LED_PIN, GPIO.LOW)
    print("LED uit, geluid gestopt.")

# Hoofdprogramma
try:
    print("Druk op de knop om geluid af te spelen.")
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:  # Knop ingedrukt (laag door pull-up configuratie)
            play_sound_and_light()
            time.sleep(0.5)  # Anti-bounce tijd
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Programma gestopt.")

finally:
    GPIO.cleanup()
    print("GPIO vrijgegeven.")
