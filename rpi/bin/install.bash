#! /usr/bin/env bash

# install the sysstat library needed by the sensor at runtime
sudo apt install -y sysstat apache2;

# set the locale to what we need for sysstat
echo "LANG=C.UTF-8" | sudo tee /etc/default/locale;

# get the path where we are executing from
executingDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

sensorName="";
if [ "$#" -gt 0 ]; then
    sensorName="$1";
fi

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

  # put the status.png file in place
  sudo cp "$executingDir/../img/status.png" "/var/www/html/";
fi

# configure a sensor
binPath="$homePath/bin";
mkdir -p $binPath;
configuredSensorFile="$binPath/sensor.py";
while [ ! -e "$configuredSensorFile" ]; do
    installPath="$executingDir/../install";
    sensorPath="$executingDir/../sensors";

    # look to see if a sensor was already requested on the command line
    if [ -z "$sensorName" ]; then
        echo "No sensor is configured. The choices are:";
        find "$sensorPath" -type f -printf '    %P\n' | sed -e "s/.py$//";
        read -p "Which sensor would you like to use? " sensorName;
    fi

    targetInstall="$installPath/$sensorName.bash";
    if [ -e "$targetInstall" ]; then
        echo "Installing support for $sensorName (this might take a little while)...";
        sudo "$targetInstall";
    fi

    targetSensor="$sensorPath/$sensorName.py";
    if [ -e "$targetSensor" ]; then
        echo "Linking $sensorName";
        ln -sf "$targetSensor" "$configuredSensorFile";
    fi
    sensorName="";
done

# configure the service
existing=$(ls -l "$configuredSensorFile" | sed -e "s/^.*-> //");
existing=$(basename "$existing" | sed -e "s/.py$//");
echo "Configured for sensor ($existing).";
# copy the service file to the lib directory and start it
serviceName="get-sensor.service";
echo "Installing service \"$serviceName\"...";
sudo systemctl stop "$serviceName";
ln -sf "$executingDir/get-sensor.bash" "$binPath/get-sensor.bash";
sudo cp "$executingDir/$serviceName" "/lib/systemd/system/"
sudo systemctl enable "$serviceName";
sudo systemctl start "$serviceName";
echo "Done.";

# reboot the raspberry pi
sudo reboot now;
