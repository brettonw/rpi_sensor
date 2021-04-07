#! /usr/bin/env python3

import subprocess

# helper to print each field we care about
separator = ""
def printKeyValuePair (key, value):
    global separator
    print ("{}\"{}\":{}".format (separator, key, value), end='')
    separator = ","

# from apcupsd cource, statflag values are:
#define UPS_calibration   0x00000001
#define UPS_trim          0x00000002
#define UPS_boost         0x00000004
#define UPS_online        0x00000008
#define UPS_onbatt        0x00000010
#define UPS_overload      0x00000020
#define UPS_battlow       0x00000040
#define UPS_replacebatt   0x00000080
flagValues = [ "CALIBRATION", "TRIM", "BOOST", "ONLINE", "ONBATTERY", "OVERLOAD", "BATTERY_LOW", "REPLACE_BATTERY" ]

# get the apcups status and report the values we want
wanted = { "LINEV", "LOADPCT", "BCHARGE", "TIMELEFT" }
for line in subprocess.run(['/usr/sbin/apcaccess'], capture_output=True, text=True).stdout.splitlines():
    kv = [items.rstrip () for items in line.split (": ", 1)]
    if (kv[0] == "STATFLAG"):
        # flags are reported as a hexadecimal number. we convert each flag to a 0 or 1 for output, but
        # we only care about the last 5
        flags = int (kv[1], 16)
        for flagIndex, flagName in enumerate(flagValues):
            if (flagIndex >= 3):
                printKeyValuePair (flagName, int ((flags & (2 ** flagIndex)) > 0))
    else:
        if (kv[0] in wanted):
            printKeyValuePair (kv[0], "\"{}\"".format (kv[1]))
