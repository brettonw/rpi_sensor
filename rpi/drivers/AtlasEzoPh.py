#! /usr/bin/env python3

# EZO pH Docs: https://files.atlas-scientific.com/pH_EZO_Datasheet.pdf

from AtlasEzo import AtlasEzo


class AtlasEzoPh(AtlasEzo):
    """
    The EZO pH sensor is configured to return pH in the range 0..14
    """

    # we use -999.0 as the error value
    PH_ERROR = -999.0

    def __init__(self, address: int = 0x63):
        super().__init__("ph", address)

    def soft_reset(self) -> None:
        AtlasEzo._assert_equals(self.query("pHext,0"), AtlasEzo.OK)

    @property
    def value(self) -> float:
        return self.ph

    @property
    def ph(self) -> float:
        return self.query_float("R", -1.0)

    # CALIBRATION FUNCTIONS
    # NOTE three point calibration should proceed as mid, low, high because the EZO pH module will
    #      clear the calibration when mid is called, meaning low and high will have to be called
    #      afterward to complete calibration

    @property
    def calibration_type(self) -> int:
        """
        :return: -1 = an error was encountered, 0 = not-calibrated, 1 = one-point, 2 = two-point,
                 3 = three-point
        """
        response = self.query("CAL,?")
        try:
            return int(response.split(',', 1)[1]) if response.startswith("?CAL,") else AtlasEzo.CALIBRATION_ERROR
        except ValueError:
            return AtlasEzo.CALIBRATION_ERROR

    def _calibrate(self, target: str, target_value: float) -> bool:
        self.wait_for_stable_value()
        return self.query(f"CAL,{target},{target_value:.03f}") == AtlasEzo.OK

    def calibrate_low(self, target_value: float = 4.0) -> bool:
        return self._calibrate("low", target_value)

    def calibrate_mid(self, target_value: float = 7.0) -> bool:
        return self._calibrate("mid", target_value)

    def calibrate_high(self, target_value: float = 10.0) -> bool:
        return self._calibrate("high", target_value)


def main():
    print("Start")
    device = AtlasEzoPh()
    print("Soft Reset")
    device.soft_reset()
    print(f"Units: {device.units}")
    print(f"Calibration: {device.calibration_type}")
    print(f"pH: {device.ph}")


if __name__ == '__main__':
    main()
