#! /usr/bin/env python3

# documentation: https://www.whiteboxes.ch/docs/tentacle/t3-mkII/#/?id=introduction
# source: https://github.com/whitebox-labs/whitebox-raspberry-ezo

# newer version of the whitebox: https://atlas-scientific.com/electrical-isolation/i3-interlink/#

# new github: https://github.com/AtlasScientific/Raspberry-Pi-sample-code
# conductivity calibration: https://www.instructables.com/Atlas-Scientific-EZO-EC-Calibration-Procedure/
# ph calibration: https://www.instructables.com/Atlas-Scientific-EZO-PH-Calibration-Procedure/

import io
import fcntl
import time


class AtlasI2C:
    # the default names for ezo modules
    EZO_MODULE_PH = "ph"
    EZO_MODULE_CONDUCTIVITY = "conductivity"
    EZO_MODULE_TEMPERATURE = "temperature"

    # the timeout needed to query readings and calibrations
    LONG_TIMEOUT = 1.5

    # timeout for regular commands
    SHORT_TIMEOUT = .3

    # the default bus for I2C on the newer Raspberry Pis,
    # certain older boards use bus 0
    DEFAULT_BUS = 1

    # the default address for the sensor
    LONG_TIMEOUT_COMMANDS = ("R", "CAL")
    SLEEP_COMMANDS = ("SLEEP")

    def __init__(self, ezo):
        """
        open two file streams, one for reading and one for writing
        the specific I2C channel is selected with bus
        it is usually 1, except for older revisions where its 0
        wb and rb indicate binary read and write
        """

        ezo_address = {
            AtlasI2C.EZO_MODULE_PH: 0x63,
            AtlasI2C.EZO_MODULE_CONDUCTIVITY: 0x64,
            AtlasI2C.EZO_MODULE_TEMPERATURE: 0x66
        }
        if ezo in ezo_address:
            self._ezo = ezo
            self.file_read = io.open(file="/dev/i2c-{}".format(AtlasI2C.DEFAULT_BUS), mode="rb", buffering=0)
            self.file_write = io.open(file="/dev/i2c-{}".format(AtlasI2C.DEFAULT_BUS), mode="wb", buffering=0)
            self._address = self.set_i2c_address(ezo_address[ezo])

            # set the units
            self._units = {
                AtlasI2C.EZO_MODULE_PH: "pH",
                AtlasI2C.EZO_MODULE_CONDUCTIVITY: "uS",
                AtlasI2C.EZO_MODULE_TEMPERATURE: "C"
            }[ezo]

    @property
    def ezo(self):
        return self._ezo

    @property
    def units(self):
        return self._units

    @property
    def address(self):
        return self._address

    def set_i2c_address(self, address):
        """
        set the I2C communications to the slave specified by the address
        the commands for I2C dev using the ioctl functions are specified in
        the i2c-dev.h file from i2c-tools
        """
        i2c_slave = 0x703
        fcntl.ioctl(self.file_read, i2c_slave, address)
        fcntl.ioctl(self.file_write, i2c_slave, address)
        return address

    def write(self, cmd):
        """
        appends the null character and sends the string over I2C
        """
        cmd += "\00"
        self.file_write.write(cmd.encode('latin-1'))

    @staticmethod
    def handle_raspi_glitch(response):
        """
        Change MSB to 0 for all received characters except the first
        and get a list of characters
        NOTE: having to change the MSB to 0 is a glitch in the raspberry pi,
        and you shouldn't have to do this!
        """
        return list(map(lambda x: chr(x & ~0x80), list(response)))

    @staticmethod
    def response_valid(response):
        valid = True
        error_code = None
        if len(response) > 0:
            error_code = str(response[0])
            if error_code != '1':
                valid = False
        return valid, error_code

    def read(self, num_of_bytes=31):
        response = self.file_read.read(num_of_bytes)
        # print(response)
        is_valid, error_code = AtlasI2C.response_valid(response=response)
        return str(''.join(AtlasI2C.handle_raspi_glitch(response[1:]))) if is_valid else "\"error (" + error_code + ")\""

    def get_command_timeout(self, command):
        if command.upper().startswith(self.LONG_TIMEOUT_COMMANDS):
            return self.LONG_TIMEOUT
        elif not command.upper().startswith(self.SLEEP_COMMANDS):
            return self.SHORT_TIMEOUT
        return None

    def query(self, command):
        """
        write a command to the board, wait the correct timeout,
        and read the response
        """
        self.write(command)
        current_timeout = self.get_command_timeout(command=command)
        if not current_timeout:
            return "sleep mode"
        else:
            time.sleep(current_timeout)
            return self.read()

    def close(self):
        self.file_read.close()
        self.file_write.close()

    def fetch(self):
        value = self.query("R")
        return "\"" + self.ezo + "\":" + value + ",\"" + self.ezo + "-unit\":\"" + self.units + "\""


def main():
    device_list = [
        AtlasI2C(AtlasI2C.EZO_MODULE_PH),
        AtlasI2C(AtlasI2C.EZO_MODULE_CONDUCTIVITY),
        AtlasI2C(AtlasI2C.EZO_MODULE_TEMPERATURE)
    ]
    output = ""
    comma = ""
    for device in device_list:
        output += comma + device.fetch()
        comma = ","
    print(output)


if __name__ == '__main__':
    main()
