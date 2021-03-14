#! /usr/bin/env bash

pip3 install adafruit-python-shell;
pip3 install adafruit-blinka;

# enable i2c - code loosely based on raspi-config
echo "Enabling I2C";
CONFIG="/boot/config.txt";
MODULES="/etc/modules";

sed -i -e "s/.*dtparam=i2c_arm=.*/dtparam=i2c_arm=on/" "$CONFIG";
I2C_CONFIG=$(grep "dtparam=i2c_arm" "$CONFIG");
if [ -z "$I2C_CONFIG" ]; then
    echo "dtparam=i2c_arm=on" >> "$CONFIG";
fi;

sed -i -e "s/^#[[:space:]]*\(i2c[-_]dev\)/\1/" "$MODULES";
if ! grep -q "^i2c[-_]dev" "$MODULES"; then
printf "i2c-dev\n" >> "$MODULES"
fi
dtparam i2c_arm=on
modprobe i2c-dev
