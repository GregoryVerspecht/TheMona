import RPi.GPIO as GPIO
import time

BUTTON_PIN = 17  # De GPIO-pin waarop de knop is aangesloten

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Interne pull-up weerstand activeren

try:
    print("Druk op de knop...")
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:  # Knop ingedrukt
            print("Knop ingedrukt!")
        else:
            print("Knop niet ingedrukt.")
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Programma gestopt.")

finally:
    GPIO.cleanup()
    print("GPIO vrijgegeven.")
