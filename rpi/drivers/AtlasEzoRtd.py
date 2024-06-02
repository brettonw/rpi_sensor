#! /usr/bin/env python3

# EZO RTD Docs: # https://files.atlas-scientific.com/EZO_RTD_Datasheet.pdf

from AtlasEzo import AtlasEzo
from time import time

class AtlasEzoRtd(AtlasEzo):
    """
    The EZO RTD sensor is configured to return temperature in degrees C
    """

    # we use -999.0 as the error value
    TEMPERATURE_ERROR = -999.0

    # the RTD encapsulator won't read the time more often than this (seconds)
    MAX_AGE = 5.0

    def __init__(self, address: int = 0x66):
        super().__init__("temperature", address)
        self._last_read_time: float = 0
        self._last_read_value: float = AtlasEzoRtd.TEMPERATURE_ERROR

        # fetch the units directly from the device
        self._get_units()


    def soft_reset(self) -> None:
        # set the temperature scale to degrees C
        AtlasEzo._assert_equals (self.query("S,c"), AtlasEzo.OK)

        # turn off the data logger
        AtlasEzo._assert_equals(self.query("D,0"), AtlasEzo.OK)

    def _get_command_timeout(self, command: str) -> float:
        return {
            "R": 0.6,
            "CAL": 0.6
        }.get(command, 0.3)

    # READ FUNCTIONS

    @property
    def value(self) -> float | int:
        return self.temperature

    @property
    def temperature(self) -> float:
        now = time()
        if ((now - self._last_read_time) > AtlasEzoRtd.MAX_AGE) or (self._last_read_value == AtlasEzoRtd.TEMPERATURE_ERROR):
            self._last_read_value = self.query_float("R", AtlasEzoRtd.TEMPERATURE_ERROR)
            self._last_read_time = now
        return self._last_read_value

    # CALIBRATION FUNCTIONS

    @property
    def calibration_type(self) -> int:
        """
        :return: -1 = an error was encountered, 0 = not-calibrated, 1 = calibrated
        """
        response = self.query("CAL,?", 0.3)
        try:
            return int(response.split(',', 1)[1]) if response.startswith("?CAL,") else AtlasEzo.CALIBRATION_ERROR
        except ValueError:
            return AtlasEzo.CALIBRATION_ERROR

    def calibrate(self, target_value: float = 100.0) -> bool:
        self.wait_for_stable_value(0.1)
        return self.query(f"CAL,{target_value:.3f}") == AtlasEzo.OK

    def _get_units(self):
        response = self.query("S,?")
        self._units = response.split(',')[-1].upper()
        #print(f"Units: {self._units}")

    def set_units(self, units:str):
        if units in ["c", "C", "f", "F", "k", "K"]:
            AtlasEzo._assert_equals(self.query(f"S,{units.lower()}"), AtlasEzo.OK)
            self._units = units.upper()
        #print(f"Units: {self._units}")

    def wait_for_stable_value(self):
        self._wait_for_stable_value(0.005, 20)


def main():
    print("Start")
    device = AtlasEzoRtd()
    print("Soft Reset")
    device.soft_reset()
    print(f"Units: {device.units}")
    print(f"Calibration: {device.calibration_type}")
    print(f"Temperature: {device.temperature}")


if __name__ == '__main__':
    main()
