import board
import neopixel
import time

# Configuratie
LED_COUNT = 7        # Aantal LEDs in de strip/ring
LED_PIN = board.D18   # GPIO-pin waarop de datalijn is aangesloten
LED_BRIGHTNESS = 0.5  # Helderheid (tussen 0.0 en 1.0)
LED_ORDER = neopixel.GRB  # LED-kleurvolgorde

# Initialiseer de Neopixels
pixels = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False, pixel_order=LED_ORDER)

def emergency_flash(color, flash_count, flash_speed, pause_duration):
    """
    Simuleer een flikkerend lichtpatroon.
    
    :param color: Tuple met RGB-waarden (bijvoorbeeld (0, 0, 255) voor blauw)
    :param flash_count: Aantal flitsen per cyclus
    :param flash_speed: Tijdsduur tussen flitsen (in seconden)
    :param pause_duration: Pauze na een cyclus (in seconden)
    """
    for _ in range(flash_count):
        # Zet alle LEDs aan
        pixels.fill(color)
        pixels.show()
        time.sleep(flash_speed)
        # Zet alle LEDs uit
        pixels.fill((0, 0, 0))
        pixels.show()
        time.sleep(flash_speed)
    # Pauze na de flitsen
    time.sleep(pause_duration)

# Voorbeeld: blauw flikkerlicht
try:
    while True:
        emergency_flash((0, 0, 255), flash_count=2, flash_speed=0.1, pause_duration=0.5)
except KeyboardInterrupt:
    # Schakel alle LEDs uit bij stoppen
    pixels.fill((0, 0, 0))
    pixels.show()
