#! /usr/bin/env python3

import board
from adafruit_hts221 import HTS221
from statistics import mean, stdev
from time import sleep

# 5 samples
minSamples = 5
sampleList = []
i2c = board.I2C()
while (len(sampleList) < minSamples):
    sampleList.append(HTS221 (i2c))
    sleep (0.25)

# split the samples out into tuples that can be used in statistics
temperatures = tuple (i.temperature for i in sampleList)
humidities = tuple (i.relative_humidity for i in sampleList)

# output the result
print("\"temperature\": {:5.3f}, \"temperature-unit\": \"C\", \"temperature-stdev\": {:5.3f}, \"humidity\": {:5.3f}, \"humidity-unit\": \"%\", \"humidity-stdev\": {:5.3f}"
      .format(mean (temperatures), stdev (temperatures), mean (humidities), stdev(humidities))
      )

