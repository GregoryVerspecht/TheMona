import board
import neopixel
import time

# Configuratie
LED_COUNT = 14        # Aantal LEDs in de strip/ring
LED_PIN = board.D18   # GPIO-pin waarop de datalijn is aangesloten
LED_BRIGHTNESS = 0.25  # Helderheid (tussen 0.0 en 1.0)
LED_ORDER = neopixel.GRB  # LED-kleurvolgorde

# Initialiseer de Neopixels
pixels = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False, pixel_order=LED_ORDER)

def color_wipe(color, wait):
    """Vul de strip met één kleur"""
    for i in range(LED_COUNT):
        pixels[i] = color
        pixels.show()
        time.sleep(wait)

def rainbow_cycle(wait):
    """Maak een regenboogeffect"""
    for j in range(255):
        for i in range(LED_COUNT):
            pixel_index = (i * 256 // LED_COUNT) + j
            pixels[i] = wheel(pixel_index & 255)
        pixels.show()
        time.sleep(wait)

def wheel(pos):
    """Bereken kleuren voor een regenboogeffect"""
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    else:
        pos -= 170
        return (pos * 3, 0, 255 - pos * 3)

# Voorbeeld: kleuren afspelen
try:
    while True:
        color_wipe((255, 0, 0), 0.1)  # Rood
        color_wipe((0, 255, 0), 0.1)  # Groen
        color_wipe((0, 0, 255), 0.1)  # Blauw
        #rainbow_cycle(0.01)          # Regenboog
except KeyboardInterrupt:
    pixels.fill((0, 0, 0))
    pixels.show()
