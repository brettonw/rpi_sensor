#! /usr/local/bin/python3

from bedrock_cgi.service_base import ServiceBase

def handleOk (event):
    event.ok ({ "OK": "OK" })

ServiceBase.respond()

