#! /usr/bin/env python3

# Atlas Interlink: https://atlas-scientific.com/electrical-isolation/i3-interlink/#

# Atlas GitHub: https://github.com/AtlasScientific/Raspberry-Pi-sample-code
# EZO Docs (for calibration and mode settings):
# https://files.atlas-scientific.com/pH_EZO_Datasheet.pdf
# https://files.atlas-scientific.com/EC_EZO_Datasheet.pdf
# https://files.atlas-scientific.com/EZO_RTD_Datasheet.pdf
# NOTE - to calibrate the sensors, use the AtlasI2c shell scripts in the GitHub repository to send
#        commands - might be useful to expose calibration later... as separate devices.

from abc import ABC, abstractmethod
from typing import Union
import io
import fcntl
from time import time, sleep
import json
from statistics import stdev
import itertools


class AtlasEzo(ABC):
    CALIBRATION_ERROR: int = -1
    NOT_CALIBRATED: int = 0
    ERROR: str = "ERROR"
    OK: str = "OK"

    def __init__(self, name: str, address: int, units: str = ""):

        # two file streams, one for reading and one for writing
        self.file_read = io.open(file="/dev/i2c-1", mode="rb", buffering=0)
        self.file_write = io.open(file="/dev/i2c-1", mode="wb", buffering=0)

        # tell this stream what i2c address to read/write from
        i2c_slave = 0x703
        fcntl.ioctl(self.file_read, i2c_slave, address)
        fcntl.ioctl(self.file_write, i2c_slave, address)

        # save out our values
        self._name = name
        self._address = address
        self._units = units

        # set up the gatekeeper on the write cycles, no more than one per second
        self._last_write_time = 0

    def soft_reset(self) -> None:
        pass

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> Union[float, int]:
        return 0

    @property
    def units(self) -> str:
        return self._units

    @property
    def address(self) -> int:
        return self._address

    def report(self, value: float) -> str:
        return json.dumps({
            "value": value,
            "unit": self.units
        })

    @staticmethod
    def _assert_equals(left, right) -> None:
        if left != right:
            print(f"Assertion Failure: ({left}) != ({right})");
            raise AssertionError

    def write(self, cmd: str) -> None:
        """
        appends the null character and sends the string over I2C
        """
        now = time()
        delta = now - self._last_write_time
        if delta < 1.0:
            sleep(1.0 - delta)
        self._last_write_time = time()
        cmd += "\00"
        self.file_write.write(cmd.encode('latin-1'))

    @staticmethod
    def _join(response: bytes) -> str:
        """
        this function is called when there is a success, to format the response bytes - for
        functions that don't actually have a response value, we substitute "OK"
        """
        # change MSB to 0 for all received characters except the first and get a list of characters
        # NOTE: this is a glitch in the raspberry pi,we shouldn't have to do this
        #print(f"response is ({response}), with length {len(response)}")
        valid_contents = (len(response) > 0) and (response[0] != 0)
        return "".join(list(map(lambda x: chr(x & ~0x80), list(response)))) if valid_contents else AtlasEzo.OK

    @staticmethod
    def _get_error(error_code: int) -> str:
        """
        error codes seem to be universal across the ezo modules
        :param error_code: the input code to return a string for
        :return: a string describing the result
        """
        return f"{AtlasEzo.ERROR} ({error_code}) - " + {
            255: "no data to send",
            254: "not ready",
            2: "syntax error",
            0: "no response"
        }.get(error_code, "UNKNOWN")

    def read(self, num_of_bytes: int = 31) -> str:
        """
        read the result of a command issued to the module
        :param num_of_bytes: almost always empty
        :return: a string with the ezo module response
        """
        # trim all trailing zeroes
        response = self.file_read.read(num_of_bytes)
        while response[0] == 254:
            sleep(0.1)
            response = self.file_read.read(num_of_bytes)
        response_code = int(response[0]) if (len(response) > 0) else 0
        return AtlasEzo._join(response[1:].rstrip(bytes([0]))) if (response_code == 1) else AtlasEzo._get_error(response_code)

    @abstractmethod
    def _get_command_timeout(self, command: str) -> float:
        """
        command timeouts are dependent on the module, so we expect this method to be overridden
        """
        pass

    def query(self, command: str, timeout: float = 0.0) -> str:
        """
        write a command to the board, wait the correct timeout,
        and read the response
        """
        self.write(command)
        # add a little slop to the timeout
        sleep(timeout if (timeout > 0.0) else self._get_command_timeout(command.split(',')[0].upper()))
        return self.read()

    def query_float(self, command: str, value_on_error: float, timeout: float = 0.0) -> float:
        response = self.query(command, timeout)
        try:
            return float(response)
        except ValueError:
            print(f"response (query_float): {response}")
            return value_on_error

    def query_int(self, command: str, value_on_error: int, timeout: float = 0.0) -> int:
        response = self.query(command, timeout)
        try:
            return int(response)
        except ValueError:
            print(f"response (query_int): {response}")
            return value_on_error

    def report_stable_value(self, n: int = 30):
        samples = []
        for _ in itertools.repeat(None, n):
            sample = self.query_float("R", 0.0)
            samples.append(sample)
            print(f"sample: {sample:.3f}")
            sleep(1)
        print(f"stdev: {stdev(samples):.3f}, samples: {n}")

    @abstractmethod
    def wait_for_stable_value(self):
        pass

    def _wait_for_stable_value(self, tolerance: float, n: int = 30) -> None:
        # all ezo modules support "R" commands to just read a value. we simply want to read at one
        # second intervals until the variance in the last n samples drops below some standard
        # the actual intervals will be 1 second plus the query time, so probably closer to 2 seconds
        samples = []
        for _ in itertools.repeat(None, n):
            sample = self.query_float("R", 0.0)
            samples.append(sample)
            print(f"sample: {sample:.3f}")
            sleep(1)
        sd = stdev(samples)
        print(f"stdev: {sd:.3f}, samples: {n}, tolerance: {tolerance:.3f}")
        while sd > tolerance:
            sample = self.query_float("R", 0.0)
            samples.append(sample)
            samples = samples[-n:]
            sd = stdev(samples)
            print(f"sample: {sample:.3f}, stdev: {sd:.3f}, tolerance: {tolerance:.3f}")
            sleep(1)

    @property
    @abstractmethod
    def calibration_type(self) -> int:
        pass

    def close(self) -> None:
        self.file_read.close()
        self.file_write.close()
