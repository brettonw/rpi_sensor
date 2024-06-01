#! /usr/bin/env python3

import RPi.GPIO as GPIO
from time import sleep
from sys import argv

if len(argv) > 1:
  # could be 1 pin number, or 1 or more pin numbers followed by a value
  value = (len(argv) >= 3) and (argv[-1].lower() in ("yes", "true", "t", "1"))

  GPIO.setmode(GPIO.BOARD)
  GPIO.setwarnings(False)

  for i in range(1,len(argv)-1):
    pin = int(argv[i])
    print (f"Set PIN ({pin}) to {value}")
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, value)
    #GPIO.cleanup (pin)

