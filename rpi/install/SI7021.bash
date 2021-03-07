#! /usr/bin/env bash

sudo pip3 install adafruit-python-shell;
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py;
sudo python3 raspi-blinka.py;
rm -f raspi-blinka.py;
sudo pip3 install adafruit-circuitpython-si7021;

