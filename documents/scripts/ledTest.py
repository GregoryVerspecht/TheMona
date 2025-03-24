import board
import neopixel
import time

# Configuratie
LED_COUNT = 14        # Aantal LEDs in de strip/ring
LED_PIN = board.D18   # GPIO-pin waarop de datalijn is aangesloten
LED_BRIGHTNESS = 0.95  # Helderheid (tussen 0.0 en 1.0)
LED_ORDER = neopixel.GRB  # LED-kleurvolgorde

# Initialiseer de Neopixels
pixels = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False, pixel_order=LED_ORDER)

def static_color(color):
    """
    Laat alle LEDs statisch branden in één kleur.
    
    :param color: Tuple met RGB-waarden (bijvoorbeeld (255, 0, 0) voor rood)
    """
    pixels.fill(color)
    pixels.show()

# Voorbeeld: Laat alle LEDs rood branden
try:
    static_color((255, 0, 0))  # Stel de kleur in (bijv. rood)
    while True:
        time.sleep(1)  # Houd de LEDs statisch aan
except KeyboardInterrupt:
    # Schakel alle LEDs uit bij stoppen
    pixels.fill((0, 0, 0))
    pixels.show()
