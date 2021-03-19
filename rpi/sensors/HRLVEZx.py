#! /usr/bin/env python3

from time import time
from time import sleep
from serial import Serial

noValue = 0
minValue = 300

# data from the Maxbotics sensor comes through serial as a stream of constant
# size, 6 bytes each "R0000\r". We want to wait until we have at least 11
# characters, as we'll be guaranteed to have a full sequence in case we jumped
# in at the second character. once we have a read, find the first R, then use
# that offset to find the index of the last R in the buffer with a full read in
# it, and extract the four digits right after that as the distance in mm
def measure():
    ser = Serial("/dev/serial0", 9600, 8, 'N', 1, timeout=1)
    timeOut = 1
    timeStart = time()
    endTime = timeStart + timeOut

    # eat any existing data in the serial pipe
    while time() < endTime:
        bytesToRead = ser.inWaiting()
        if bytesToRead > 0:
            ser.read(bytesToRead)
        else:
            break

    # now try to get a measurement
    result = noValue
    guaranteedRead = 11
    fullReadSize = 6
    digitsReadSize = 4
    while time() < endTime:
        bytesToRead = ser.inWaiting()
        if bytesToRead >= guaranteedRead:
            readBytes = ser.read(bytesToRead)
            rIndex = readBytes.find (b'R')
            fullReadCount = int ((len (readBytes) - rIndex) / fullReadSize) - 1
            readIndex = rIndex + (fullReadCount * fullReadSize) + 1
            readEnd = readIndex + digitsReadSize
            while readBytes[readIndex] == b'0'[0]:
                readIndex += 1
            readSlice = readBytes[readIndex:readEnd]
            result = int (readSlice)
            break
    ser.close()
    return result

sampleList = []
def mean():
    return sum(sampleList) / len(sampleList)

def variance():
    expected = mean ()
    return sum((i - expected) ** 2 for i in sampleList) / len(sampleList)

# gather samples until the variance is below a threshold
minSamples = 3
maxVariance = 5
print ("Start")
while (len(sampleList) < minSamples) or (variance() > maxVariance):
    sample = measure()
    if (sample >= minValue):
        sampleList.append(sample)
        print ("  sample: {:5.3f}, count: {}, mean: {:5.3f}, variance: {5.3f}".format(sample, len (sampleList), mean (), variance ()))
    else:
        print ("  reject: {:5.3f}".format (sample))
print("\"distance\": {:5.3f}, \"distance-unit\": \"mm\"".format(mean ()))


