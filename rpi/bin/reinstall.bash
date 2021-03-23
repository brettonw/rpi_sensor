#! /usr/bin/env bash

# get the path where we are executing from
executingDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# configure a sensor
existing="";
workingPath="/home/brettonw/bin";
sensorFile="$workingPath/sensor.py";
if [ -e "$sensorFile" ]; then
  existing=$(ls -l "$sensorFile" | sed -e "s/^.*-> //");
  existing=$(basename "$existing" | sed -e "s/sensor-//" | sed -e "s/.py$//");
  rm -f "$sensorFile";
  echo "Removed existing sensor configuration ($existing).";
fi

. $executingDir/install.bash $existing;
