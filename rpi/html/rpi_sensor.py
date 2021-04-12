#! /usr/local/bin/python3

from bedrock_cgi import ServiceBase

def handleOk (event):
    event.ok ({ "OK": "OK" })

ServiceBase.respond()
