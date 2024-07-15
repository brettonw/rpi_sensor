#! /usr/bin/env python3

import subprocess
from statistics import mean, stdev
from time import sleep


def get_raw_value(command: str) -> str | None:
    # run the command and capture the output
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    return result.stdout.strip() if result.returncode == 0 else None

def get_int_value(command: str, value_on_error: int | None = None) -> int | None:
    result = get_raw_value(command)
    return int(result) if result is not None else value_on_error

def get_float_value(command: str, value_on_error: int | None = None) -> int | None:
    result = get_raw_value(command)
    return float(result) if result is not None else value_on_error

# Example usage
#command_output = execute_command("echo Hello, World!")
#print(command_output)


# get the current fan speed
fan_speed = get_int_value("cat /sys/class/thermal/cooling_device0/cur_state", -1)

# get 5 samples of the µA measurement, converting to A
samples = []
def get_sample():
    sample = get_float_value("cat /sys/devices/platform/rpi-poe-power-supply/power_supply/rpi-poe/current_now")
    if sample is not None:
        samples.append(sample / 1000000.0)
get_sample()
for i in range(4):
    sleep(0.1)
    get_sample()

# output the result
print(f"\"fan_speed\": {fan_speed}, \"fan_speed-unit\": \"\", \"current\": {mean(samples):5.3f}, \"current-unit\": \"A\", \"current-stdev\": {stdev(samples):5.3f}")
