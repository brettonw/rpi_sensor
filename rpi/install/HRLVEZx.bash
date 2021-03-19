#! /usr/bin/env bash

sudo pip3 install pyserial;

# enable the UART

# add to /boot/config.txt
CONFIG="/boot/config.txt";

# enable_uart=1
sed -i -e "s/.*enable_uart=.*/enable_uart=1/" "$CONFIG";
UART_ENABLE=$(grep "enable_uart=1" "$CONFIG");
if [ -z "$UART_ENABLE" ]; then
    echo "enable_uart=1" >> "$CONFIG";
fi;

# dtoverlay=pi3-miniuart-bt
sed -i -e "s/.*dtoverlay=pi3.*bt/dtoverlay=pi3-miniuart-bt/" "$CONFIG";
UART_OVERLAY=$(grep "dtoverlay=pi3-miniuart-bt" "$CONFIG");
if [ -z "$UART_OVERLAY" ]; then
    echo "dtoverlay=pi3-miniuart-bt" >> "$CONFIG";
fi;


# update cmd line
CMDLINE="/boot/cmdline.txt";
sed -i $CMDLINE -e "s/console=ttyAMA0,[0-9]\+ //";
sed -i $CMDLINE -e "s/console=serial0,[0-9]\+ //";
