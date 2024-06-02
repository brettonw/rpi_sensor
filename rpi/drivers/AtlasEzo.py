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
    @abstractmethod
    def value(self) -> Union[float, int]:
        pass

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
            print(f"Assertion Failure: ({left}) != ({right})")
            raise AssertionError

    def _write(self, cmd: str) -> None:
        # we gate requests to the device to one per second, so compute how long it's been since the
        # last request and sleep to make it so
        now = time()
        delta = now - self._last_write_time
        if delta < 1.0:
            sleep(1.0 - delta)
        self._last_write_time = time()

        # appends the null character and sends the string over i2c
        cmd += "\00"
        self.file_write.write(cmd.encode('latin-1'))

    @staticmethod
    def _join(response: bytes) -> str:
        """
        this function is called when there is a success, to format the response bytes - for
        functions that don't actually have a response value, we substitute "OK"
        """
        # per Atlas Scientific, a glitch in the raspberry pi requires us to change the MSB to 0 for
        # all received characters
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
            2: "syntax error",
            0: "no response"
        }.get(error_code, "UNKNOWN")

    def _read(self, num_of_bytes: int = 31) -> str:
        """
        read the result of a command issued to the module
        :param num_of_bytes: almost always empty
        :return: a string with the ezo module response
        """
        # all commands require some amount of delay before the read-back, all ezo modules use 0.3 as
        # the multiple, 0.3, 0.6, 0.9... to minimize traffic, we start with this
        READ_DELAY = 0.3

        def listen() -> (bytes, int):
            sleep(READ_DELAY)
            response = self.file_read.read(num_of_bytes)
            return response, int(response[0]) if (len(response) > 0) else 0

        response, response_code = listen()
        while response_code == 254:
            response, response_code = listen()

        # if the response is valid, strip trailing nulls and convert to a string, otherwise embed
        # the error in the response
        return AtlasEzo._join(response[1:].rstrip(bytes([0]))) if (response_code == 1) else AtlasEzo._get_error(response_code)

    def query(self, command: str) -> str:
        """
        write a command to the ezo device and read the response
        """
        self._write(command)
        return self._read()

    def query_float(self, command: str, value_on_error: float) -> float:
        response = self.query(command)
        try:
            return float(response)
        except ValueError:
            print(f"response (query_float): {response}")
            return value_on_error

    def query_int(self, command: str, value_on_error: int) -> int:
        response = self.query(command)
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
            sd = f"{stdev(samples): 3.03f}" if len(samples) > 1 else "n/a"
            print(f"sample: {sample: 5.03f}, stdev: {sd}, samples: {len(samples)}")

        print(f"stdev: {stdev(samples):.03f}, samples: {n}")

    @abstractmethod
    def wait_for_stable_value(self):
        pass

    def _wait_for_stable_value(self, tolerance: float, n_max: int = 30, n_min: int = 10) -> None:
        # all ezo modules support "R" commands to just read a value. we simply want to read at one
        # second intervals until the variance in the last n samples drops below some standard
        # the actual intervals will be 1 second plus the query time, so probably closer to 2 seconds
        samples = []

        def collect_sample() -> float:
            sample = self.query_float("R", 0.0)
            nonlocal samples
            samples.append(sample)
            samples = samples[-n_max:]
            sd = stdev(samples) if len(samples) > 1 else tolerance + 1
            sds = f"{sd:.03f}" if len(samples) > 1 else "n/a"
            print(f"sample: {sample: 5.03f}, stdev: {sds}, samples: {len(samples): 3d}, tolerance: {tolerance:.03f}")
            return sd

        sample = collect_sample()
        while (len(samples) < n_min) or (sample > tolerance):
            sample = collect_sample()

    @property
    @abstractmethod
    def calibration_type(self) -> int:
        pass

    def close(self) -> None:
        self.file_read.close()
        self.file_write.close()
