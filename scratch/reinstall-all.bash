#!/usr/bin/env bash

my_array=("rpi-sensor-garage" "rpi-sensor-bedroom" "rpi-sensor-guest-room" "rpiaqm", "rpi-zwave", "homesvcs", "rpi2", "rpi4", "rpi5", "rpi6")

COMMAND="cd rpi_sensor && git pull && rpi/bin/reinstall.bash;";

# Iterate over the array
for element in "${my_array[@]}"
do
    echo "Processing: $element"
    ssh $element.local "$COMMAND";
done
