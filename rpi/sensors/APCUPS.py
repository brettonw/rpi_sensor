#! /usr/bin/env python3

import subprocess

# helper to print each field we care about
separator = ""
def printKeyValuePair (key, value):
    global separator
    print ("{}\"{}\":{}".format (separator, key, value), end='')
    separator = ","

# the key names we want to report with
reportNames = {
    "LINEV"    : "line/ Volts",
    "LOADPCT"  : "load/ Percent",
    "BCHARGE"  : "battery/ Percent",
    "TIMELEFT" : "remaining/ Minutes"
}

# format a key value pair from the non-flag section of the report
def printWantedKeyValuePair (key, value):
    if (key in reportNames):
        reportName = reportNames[key]
        key, unit = reportName.split ("/",1)
        value = "{:3.1f}".format (float (value.replace(unit, "")))
        printKeyValuePair(key, value)

# yes no array
yesno = ["\"no\"", "\"yes\""]

# from apcupsd source, statflag values we care about are:
UPS_online = 0x00000008
UPS_replacebatt = 0x00000080

# get the apcups status and report the values we want
for line in subprocess.run(['/usr/sbin/apcaccess'], capture_output=True, text=True).stdout.splitlines():
    kv = [items.rstrip () for items in line.split (": ", 1)]
    if (kv[0] == "STATFLAG"):
        # flags are reported as a hexadecimal number string. we make that into an int
        flags = int (kv[1], 16)
        printKeyValuePair ("online", yesno[int ((flags & UPS_online) > 0)])
        printKeyValuePair ("replace", yesno[int ((flags & UPS_replacebatt) > 0)])
    else:
        printWantedKeyValuePair (kv[0], kv[1])
print ()
