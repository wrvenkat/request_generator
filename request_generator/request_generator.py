from builders import *
from html.html_request_builder import HtmlRequestBuilder
from html.jquery.jquery_request_builder import JQueryRequestBuilder

class RequestGenerator():

    @classmethod
    def generate_request(cls, requests=None, type=None, target_type=None, auto_submit=None):
        """
        Build bootstrap method.
        """

        builder = None
        #get the right builder object
        if type == Type.form_request or type == Type.xhr_request:
            builder = HtmlRequestBuilder(requests=requests)
        elif type == Type.jquery_request:
            builder = JQueryRequestBuilder(requests=requests)
        else:
            return "No builder found."
        
        #build it        
        builder.build(type=type, target_type=target_type, auto_submit=auto_submit)
    
        #return the generated code
        return builder.generate()
