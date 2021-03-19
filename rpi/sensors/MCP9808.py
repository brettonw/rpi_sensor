#! /usr/bin/env python3

import board
from adafruit_mcp9808 import MCP9808
from statistics import mean, variance

# 5 samples
minSamples = 5
sampleList = []
i2c = board.I2C()
while (len(sampleList) < minSamples):
    sampleList.append(MCP9808 (i2c))

# split the samples out into tuples that can be used in statistics
temperatures = tuple ((i.temperature) ** 2 for i in sampleList)

# output the result
print("\"temperature\": {:5.3f}, \"temperature-unit\": \"C\", \"temperature-variance\": {:5.3f}"
      .format(mean (temperatures), variance (temperatures))
      )

