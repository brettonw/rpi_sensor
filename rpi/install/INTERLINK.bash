#! /usr/bin/env bash

# get the path where we are executing from
EXECUTING_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# enable i2c and install the driver
. $EXECUTING_DIR/../bin/install-i2c.bash;

echo "copying dependencies";
cp $EXECUTING_DIR/../dependencies/AtlasI2C.py /home/brettonw/bin/;
