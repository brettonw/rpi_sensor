#! /usr/bin/env python3

import board
from adafruit_sht31d import SHT31D
from statistics import mean, stdev
from time import sleep

# 5 samples
minSamples = 5
sampleList = []
sensor = SHT31D (board.I2C())
while (len(sampleList) < minSamples):
    sampleList.append({ "temperature": sensor.temperature, "humidity": sensor.relative_humidity})
    sleep (0.1)

# split the samples out into tuples that can be used in statistics
temperatures = tuple (i["temperature"] for i in sampleList)
relative_humidities = tuple (i["humidity"] for i in sampleList)

# output the result
print("\"temperature\": {:5.3f}, \"temperature-unit\": \"°C\", \"temperature-stdev\": {:5.3f}, \"humidity\": {:5.3f}, \"humidity-unit\": \"%\", \"humidity-stdev\": {:5.3f}"
      .format(mean (temperatures), stdev (temperatures), mean (relative_humidities), stdev(relative_humidities))
      )
