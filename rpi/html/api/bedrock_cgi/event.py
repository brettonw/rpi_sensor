import json
import time
import inspect
from .cgi_request import CgiRequest
from .cgi_response import respond, STATUS_OK

# some constants we need
QUERY = "query"
RESPONSE = "response"
RESPONSE_TIME_NS = "response-time-ns"
STATUS = "status"
OK = "ok"
ERROR = "error"
EVENT = "event"

"""
Common Gateway Interface - this joins the Server Base and event handling of the Java version of
Bedrock.
"""
class Event:
    def __init__(self):
        self.query = CgiRequest.getQuery()
        self.startTime = time.time_ns()

    def __respond (self, status, responseName, response):
        bedrockResponse = { STATUS: status, QUERY: self.query, RESPONSE_TIME_NS : time.time_ns() - self.startTime }
        if (response != None):
            bedrockResponse[responseName] = response
        respond (STATUS_OK, json.dumps (bedrockResponse))

    def ok (self, response):
        self.__respond (OK, RESPONSE, response)

    def error (self, description):
        self.__respond (ERROR, ERROR, description)

    def handle (self, globals = None):
        try:
            if (EVENT in self.query):
                eventName = str(self.query[EVENT])
                eventHandler = "handle{}".format (eventName.lower().capitalize())
                if (globals == None):
                    # get the globals from the top-level calling frame
                    frame = inspect.currentframe()
                    while (frame.f_back != None):
                        frame = frame.f_back
                    globals = frame.f_globals
                if (eventHandler in globals):
                    # the handler is expected to call cgi.ok or cgi.error on the instance
                    globals[eventHandler](self)
                else:
                    self.error("No handler found for '{}' ({})".format (EVENT, eventName))
            else:
                self.error ("Missing '{}'".format (EVENT))
        except Exception as exception:
            self.errorOnException(exception)

    def errorOnException (self, exception):
        trace = [ "({}) {}".format (type(exception).__name__, str(exception)) ]
        tb = exception.__traceback__
        while tb is not None:
            trace.append("({}) {}, line {}".format (tb.tb_frame.f_code.co_name, tb.tb_frame.f_code.co_filename, tb.tb_lineno))
            tb = tb.tb_next
        self.error(trace)

