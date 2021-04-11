#! /usr/local/bin/python3

from bedrock.bedrock import Bedrock

def handleOk (query):
    return { "OK": "OK" }

Bedrock.handleRequest()

