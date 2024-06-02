#! /usr/bin/env python3

# EZO RTD Docs: # https://files.atlas-scientific.com/EZO_RTD_Datasheet.pdf

from AtlasEzo import AtlasEzo
from time import time
from typing import Union


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
        response = self.query("S,?")
        self._units = response.split(',')[-1].upper()
        assert self._units in ["C", "F", "K"]
        # print(f"Units: {self._units}")

    def soft_reset(self) -> None:
        # set the temperature scale to degrees C
        self.set_units("c")

        # turn off the data logger
        AtlasEzo._assert_equals(self.query("D,0"), AtlasEzo.OK)

    @property
    def value(self) -> Union[float, int]:
        return self.temperature

    @property
    def temperature(self) -> float:
        now = time()
        if ((now - self._last_read_time) > AtlasEzoRtd.MAX_AGE) or (self._last_read_value == AtlasEzoRtd.TEMPERATURE_ERROR):
            self._last_read_value = self.query_float("R", AtlasEzoRtd.TEMPERATURE_ERROR)
            self._last_read_time = now
        return self._last_read_value

    def wait_for_stable_value(self):
        self._wait_for_stable_value(0.005, 20)

    def set_units(self, units: str):
        units = units.lower()
        if units in ["c", "f", "k"]:
            AtlasEzo._assert_equals(self.query(f"S,{units}"), AtlasEzo.OK)
            self._units = units.upper()
        # print(f"Units: {self._units}")

    # CALIBRATION FUNCTIONS

    @property
    def calibration_type(self) -> int:
        """
        :return: -1 = an error was encountered, 0 = not-calibrated, 1 = calibrated
        """
        response = self.query("CAL,?")
        try:
            return int(response.split(',', 1)[1]) if response.startswith("?CAL,") else AtlasEzo.CALIBRATION_ERROR
        except ValueError:
            return AtlasEzo.CALIBRATION_ERROR

    def calibrate(self, target_value: float = 100.0) -> bool:
        self.wait_for_stable_value()
        return self.query(f"CAL,{target_value:.3f}") == AtlasEzo.OK


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
