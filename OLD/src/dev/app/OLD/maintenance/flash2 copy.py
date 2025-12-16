import board
import neopixel
import time
import signal
import sys

# Configuratie
LED_COUNT = 14        # Aantal LEDs in de strip/ring
LED_PIN = board.D18   # GPIO-pin waarop de datalijn is aangesloten
LED_BRIGHTNESS = 0.95 # Helderheid (tussen 0.0 en 1.0)
LED_ORDER = neopixel.GRB  # LED-kleurvolgorde

# Initialiseer de Neopixels
pixels = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False, pixel_order=LED_ORDER)

def flash_section(led_indices, color, duration):
    for i in led_indices:
        pixels[i] = color
    pixels.show()
    time.sleep(duration)
    pixels.fill((0, 0, 0))
    pixels.show()

def alternating_flash(color, flash_speed, cycles):
    left_section = [1, 2, 3, 4, 5, 6, 7]
    right_section = [0, 8, 9, 10, 11, 12, 13]
    
    for _ in range(cycles):
        flash_section(left_section, color, flash_speed)
        flash_section(right_section, color, flash_speed)

def shutdown_handler(signum, frame):
    """
    Wordt aangeroepen bij SIGINT of SIGTERM
    """
    print(f"Signaal {signum} ontvangen, stoppen...")
    pixels.fill((0, 0, 0))
    pixels.show()
    sys.exit(0)

# Koppel signalen aan de shutdown handler
signal.signal(signal.SIGINT, shutdown_handler)  # CTRL+C
signal.signal(signal.SIGTERM, shutdown_handler) # Kill of systemctl stop

# Hoofdloop
try:
    while True:
        alternating_flash((0, 0, 255), flash_speed=0.1, cycles=5)
        time.sleep(0.5)
except KeyboardInterrupt:
    print("KeyboardInterrupt ontvangen, stoppen...")
    # Dit blok is optioneel als je signalen al hebt ingesteld.
