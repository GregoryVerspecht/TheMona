import board
import neopixel
import asyncio
import signal
import pygame

# Configuratie
LED_COUNT = 14        # Aantal LEDs in de strip/ring
LED_PIN = board.D18   # GPIO-pin waarop de datalijn is aangesloten
LED_BRIGHTNESS = 0.95 # Helderheid (tussen 0.0 en 1.0)
LED_ORDER = neopixel.GRB  # LED-kleurvolgorde

# Geluidsbestand
SOUND_FILE = "/home/mona/the-mona/static/assets/sounds/sound-of-the-police.wav"

# Initialiseer de Neopixels
pixels = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False, pixel_order=LED_ORDER)

# Pygame setup voor geluid
pygame.mixer.init()

async def play_sound():
    """Speelt het geluid af."""
    try:
        pygame.mixer.music.load(SOUND_FILE)
        print("Geluidsbestand succesvol geladen.")
        pygame.mixer.music.play()
        print("Geluid wordt afgespeeld.")
        while pygame.mixer.music.get_busy():
            print("Geluid speelt nog...")
            await asyncio.sleep(0.5)  # Controleert om de 0.5 seconden
        print("Geluid is klaar.")
    except pygame.error as e:
        print(f"Fout bij het afspelen van geluid: {e}")


async def alternating_flash(color, flash_speed, cycles):
    """Knippert LEDs afwisselend."""
    left_section = [1, 2, 3, 4, 5, 6, 7]
    right_section = [0, 8, 9, 10, 11, 12, 13]
    
    for _ in range(cycles):
        for i in left_section:
            pixels[i] = color
        pixels.show()
        await asyncio.sleep(flash_speed)
        
        for i in left_section:
            pixels[i] = (0, 0, 0)
        pixels.show()
        
        for i in right_section:
            pixels[i] = color
        pixels.show()
        await asyncio.sleep(flash_speed)
        
        for i in right_section:
            pixels[i] = (0, 0, 0)
        pixels.show()

def shutdown_handler(signum, frame):
    """Schakelt de LEDs uit en sluit af."""
    print(f"Signaal {signum} ontvangen, stoppen...")
    pixels.fill((0, 0, 0))
    pixels.show()
    asyncio.get_event_loop().stop()

# Koppel signalen aan de shutdown handler
signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

async def main():
    # Start het geluid en de LED-animatie tegelijkertijd
    await asyncio.gather(
        play_sound(),
        alternating_flash((0, 0, 255), flash_speed=0.1, cycles=50)  # Pas cycles aan zoals nodig
    )

if __name__ == "__main__":
    asyncio.run(main())
