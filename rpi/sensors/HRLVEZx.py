#! /usr/bin/env python3

from time import time
from time import sleep
from serial import Serial

# data from the Maxbotics sensor comes through serial as a stream of constant
# size, 6 bytes each "R0000\r". We want to wait until we have at least 11
# characters, as we'll be guaranteed to have a full sequence.
# once we have a read, find the first R, then use that offset to find the index
# of the last R in the buffer with a full read in it, and extract the four
# digits right after that as the distance in mm
def measure():
    ser = Serial("/dev/serial0", 9600, 8, 'N', 1, timeout=1)
    timeOut = 0.5
    result = -1
    guaranteedRead = 11
    fullReadSize = 6
    digitsReadSize = 4
    timeStart = time()
    while time() < timeStart + timeOut:
        bytesToRead = ser.inWaiting()
        if bytesToRead >= guaranteedRead:
            readBytes = ser.read(bytesToRead)
            print ("READ: {} bytes = {}".format (bytesToRead, readBytes))
            rIndex = readBytes.find (b'R')
            print ("  rIndex: {}".format (rIndex))
            fullReadCount = int ((len (readBytes) - rIndex) / fullReadSize) - 1
            print ("  fullReadCount: {}".format (fullReadCount))
            readIndex = rIndex + (fullReadCount * fullReadSize) + 1
            readEnd = readIndex + digitsReadSize
            print ("  slice from {} to {}: {}".format (readIndex, readEnd, readBytes[readIndex:readEnd]))
            while readBytes[readIndex] == '0':
                readIndex += 1
            readSlice = readBytes[readIndex:readEnd]
            result = int (readSlice)
            print (" {} parses as {}".format (readSlice, result))
            break
    ser.close()
    return result

while True:
    measure()
    sleep (0.05)


