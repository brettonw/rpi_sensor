import os
import inspect
from .cgi_response import respond, STATUS_OK, STATUS_UNSUPPORTED_REQUEST_METHOD
from .event import Event

# cgi request header environment variables and values
REQUEST_METHOD = "REQUEST_METHOD"
REQUEST_METHOD_POST = "POST"
REQUEST_METHOD_OPTIONS = "OPTIONS"

class ServiceBase:
    @staticmethod
    def __doPost (method):
        # TODO look for a schema, validate events, and filter events
        Event ().handle()

    @staticmethod
    def __doOptions (method):
        # see https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/OPTIONS
        # TODO may want to actually check the request headers to confirm they are allowed
        respond (STATUS_OK, method)

    @staticmethod
    def __doUnsupported (method):
        # this is just a base error - if we couldn't get a workable request
        respond (STATUS_UNSUPPORTED_REQUEST_METHOD, "Unsupported Request ('{}' must be '{}' or '{}', received '{}')".format (REQUEST_METHOD, REQUEST_METHOD_POST, REQUEST_METHOD_OPTIONS, method))

    @staticmethod
    def respond ():
        # we only respond to 'post' events so that HTTPS can mask exchanges, and 'options' for CORS
        switcher = { REQUEST_METHOD_POST : ServiceBase.__doPost, REQUEST_METHOD_OPTIONS : ServiceBase.__doOptions }
        method = os.environ.get(REQUEST_METHOD, None)
        switcher.get (method, ServiceBase.__doUnsupported) (method)
