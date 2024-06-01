import RPi.GPIO as GPIO
from entity import Entity, Control


class Switch(Control):
    PIN = "pin"

    def __init__(self, entity:dict):
        super().__init__(entity)
        # check that states only has two elements
        assert len(self._entity[Entity.STATES]) == 2

        # XXX what do we do about errors?

    @property
    def pin (self):
        return self._entity[Switch.PIN]

    def set(self, value: str | bool) -> bool:
        # determine the value we want to set on the switch
        if self.updateValue (value):
            GPIO.setmode(GPIO.BOARD)
            GPIO.setwarnings(False)

            GPIO.setup(self.pin, GPIO.OUT)

            # NOTE that our GPIO implementation has pin = false is on, pin = true is off - can we change that?
            GPIO.output(self.pin, value)

            # return true
            return True
        return False
