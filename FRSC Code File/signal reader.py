import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(26,GPIO.OUT)

while True:
    print(str(GPIO.input(26)))
    time.sleep(0.2)
