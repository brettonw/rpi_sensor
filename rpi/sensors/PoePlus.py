#! /usr/bin/env python3

import subprocess
from statistics import mean, stdev
from time import sleep


def get_value(command: str, value_on_error: int | float = None) -> int | float | None:
    # run the command and capture the output
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    return float(result.stdout.strip()) if result.returncode == 0 else value_on_error

# Example usage
#command_output = execute_command("echo Hello, World!")
#print(command_output)


# get the current fan speed
fan_speed: int = get_value("cat /sys/class/thermal/cooling_device0/cur_state", -1)

# get 5 samples of the µA measurement, converting to A
samples = []
def get_sample():
    sample = get_value("cat /sys/devices/platform/rpi-poe-power-supply/power_supply/rpi-poe/current_now") / 1000000
    if sample is not None:
        samples.append(sample)
get_sample()
for i in range(5):
    sleep(0.1)
    get_sample()

# output the result
print(f"\"fan_speed\": {fan_speed}, \"fan_speed-unit\": \"\", \"current\": {mean(samples):5.3f}, \"current-unit\": \"A\", \"current-stdev\": {stdev(samples):5.3f}")
