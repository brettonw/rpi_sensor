#! /usr/bin/env python3

# EZO EC Docs: # https://files.atlas-scientific.com/EC_EZO_Datasheet.pdf

from AtlasEzo import AtlasEzo

class AtlasEzoEc(AtlasEzo):
    """
    The EZO EC sensor is configured to return conductivity and salinity on a seawater range using a
     K-1.0 probe
    """

    # we use -999.0 as the error value
    EC_ERROR = -999

    def __init__(self, address: int = 0x64):
        super().__init__("conductivity", address, "μS")

    def soft_reset(self) -> None:
        # set the probe type to the 1.0 range (normal seawater range probes). probes come in 0.1,
        # 1.0, and 10.0 ranges
        AtlasEzo._assert_equals(self.query("K,1.0"), AtlasEzo.OK)

        # ensure the output is set to conductivity only
        AtlasEzo._assert_equals(self.query("O,EC,1"), AtlasEzo.OK)
        AtlasEzo._assert_equals(self.query("O,S,0"), AtlasEzo.OK)
        AtlasEzo._assert_equals(self.query("O,TDS,0"), AtlasEzo.OK)
        AtlasEzo._assert_equals(self.query("O,SG,0"), AtlasEzo.OK)

    def _get_command_timeout(self, command: str) -> float:
        return {
            "R": 0.6,
            "RT": 0.9,
            "CAL": 0.6
        }.get(command, 0.3)

    # READ FUNCTIONS
    @property
    def conductivity(self) -> int:
        return self.query_int("R", AtlasEzoEc.EC_ERROR)

    # CALIBRATION FUNCTIONS
    # NOTE two-point calibration should proceed as dry, n, three-point calibration should proceed as
    # dry, low, high

    @property
    def calibration_type(self) -> int:
        """
        :return: -1 = an error was encountered, 0 = not-calibrated, 2 = two-point, 3 = three-point
        """
        response = self.query("CAL,?")
        try:
            calibration = int(response.split(',', 1)[1]) if response.startswith("?CAL,") else (AtlasEzo.CALIBRATION_ERROR - 1)
            return AtlasEzo.NOT_CALIBRATED if (calibration == AtlasEzo.NOT_CALIBRATED) else (calibration + 1)
        except ValueError:
            return AtlasEzo.CALIBRATION_ERROR

    def _calibrate(self, target: str) -> bool:
        self.wait_for_stable_value(40)
        return self.query(f"CAL,{target}") == AtlasEzo.OK

    def calibrate_dry(self) -> bool:
        return self._calibrate("dry")

    def calibrate_n(self, target_value: int = 53000) -> bool:
        return self._calibrate(f"{target_value}")

    def calibrate_low(self, target_value: int = 12880) -> bool:
        return self._calibrate(f"low,{target_value}")

    def calibrate_high(self, target_value: int = 80000) -> bool:
        return self._calibrate(f"high,{target_value}")

    def wait_for_stable_value(self):
        self._wait_for_stable_value(20, 20)

def main():
    print("Start")
    device = AtlasEzoEc()
    print("Soft Reset")
    device.soft_reset()
    print(f"Units: {device.units}")
    print(f"Calibration: {device.calibration_type}")
    print(f"Conductivity: {device.conductivity}")


if __name__ == '__main__':
    main()
