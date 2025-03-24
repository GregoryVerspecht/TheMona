import pygame
pygame.mixer.init()
pygame.mixer.music.load("/home/mona/the-mona/static/assets/sounds/sound-of-the-police.wav")
pygame.mixer.music.play()

while pygame.mixer.music.get_busy():
    pass
