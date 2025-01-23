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

def flash_section(led_indices, color, duration):
    """
    Laat een specifieke sectie van LEDs flikkeren.
    
    :param led_indices: Lijst van indices van LEDs die aangaan
    :param color: Tuple met RGB-waarden (bijvoorbeeld (0, 0, 255) voor blauw)
    :param duration: Tijd dat de LEDs aanblijven (in seconden)
    """
    # Zet alleen de geselecteerde LEDs aan
    for i in led_indices:
        pixels[i] = color
    pixels.show()
    time.sleep(duration)
    # Zet alle LEDs uit
    pixels.fill((0, 0, 0))
    pixels.show()

def alternating_flash(color, flash_speed, cycles):
    """
    Simuleer een links-rechts wisselend flikkerpatroon.
    
    :param color: Tuple met RGB-waarden (bijvoorbeeld (0, 0, 255) voor blauw)
    :param flash_speed: Tijd tussen flitsen (in seconden)
    :param cycles: Aantal keer dat het patroon herhaald wordt
    """
    left_section = [1, 2, 3,4, 5, 6,7]  # LEDs 0, 1, 2 (linkerkant)
    right_section = [0,8,9,10,11,12,13] # LEDs 4, 5, 6 (rechterkant)
    middle_led = [0,7]           # Middelste LED (uitgeschakeld)
    
    for _ in range(cycles):
        # Linkerkant aan
        flash_section(left_section, color, flash_speed)
        
        # Rechterkant aan
        flash_section(right_section, color, flash_speed)

# Voorbeeld: blauw flikkerlicht met links-rechts wisseling
try:
    while True:
        alternating_flash((0, 0, 255), flash_speed=0.1, cycles=5)
        time.sleep(0.5)  # Pauze na een reeks cycli
except KeyboardInterrupt:
    # Schakel alle LEDs uit bij stoppen
    pixels.fill((0, 0, 0))
    pixels.show()
