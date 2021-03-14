#! /usr/bin/env bash

# get the path where we are executing from
EXECUTING_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# enable i2c and install the driver
. $EXECUTING_DIR/../bin/install-i2c.bash
pip3 install adafruit-circuitpython-bmp3xx;

