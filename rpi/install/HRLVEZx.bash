#! /usr/bin/env bash

sudo pip3 install pyserial;

# enable the UART

# add to /boot/config.txt
enable_uart=1
dtoverlay=pi3-miniuart-bt

# update cmd line
CMDLINE=/boot/cmdline.txt
sed -i $CMDLINE -e "s/console=ttyAMA0,[0-9]\+ //";
sed -i $CMDLINE -e "s/console=serial0,[0-9]\+ //";
