#! /usr/bin/env python3

#! /usr/bin/env python3

from DFRobot_GP8403 import DFRobot_GP8403,OUTPUT_RANGE_10V
from bedrock_cgi import ServiceBase
import RPi.GPIO as GPIO
from time import sleep
import cgitb


cgitb.enable()


UNUSED = 11
HEATER = 13
PUMP = 15

# we look for this text, but false input is True to the GPIO
FALSE = [False, "false", "False", "FALSE", "no", "No", "NO", "off", "Off", "OFF"]
TRUE = [True, "true", "True", "TRUE", "yes", "Yes", "YES", "on", "On", "ON"]


def event_ok(event):
    event.ok({"OK": "OK"})


def handle_light(event):
    dac = DFRobot_GP8403(0x5f)
    while dac.begin() != 0:
        sleep(1)
    dac.set_DAC_outrange(OUTPUT_RANGE_10V)
    dac.set_DAC_out_voltage(int(float(event.query["brightness"])) * 100, 0)
    dac.set_DAC_out_voltage(int(float(event.query["color"])) * 100, 1)
    event_ok(event)


def do_gpio(pin: int, state: bool):
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(state)
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, state)


def handle_pump(event):
    state = event.query["state"]
    if state in FALSE:
        do_gpio(PUMP, True)
    elif state in TRUE:
        do_gpio(PUMP, False)
    event_ok(event)


def handle_heater(event):
    state = event.query["state"]
    if state in FALSE:
        do_gpio(HEATER, True)
    elif state in TRUE:
        do_gpio(HEATER, False)
    event.ok({"OK": "OK"})


ServiceBase.respond()
