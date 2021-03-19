#! /usr/bin/env python3

import board
from adafruit_bmp3xx import BMP3XX_I2C
from statistics import mean, variance

# 5 samples
minSamples = 5
sampleList = []
i2c = board.I2C()
while (len(sampleList) < minSamples):
    sampleList.append(BMP3XX_I2C (i2c))

# split the samples out into tuples that can be used in statistics
temperatures = tuple (i.temperature for i in sampleList)
pressures = tuple (i.pressure for i in sampleList)

# output the result
print("\"temperature\": {:5.3f}, \"temperature-unit\": \"C\", \"temperature-variance\": {:5.3f}, \"pressure\": {:5.3f}, \"pressure-unit\": \"hPa\", \"pressure-variance\": {:5.3f}"
      .format(mean (temperatures), variance (temperatures), mean (pressures), variance(pressures))
)

