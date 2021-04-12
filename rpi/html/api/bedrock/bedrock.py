import json
import time
import inspect
from .cgi_request import CgiRequest
from .cgi_response import CgiResponse

startTime = time.time_ns()

QUERY = "query"
RESPONSE = "response"
RESPONSE_TIME_NS = "response-time-ns"
STATUS = "status"
OK = "ok"
ERROR = "error"
EVENT = "event"

class Bedrock:

    @staticmethod
    def __respond (status, query, responseName, response):
        bedrockResponse = { STATUS: status }

        # add the query
        if (query != None):
            bedrockResponse[QUERY] = query

        # add the response time
        bedrockResponse[RESPONSE_TIME_NS] = time.time_ns() - startTime

        # add the response if there is one
        if (response != None):
            bedrockResponse[responseName] = response

        # bundle it all up and send it out the door
        CgiResponse.respond (CgiResponse.STATUS_OK, json.dumps (bedrockResponse))

    @staticmethod
    def __ok (query, response):
        Bedrock.__respond (OK, query, RESPONSE, response)

    @staticmethod
    def handleRequest (globals = None):
        query = CgiRequest.getAsDictionary()
        try:
            # do some work to handle the query
            if (EVENT in query):
                eventName = str(query[EVENT])
                eventHandler = "handle{}".format (eventName.lower().capitalize())
                if (globals == None):
                    # get the globals from the calling frame
                    globals = inspect.currentframe().f_back.f_globals
                if (eventHandler in globals):
                    response = globals[eventHandler](query)
                    Bedrock.__ok (query, response)
                else:
                    Bedrock.error(query, "No handler found for '{}' ({})".format (EVENT, eventName))
            else:
                Bedrock.error (query, "Missing '{}'".format (EVENT))
        except Exception as exception:
            Bedrock.errorOnException(query, exception)

    @staticmethod
    def error (query, description):
        Bedrock.__respond (ERROR, query, ERROR, description)

    @staticmethod
    def errorOnException (query, exception):
        trace = [ "({}) {}".format (type(exception).__name__, str(exception)) ]
        tb = exception.__traceback__
        while tb is not None:
            trace.append("({}) {}, line {}".format (tb.tb_frame.f_code.co_name, tb.tb_frame.f_code.co_filename, tb.tb_lineno))
            tb = tb.tb_next
        Bedrock.error(query, trace)

