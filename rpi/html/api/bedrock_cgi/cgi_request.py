import io
import os
import sys
import json
from .constant import false, MIME_TYPE_JSON, CHARSET, CHARSET_UTF8
from .cgi_response import respond, STATUS_BAD_REQUEST

# cgi request header environment variables and values
CONTENT_LENGTH = "CONTENT_LENGTH"
CONTENT_TYPE = "CONTENT_TYPE"

class CgiRequest:

    @staticmethod
    def __isJson ():
        contentType = os.environ.get(CONTENT_TYPE, None)
        if (contentType != None):
            return contentType.split (";", 1)[0].strip () == MIME_TYPE_JSON
        return false

    @staticmethod
    def __charset ():
        contentType = os.environ.get(CONTENT_TYPE, None)
        if (contentType != None):
            splitResult = contentType.split(";", 1)
            if (len (splitResult) == 2):
                parameters = {}
                for parameter in splitResult[1].split (";"):
                    attribute, parameters[attribute] = parameter.split ("=")
                if (CHARSET in parameters):
                    # technically the attribute value could be a quoted string that we should parse...
                    return str(parameters[CHARSET]).strip (" '\"\t\r\n")
        # assume UTF-8 if no charset is passed, not technically correct according to standards, but for
        # most characters we encounter here will be the same as ASCII or ISO-8859-1 (Western Latin 1)
        return CHARSET_UTF8

    @staticmethod
    def getQuery ():
        # the type must be JSON
        if CgiRequest.__isJson():
            # the length must be specified
            contentLength = int (os.environ.get(CONTENT_LENGTH, 0))
            if (contentLength > 0):
                inputStream = io.TextIOWrapper(sys.stdin.buffer, encoding=CgiRequest.__charset ())
                inputJson = inputStream.read(contentLength)
                return json.loads(inputJson)
        # this is just a base error - if we couldn't get a workable request
        respond (STATUS_BAD_REQUEST, "Bad Request ({} must be {}, and {} > 0)".format (CONTENT_TYPE, MIME_TYPE_JSON, CONTENT_LENGTH))
