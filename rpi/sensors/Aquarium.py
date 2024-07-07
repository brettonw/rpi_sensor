#! /usr/bin/env python3

from AtlasEzoPhWithTemperatureCorrection import AtlasEzoPhWithTemperatureCorrection
from AtlasEzoEcWithTemperatureCorrection import AtlasEzoEcWithTemperatureCorrection
from AtlasEzoRtd import AtlasEzoRtd


def main():
    rtd = AtlasEzoRtd()
    ph = AtlasEzoPhWithTemperatureCorrection(rtd=rtd)
    ec = AtlasEzoEcWithTemperatureCorrection(rtd=rtd)

    output = f"\"{rtd.name}\": {rtd.value}, \"{rtd.name}-unit\": \"{rtd.units}\""
    output += f", \"{ph.name}\": {ph.value}, \"{ph.name}-unit\": \"{ph.units}\""
    output += f", \"{ec.name}\": {ec.value}, \"{ec.name}-unit\": \"{ec.units}\""
    print(output)


if __name__ == '__main__':
    main()
