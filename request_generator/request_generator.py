from builders import *
from html.html_request_builder import HtmlRequestBuilder
from html.jquery.jquery_request_builder import JQueryRequestBuilder

class RequestGenerator():    

    @classmethod
    def generate_request(cls, requests=None, *args, **kwargs):
        """
        Build bootstrap method.
        """

        builder = None

        #get the right builder object
        if type == Type.form_request or type == Type.xhr_request:
            builder = HtmlRequestBuilder(requests=requests)
        elif type == Type.jquery_request:
            builder = JQueryRequestBuilder(requests=requests)
        
        #build it
        builder.build(args, kwargs)
    
        #return the generated code
        return builder.generate()
