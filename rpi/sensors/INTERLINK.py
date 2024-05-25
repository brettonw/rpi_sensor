#! /usr/bin/env python3

# documentation: https://www.whiteboxes.ch/docs/tentacle/t3-mkII/#/?id=introduction
# source: https://github.com/whitebox-labs/whitebox-raspberry-ezo

# newer version of the whitebox: https://atlas-scientific.com/electrical-isolation/i3-interlink/#

# new github: https://github.com/AtlasScientific/Raspberry-Pi-sample-code
# conductivity calibration: https://www.instructables.com/Atlas-Scientific-EZO-EC-Calibration-Procedure/
# ph calibration: https://www.instructables.com/Atlas-Scientific-EZO-PH-Calibration-Procedure/

import time
from AtlasI2C import (
    AtlasI2C
)

def get_devices():
    device = AtlasI2C()
    device_address_list = device.list_i2c_devices()
    device_list = []

    for i in device_address_list:
        device.set_i2c_address(i)
        response = device.query("I")
        try:
            moduletype = response.split(",")[1]
            response = device.query("name,?").split(",")[1]
        except IndexError:
            #print(">> WARNING: device at I2C address " + str(i) + " has not been identified as an EZO device, and will not be queried")
            continue
        device_list.append(AtlasI2C(address = i, moduletype = moduletype, name = response))
    return device_list

def main():

    device_list = get_devices()
    device = device_list[0]

    for dev in device_list:
        dev.write("R")
    time.sleep(device.long_timeout)
    for dev in device_list:
        print(dev.read())

if __name__ == '__main__':
    main()
