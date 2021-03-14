#! /usr/bin/env bash

pip3 install adafruit-python-shell;
pip3 install adafruit-blinka;

# enable i2c
SETTING=on
STATUS=enabled
set_config_var dtparam=i2c_arm $SETTING $CONFIG &&
sed /etc/modules -i -e "s/^#[[:space:]]*\(i2c[-_]dev\)/\1/"
if ! grep -q "^i2c[-_]dev" /etc/modules; then
printf "i2c-dev\n" >> /etc/modules
fi
dtparam i2c_arm=$SETTING
modprobe i2c-dev
