#! /usr/bin/env python3

# EZO EC Docs: # https://files.atlas-scientific.com/EC_EZO_Datasheet.pdf

from AtlasEzoEc import AtlasEzoEc
from AtlasEzoRtd import AtlasEzoRtd
from interpolate import interpolate, XYPair


class AtlasEzoEcWithTemperatureCorrection(AtlasEzoEc):
    """
    The EZO EC sensor is configured to return conductivity and salinity on a seawater range using a
     K-1.0 probe, and a temperature sensor for temperature correction
    """

    def __init__(self, address: int = 0x64, rtd: AtlasEzoRtd = AtlasEzoRtd()):
        super().__init__(address)
        self._rtd = rtd

    def soft_reset(self) -> None:
        super().soft_reset()
        self._rtd.soft_reset()

    @property
    def temperature(self):
        return self._rtd.temperature

    @property
    def conductivity(self) -> float:
        return self.query_float(f"RT,{self.temperature:.03f}", AtlasEzoEc.EC_ERROR)

    # CALIBRATION FUNCTIONS

    def calibrate_n(self, target_value: int = 53000) -> bool:
        # note this should really only be done at 77F/25C - we don't have a correction chart
        self._rtd.wait_for_stable_value()
        return self._calibrate(f"{target_value}")

    def calibrate_low(self, unused: int = 0) -> bool:
        self._rtd.wait_for_stable_value()
        target_value = interpolate([
            XYPair( 5.0,  8220),
            XYPair(10.0,  9330),
            XYPair(15.0, 10480),
            XYPair(20.0, 11670),
            XYPair(25.0, 12880),
            XYPair(30.0, 14120),
            XYPair(35.0, 15550),
            XYPair(40.0, 16880),
            XYPair(45.0, 18210),
            XYPair(50.0, 19550)
        ], self.temperature)
        return super().calibrate_low(int(target_value))

    def calibrate_high(self, unused: int = 0) -> bool:
        self._rtd.wait_for_stable_value()
        target_value = interpolate([
            XYPair( 5.0,  53500),
            XYPair(10.0,  59600),
            XYPair(15.0,  65400),
            XYPair(20.0,  72400),
            XYPair(25.0,  80000),
            XYPair(30.0,  88200),
            XYPair(35.0,  96400),
            XYPair(40.0, 104600),
            XYPair(45.0, 112800),
            XYPair(50.0, 121000)
        ], self.temperature)
        return super().calibrate_high(int(target_value))

    def calibrate_three_point(self):
        print("Remove the EC probe and shake it off")
        print("Press (ENTER) to continue")
        input()
        self.calibrate_dry()

        print("Place the EC and RTD probes in the low solution")
        print("Press (ENTER) to continue")
        input()
        self.calibrate_low()

        print("Place the EC and RTD probes in the high solution")
        print("Press (ENTER) to continue")
        input()
        self.calibrate_high()

        print("Calibration complete.")


def main():
    print("Start")
    device = AtlasEzoEcWithTemperatureCorrection()
    print("Soft Reset")
    device.soft_reset()
    print(f"Units: {device.units}")
    print(f"Temperature: {device.temperature}")
    print(f"Calibration: {device.calibration_type}")
    print(f"Conductivity: {device.conductivity}")


if __name__ == '__main__':
    main()
