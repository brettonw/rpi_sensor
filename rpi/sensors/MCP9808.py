#! /usr/bin/env python3

import board
from adafruit_mcp9808 import MCP9808
from statistics import mean, stdev
from time import sleep

# 5 samples
minSamples = 5
sampleList = []
sensor = MCP9808 (board.I2C())
while (len(sampleList) < minSamples):
    sampleList.append({ "temperature": sensor.temperature () })
    sleep (0.1)

# split the samples out into tuples that can be used in statistics
temperatures = tuple (i.temperature for i in sampleList)

# output the result
print("\"temperature\": {:5.3f}, \"temperature-unit\": \"C\", \"temperature-stdev\": {:5.3f}"
      .format(mean (temperatures), stdev (temperatures))
      )

