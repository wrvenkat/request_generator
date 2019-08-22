from request_parser.http.request import HttpRequest

class RequestBuilder(object):
    """
    Abstract interface class that defines the API any request builder
    implementations would offer.
    """

    def __init__(self, requests=[]):
        """
        Accepts an array of HttpRequest objects.
        """
        if requests is not None and\
            len(requests) < 1:
            #not isinstance(http_requests, HttpRequest):
            raise ValueError("RequestBuilder(): requires at least 1 HttpRequest object")
        
        #for http_request in requests:
        #    if not isinstance(http_request, HttpRequest):
        #        raise TypeError("RequestBuilder(): requires an array of HttpRequest objects.")

        #initialize state variables
        self.requests = requests
        #holds the DOM for the request
        self.request_dom = None
    
    def build(self, *args, **kwargs):
        """
        Entry point into a biulder to triggeer building.
        """
        pass
    
    def generate(self):
        """
        Code generation trigger method.
        """
        pass