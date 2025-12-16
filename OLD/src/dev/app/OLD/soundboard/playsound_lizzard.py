import pygame
import sys

# Initialiseer pygame mixer
pygame.mixer.init()

# Laad het geluidsbestand
pygame.mixer.music.load("/home/mona/the-mona/static/assets/sounds/lizard-button.mp3")
pygame.mixer.music.play()

# Wacht tot het geluid klaar is
while pygame.mixer.music.get_busy():
    pass

# Sluit het subprocess af zodra het geluid is afgelopen
sys.exit(0)
