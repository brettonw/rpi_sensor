#! /usr/bin/env bash

# define a logging function
echoerr() { echo "$@" 1>&2; }

# setup the log file, dropped directly in the web server path
sensorDir="/var/www/html/sensor";
jsonNowFile="$sensorDir/now.json";
controlsFile="$sensorDir/controls.json";

# setup the script start time and the counter
startTimestamp=$(date +%s%3N);
counter=0;

while :
do
    # get the sensor with the timestamp and write it to the raw log
    # source data is like (note that not all sensors sense all values, and will
    # set the value to "-" to indicate "no information"):
    # temperature/relative humidity/pressure
    timestamp=$(date +%s%3N);
    sensorRead=$(/home/brettonw/bin/sensor.py | sed -e "s/^ *$//");
    if [ ! -z "$sensorRead" ]; then
        # start with the time stamp
        sensorOutput="{ \"timestamp\": $timestamp";

        # include the sensor read
        sensorOutput="$sensorOutput, $sensorRead";

        # accumulate controls if there are any
        if [ -f $controlsFile ]; then
          controls=$(<$controlsFile);
          sensorOutput="$sensorOutput, \"control\": $controls";
        fi

        # include cpu load, note mpstat responds to its own locale (probably www user), which makes
        # the time output different than a normal user - will need to verify across platforms
        # NOTE - SET THE LOCALE ON THE RUNNING MACHINE TO... C.UTF-8 (not EN)
        cpu_load=$(mpstat | tail -1 | awk '{split($0,a," "); print "\"usr\":" a[3] ", \"sys\":" a[5] ", \"idle\":" a[12]}');
        sensorOutput="$sensorOutput, \"cpu-load\": { $cpu_load }, \"cpu-load-unit\": \"%\"";

        # include cpu temperature
        cpu_temperature=$(sed 's/.\{3\}$/.&/' <<< "$(</sys/class/thermal/thermal_zone0/temp)");
        sensorOutput="$sensorOutput, \"cpu-temperature\": $cpu_temperature, \"cpu-temperature-unit\": \"°C\"";

        # include memory and swap
        memory=$(free -bw | tail -2 | head -1 | awk '{split($0,a," "); print "\"total\":" a[2] ", \"used\":" a[3] ", \"free\":" a[4] ", \"shared\":" a[5] ", \"buffers\":" a[6] ", \"cache\":" a[7] ", \"available\":" a[8]}');
        sensorOutput="$sensorOutput, \"memory\": { $memory }, \"memory-unit\": \"kB\"";
        swap=$(free -bw | tail -1 | awk '{split($0,a," "); print "\"total\":" a[2] ", \"used\":" a[3] ", \"free\":" a[4]}');
        sensorOutput="$sensorOutput, \"swap\": { $swap }, \"swap-unit\": \"kB\"";

        # close the bag
        sensorOutput="$sensorOutput }";

        # emit the results
        echo "$sensorOutput" > $jsonNowFile;

        # increment the counter
        counter=$(( counter + 1 ));
    fi

    # sleep for a little bit (making the whole loop land on 10 second intervals)
    # XXX might be nice to make it reliably 10 second intervals that are aligned to the clock minute
    targetTimestamp=$(( startTimestamp+(counter*10000) ));
    nowTimestamp=$(date +%s%3N);
    delta=$(( (targetTimestamp-nowTimestamp)/1000 ));
    if [ $delta -gt 0 ]; then
      #echoerr "sleeping for $delta seconds";
      sleep $delta;
    else
      echoerr "PROBLEM: not sleeping ($delta ms)";
    fi;
done
