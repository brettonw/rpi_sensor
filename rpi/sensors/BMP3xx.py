#! /usr/bin/env python3

import board
from adafruit_bmp3xx import BMP3XX_I2C
from statistics import mean, stdev
from time import sleep

# 5 samples
minSamples = 5
sampleList = []
sensor = BMP3XX_I2C (board.I2C())
while (len(sampleList) < minSamples):
    sampleList.append({ "temperature": sensor.temperature, "pressure": sensor.pressure})
    sleep (0.1)

# split the samples out into tuples that can be used in statistics
temperatures = tuple (i["temperature"] for i in sampleList)
pressures = tuple (i["pressure"] for i in sampleList)

# output the result
print("\"temperature\": {:5.3f}, \"temperature-unit\": \"°C\", \"temperature-stdev\": {:5.3f}, \"pressure\": {:5.3f}, \"pressure-unit\": \"hPa\", \"pressure-stdev\": {:5.3f}"
      .format(mean (temperatures), stdev (temperatures), mean (pressures), stdev(pressures))
      )
