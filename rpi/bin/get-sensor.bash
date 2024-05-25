#! /usr/bin/env bash

# define a logging function
echoerr() { echo "$@" 1>&2; }

# setup the log file, dropped directly in the web server path
sensorDir="/var/www/html/sensor";
rawHistoryFile="$sensorDir/history.raw";
jsonHistoryFile="$sensorDir/history.json";
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
        sensorOutput="{ \"timestamp\": $timestamp, $sensorRead";

        # accumulate controls if there are any
        if [ -f $controlsFile ]; then
          controls=$(<$controlsFile);
          sensorOutput="$sensorOutput, \"controls\": $controls";
        fi

        # include cpu temperature
        cpu_temperature=$(</sys/class/thermal/thermal_zone0/temp)
        sensorOutput="$sensorOutput, \"cpu-temperature\": $((cpu_temperature/1000)), \"cpu-temperature-unit\": \"C\"";

        # include memory
        memory=$(free -b | tail -2 | tr '\n' ' ' | awk '{split($0,a," "); print "\"mem-total\":" a[2] ", \"mem-used\":" a[3] ", \"mem-free\":" a[4] ", \"swap-total\":" a[9] ", \"swap-used\":" a[10] ", \"swap-free\":" a[11]}');
        sensorOutput="$sensorOutput, \"memory\": \{ $memory \}, \"memory-unit\": \"kB\"";

        # close the bag
        sensorOutput="$sensorOutput }";

        # emit the results
        echo "    , $sensorOutput" >> $rawHistoryFile;
        echo "$sensorOutput" > $jsonNowFile;

        # increment the counter, then once per minute consolidate the JSON output
        counter=$(( counter + 1 ));
        modulo=$(( counter % 6));
        if [ $modulo -eq 0 ]; then
            # limit the log output to 10K, about 1 day at every 10 seconds
            tail --lines 10K $rawHistoryFile > "$rawHistoryFile.tmp";
            mv "$rawHistoryFile.tmp" $rawHistoryFile;

            # concat everything into the JSON log, this is a bit ugly
            echo "[" > $jsonHistoryFile;
            echo "      { \"timestamp\": 0 }" >> $jsonHistoryFile;
            cat $rawHistoryFile >> $jsonHistoryFile;
            echo "]" >> $jsonHistoryFile;
        fi
    fi

    # sleep for a little bit (making the whole loop land on 10 second intervals)
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
