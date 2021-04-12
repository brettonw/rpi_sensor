import sys
from .constant import MIME_TYPE_JSON, CHARSET, CHARSET_UTF8

# cgi response headers
HEADER_STATUS = "STATUS"
HEADER_CONTENT_TYPE = "CONTENT-TYPE"

# cgi response header values
STATUS_OK = "200 OK"
STATUS_BAD_REQUEST = "400 Bad Request"
STATUS_INTERNAL_SERVER_ERROR = "500 Internal Server Error"
STATUS_UNSUPPORTED_REQUEST_METHOD = "501 Unsupported Request"

def respond (headerStatus, response):
    # print the headers...
    print ("{}: {}".format (HEADER_STATUS, headerStatus))
    print ("{}: {}; {}={}".format (HEADER_CONTENT_TYPE, MIME_TYPE_JSON, CHARSET, CHARSET_UTF8))
    print ("X-Content-Type-Options: nosniff")
    print ("Access-Control-Allow-Origin: *")
    print ("Access-Control-Allow-Headers: *")
    print ("Access-Control-Allow-Methods: POST,OPTIONS")
    print ()

    # print the response
    print (response)

    # exit stage left
    sys.exit(0)

