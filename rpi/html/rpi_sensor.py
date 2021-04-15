#! /usr/local/bin/python3

from bedrock_cgi import ServiceBase
import subprocess
import json

def handleOk (event):
    line = subprocess.run(['/home/brettonw/bin/sensor.py'], capture_output=True, text=True).stdout
    out = "{{{}}}".format (line.strip())
    sensor = json.loads(out)
    event.ok (sensor)

ServiceBase.respond()
