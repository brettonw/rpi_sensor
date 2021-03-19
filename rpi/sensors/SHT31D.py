#! /usr/bin/env python3

import board
from adafruit_sht31d import SHT31D
from statistics import mean, variance

# 5 samples
minSamples = 5
sampleList = []
i2c = board.I2C()
while (len(sampleList) < minSamples):
    sampleList.append(SHT31D (i2c))

# split the samples out into tuples that can be used in statistics
temperatures = tuple (i.temperature for i in sampleList)
humidities = tuple (i.relative_humidity for i in sampleList)

# output the result
print("\"temperature\": {:5.3f}, \"temperature-unit\": \"C\", \"temperature-variance\": {:5.3f}, \"humidity\": {:5.3f}, \"humidity-unit\": \"%\", \"humidity-variance\": {:5.3f}"
      .format(mean (temperatures), variance (temperatures), mean (humidities), variance(humidities))
      )

