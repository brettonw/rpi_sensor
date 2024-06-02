#! /usr/bin/env python3

# EZO pH Docs: https://files.atlas-scientific.com/pH_EZO_Datasheet.pdf

from AtlasEzoPh import AtlasEzoPh
from AtlasEzoRtd import AtlasEzoRtd
from interpolate import interpolate, XYPair


class AtlasEzoPhWithTemperatureCorrection(AtlasEzoPh):
    """
    The EZO pH sensor is configured to return pH in the range 0..14, and a temperature sensor for
    temperature correction
    """

    def __init__(self, address: int = 0x63, rtd: AtlasEzoRtd = AtlasEzoRtd()):
        super().__init__(address)
        self._rtd = rtd

    def soft_reset(self) -> None:
        super().soft_reset()
        self._rtd.soft_reset()

    # READ FUNCTIONS

    @property
    def temperature(self):
        return self._rtd.temperature

    @property
    def ph(self) -> float:
        return self.query_float(f"RT,{self.temperature:.03f}", AtlasEzoPh.PH_ERROR)

    # CALIBRATION FUNCTIONS

    def calibrate_low(self, unused: float = 0) -> bool:
        self._rtd.wait_for_stable_value()
        target_value = interpolate([
            XYPair( 5.0, 4.00),
            XYPair(10.0, 4.00),
            XYPair(15.0, 4.00),
            XYPair(20.0, 4.00),
            XYPair(25.0, 4.00),
            XYPair(30.0, 4.01),
            XYPair(35.0, 4.02),
            XYPair(40.0, 4.03),
            XYPair(45.0, 4.04),
            XYPair(50.0, 4.05)
        ], self.temperature)
        return super().calibrate_low(target_value)

    def calibrate_mid(self, unused: float = 0.0) -> bool:
        # use the temperature to compute a target from the table on the side of the bottle
        self._rtd.wait_for_stable_value()
        target_value = interpolate([
            XYPair( 5.0, 7.09),
            XYPair(10.0, 7.06),
            XYPair(15.0, 7.04),
            XYPair(20.0, 7.02),
            XYPair(25.0, 7.00),
            XYPair(30.0, 6.99),
            XYPair(35.0, 6.98),
            XYPair(40.0, 6.97),
            XYPair(45.0, 6.97),
            XYPair(50.0, 6.96)
        ], self.temperature)
        return super().calibrate_mid(target_value)

    def calibrate_high(self, unused: float = 0.0) -> bool:
        self._rtd.wait_for_stable_value()
        target_value = interpolate([
            XYPair( 5.0, 10.25),
            XYPair(10.0, 10.18),
            XYPair(15.0, 10.12),
            XYPair(20.0, 10.06),
            XYPair(25.0, 10.00),
            XYPair(30.0,  9.96),
            XYPair(35.0,  9.92),
            XYPair(40.0,  9.88),
            XYPair(45.0,  9.85),
            XYPair(50.0,  9.82)
        ], self.temperature)
        return super().calibrate_high(target_value)

    def calibrate_three_point(self):
        print("Place the pH and RTD probes in the mid (pH 7.00) solution")
        print("Press (ENTER) to continue")
        input()
        self.calibrate_mid()

        print("Place the pH and RTD probes in the low (pH 4.00) solution")
        print("Press (ENTER) to continue")
        input()
        self.calibrate_low()

        print("Place the pH and RTD probes in the high (pH 10.00) solution")
        print("Press (ENTER) to continue")
        input()
        self.calibrate_high()

        print("Calibration complete.")


def main():
    print("Start")
    device = AtlasEzoPhWithTemperatureCorrection()
    print("Soft Reset")
    device.soft_reset()
    print(f"Units: {device.units}")
    print(f"Temperature: {device.temperature}")
    print(f"Calibration: {device.calibration_type}")
    print(f"pH: {device.ph}")


if __name__ == '__main__':
    main()
