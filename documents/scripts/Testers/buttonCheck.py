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
    "./meow.wav",  # Geluid voor knop 1
    "./PeppaPigRev02.wav",  # Geluid voor knop 2
    "./meow.wav",  # Geluid voor knop 3
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

def play_sound_and_log(button_index):
    """
    Speel een geluid af, log knopactiviteit en laat de LED en NeoPixels reageren.

    :param button_index: Index van de knop die is ingedrukt.
    """
    print(f"Knop {button_index + 1} ingedrukt.")

    # Stop huidig spelend geluid als er een nieuwe knop wordt ingedrukt
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()

    # Zet de LED aan
    GPIO.output(LED_PIN, GPIO.HIGH)

    # Laad en speel het bijbehorende geluid af
    pygame.mixer.music.load(SOUND_FILES[button_index])
    pygame.mixer.music.play()

    # Laat de NeoPixels oplichten in een specifieke kleur
    color = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255)][button_index]
    pixels.fill(color)
    pixels.show()

    # Wacht tot het geluid is afgelopen of een nieuwe knop wordt ingedrukt
    sound_duration = 3  # Duur in seconden dat de LED actief blijft
    start_time = time.time()
    while time.time() - start_time < sound_duration:
        if any(GPIO.input(pin) == GPIO.LOW for pin in BUTTON_PINS):  # Controleer op nieuwe knop
            pygame.mixer.music.stop()
            break
        time.sleep(0.1)

    # Zet alles uit als geen andere knop wordt ingedrukt
    if not any(GPIO.input(pin) == GPIO.LOW for pin in BUTTON_PINS):
        GPIO.output(LED_PIN, GPIO.LOW)
        pixels.fill((0, 0, 0))
        pixels.show()

def main():
    """Hoofdprogramma voor het controleren van knoppen en uitvoeren van acties."""
    try:
        print("Druk op een knop om een actie uit te voeren.")
        while True:
            for i, pin in enumerate(BUTTON_PINS):
                if GPIO.input(pin) == GPIO.LOW:  # Knop ingedrukt
                    play_sound_and_log(i)
                    time.sleep(0.5)  # Anti-bounce tijd
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Programma gestopt.")

    finally:
        GPIO.cleanup()
        print("GPIO vrijgegeven.")

if __name__ == "__main__":
    main()
