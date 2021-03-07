#! /usr/bin/env bash

# create the "sensor" user
user="brettonw";
homePath="/home/$user";

# configure the target dir for the "api"
sensorDir="/var/www/html/sensor";
sudo rm -rf "$sensorDir";
if [ ! -d "$sensorDir" ]; then
  sudo mkdir "$sensorDir";
  sudo chown $user:$user "$sensorDir";
  chmod ugo+r "$sensorDir";
  echo "Created sensor dir ($sensorDir).";
fi

# configure a sensor
binPath="$homePath/bin";
configuredSensorFile="$binPath/sensor.py";
if [ ! -e "$configuredSensorFile" ]; then
  installPath="$homePath/install";
  sensorPath="$homePath/sensor";

  echo "No sensor is configured. The choices are:";
  find "$sensorPath" -printf '    %P\n' | sed -e "s/.py$//";
  read -p "Which sensor would you like to use? " sensorName;

  targetInstall="$installPath/$sensorName.bash";
  if [ -e "$targetInstall" ]; then
    $($targetInstall);
  fi

  targetSensor="$sensorPath/$sensorName.py";
  if [ -e "$targetSensor" ]; then
    ln -s "$targetSensor" "$configuredSensorFile";
  fi
fi

if [ -e "$configuredSensorFile" ]; then
  existing=$(ls -l "$configuredSensorFile" | sed -e "s/^.*-> //");
  existing=$(basename "$existing" | sed -e "s/.py$//");
  echo "Configured for sensor ($existing).";
  # copy the service file to the lib directory and start it
  serviceName="get-sensor.service";
  echo "Installing service \"$serviceName\"...";
  sudo systemctl stop "$serviceName";
  sudo cp "$binPath/$serviceName" "/lib/systemd/system/"
  sudo systemctl enable "$serviceName";
  sudo systemctl start "$serviceName";
fi
echo "Done.";
