from dom.Encoder import Encoder
from base64 import b64encode

from request_parser.http.request import HttpRequest, QueryDict
from request_parser.conf.settings import Settings

from js_statements_template import *
import dom.simple_html_elements as HTMLDocument

class UnsupportedFormMethodException(Exception):
    """
    Raised when a build_form() is called with an HttpRequest object with
    request method other than POST or GET.
    """
    pass

class UnsupportedContentTypeException(Exception):
    """
    Raised when a build_form() is called with an HttpRequest object with
    a content_type other than the 3 supproted by default.
    """
    pass

class SimpleCSRFDOMBuilder():
    """
    Builds an HTML DOM from a request_parser.http.request object.
    """

    class Type():
        form_request    = 0        
        xhr_request     = 1
    
    class TargetType():
        iframe      = 0
        new_tab     = 1
        same_page   = 2
    
    def __init__(self, http_requests=[]):
        """
        Accepts an array of HttpRequest objects.
        """
        if http_requests is not None and\
            len(http_requests) < 1:
            #not isinstance(http_requests, HttpRequest):
            raise ValueError("SimpleHTMLDOMBuilder(): requires at least 1 HttpRequest object")
        
        for http_request in http_requests:
            if not isinstance(http_request, HttpRequest):
                raise TypeError("SimpleHTMLDOMBuilder(): requires an array of HttpRequest objects.")

        #initialize state variables
        self.http_requests = http_requests
        #holds the DOM for the request
        self.html_request = None
    
    def build_CSRF_POC(self, type=Type.form_request, target_type=TargetType.iframe,auto_submit=False):
        """
        Build bootstrap method.
        """

        if self.http_requests is None:
            self.html_request = None
            return None
        
        if type == self.Type.form_request:
            self.html_request = self.build_form_request(target_type=target_type, auto_submit=auto_submit)
        elif type == self.Type.xhr_request:
            self.html_request = self.build_XHR_request(auto_submit=auto_submit)
        return self.html_request
    
    def generate(self):
        """
        Returns the generated code for self.request_html.
        """

        if self.html_request is None:
            return ''
        
        return self.html_request.generate()

    def build_form_request(self, target_type=TargetType.iframe, auto_submit=False):
        """
        Builds an HTML DOM for form based request.
        """
        
        if self.http_requests is None:
            return None

        #get an HTML DOM
        html_dom = self._build_CSRF_template_DOM()
        
        #setup the target
        if target_type == SimpleCSRFDOMBuilder.TargetType.iframe:
            iframe_attrs = {
                'id' : 'iframe0',
                'name' : 'iframe0'
            }
            iframe = HTMLDocument.IFrame(attrs=iframe_attrs)
            html_dom.body[0].append(iframe)

        #create a form for each of the request provided
        for index, request in enumerate(self.http_requests):
            request_form = self._build_form(id=index, request=request)

            target = None
            if target_type == SimpleCSRFDOMBuilder.TargetType.iframe:
                target = (html_dom.body[0].iframe[0])['id']
            elif target_type == SimpleCSRFDOMBuilder.TargetType.new_tab:
                target = '_blank' 
            elif target_type == SimpleCSRFDOMBuilder.TargetType.same_page:
                target = None
            
            if target is not None:
                request_form["target"] = target

            #append the form to the body
            html_dom.body[0].append(request_form)

        #build auto submit script snippets for all the forms
        if auto_submit:
            form_ids = []
            #construct an array of form ids to be used
            for form in html_dom.body[0].form:
                form_ids.append(form['id'])
            script_snippet = self._build_auto_submit_JS_snippets(form_ids=form_ids)
            html_dom.body[0].append(script_snippet)            
        
        #set our request object as the one constructed
        return html_dom
    
    #TODO: Implement this.
    def build_XHR_request(self, target_type=TargetType.same_page, auto_submit=False):
        """
        Builds HTML DOM to make XHR request
        """
        pass
    
    def _build_form(self, id=1, request=None):
        """
        Builds and returns an HTML form for the provided
        http_request obejct.

        Accepts an optional id argument for the value of the id parameter.
        """
        if request is None:
            return None
        
        method = request.method
        #extract the info needed to construct a form
        req_content_type = request.content_type
        if  req_content_type != "application/x-www-form-urlencoded" and\
            req_content_type != "multipart/form-data" and\
            req_content_type != "text/plain":
            raise UnsupportedContentTypeException()
        
        #build a generic form
        #extract the info needed to construct a form
        method = request.method
        get_parameters = request.GET
        post_parameters = request.POST
        req_content_type = request.content_type

        #get the safe URI with get_parameters
        action_url = request.get_uri() + self._build_query_string(get_parameters)

        #build the multipart/form-data form
        form_attrs = {
            'enctype'   : req_content_type,
            'id'        : id,
            'name'      : id
        }
        form = HTMLDocument.Form(action=action_url, method=method, attrs=form_attrs)

        #post_parameters = QueryDict(settings=Settings.default)
        #Add post params and other files as part of the multipart request
        #add all the post_parameters as input elements
        for param, value in post_parameters.items():
            if req_content_type == "multipart/form-data":
                value = value['data']
            input_element = HTMLDocument.Input(name=param, _type=HTMLDocument.Input.Type.hidden, value=value)
            form.append(input_element)

        #build the multipart/form-data part of the request
        files = request.FILES
        
        #build the file input elements
        for index, param_name in enumerate(files):
            #add the getFile function during the first iteration
            if index == 0:
                form.append(self._build_get_file_JS_function())

            #create file input element and append to form
            file_input_attrs = {
                'id' : 'fileToUpload{}'.format(index)
            }
            file_input_element = HTMLDocument.Input(name=param_name,
                _type=HTMLDocument.Input.Type.file, attrs=file_input_attrs)
            form.append(file_input_element)
            form.append(HTMLDocument.BR())
        
        #construct JS statements to assign files to their input elements
        for index, param_name in enumerate(files):
            file_object = files[param_name]
            file_JS_element = self._build_multipart_file_js_snippet(file_index=index, multipart_file=file_object)
            #append to the form
            form.append(file_JS_element)

        #add the submit button
        form.append(HTMLDocument.BR())
        form.append(HTMLDocument.Input(name='Submit', _type=HTMLDocument.Input.Type.submit, value="Submit"))

        return form
    
    def _build_query_string(self, query_dict={}):
        """
        Builds the query string part of a request URL.
        """

        if len(query_dict) == 0:
            return ''
        
        query_string = '?'
        index = 0
        for key, value in query_dict:
            q_string = '{}={}'
            q_string = q_string.format(Encoder.escape_for_url_parameter_value(key), 
                                       Encoder.escape_for_url_parameter_value(value))
            if index == 0:
                query_string += q_string
            else:
                query_string += '&'+q_string
            index +=1
        return query_string

    def _build_multipart_file_js_snippet(self, file_index = 1, multipart_file=None):
        """
        Builds multipart JS snippet statements.
        """

        file_JS_element = None
        if multipart_file is None:
            return file_JS_element
        
        #create the base64 encoded version of the file contents
        base64_file_content = b64encode(multipart_file.read())
        file_name = multipart_file.name
        content_type = multipart_file.content_type

        #generate JS statements for files
        file_JS_element = HTMLDocument.Script()
        encoded_file_name = MULTI_PART_ENCODED_FILE_NAME.format(file_index)
        decoded_file_name = MULTI_PART_DECODED_FILE_NAME.format(file_index)
        encoded_assignment_text = MULTI_PART_FILE_JS_ENCODED_STMT.format(encoded_file_name, base64_file_content)
        decoded_assignment_text = MULTI_PART_FILE_JS_DECODED_STMT.format(decoded_file_name, encoded_file_name)
        file_input_assignment_text = ''
        if content_type is not None and len(content_type) > 0:
            file_input_assignment_text = MULTI_PART_FILE_INPUT_ASSIGNMENT_STMT_1.format(file_index,
                                        decoded_file_name, Encoder.encode_for_JS_data_values(file_name),
                                        Encoder.encode_for_JS_data_values(content_type))
        else:
            file_input_assignment_text = MULTI_PART_FILE_INPUT_ASSIGNMENT_STMT_2.format(file_index,
                                        decoded_file_name, Encoder.encode_for_JS_data_values(file_name))
        
        #create text elements
        encoded_assignment_stmt = HTMLDocument.Text(text=encoded_assignment_text)
        decoded_assignment_stmt = HTMLDocument.Text(text=decoded_assignment_text)
        file_input_assignment_stmt = HTMLDocument.Text(text=file_input_assignment_text)

        #add it to the script element
        file_JS_element.append(encoded_assignment_stmt)
        file_JS_element.append(decoded_assignment_stmt)
        file_JS_element.append(file_input_assignment_stmt)

        return file_JS_element
    
    def _build_get_file_JS_function(self):
        """
        Builds the getFile JS function that returns
        DataTransfer.files created for the file.
        """
        get_file_script_element = HTMLDocument.Script()
        #create text elements for the JS statements
        func_hdr = HTMLDocument.Text(text=GET_FILE_FUNCTION_HEADER)
        func_stmt1 = HTMLDocument.Text(text=JS_COMMENT)
        func_stmt2 = HTMLDocument.Text(text=DATA_TRANSFER_JS_CLIPBOARD_STMT)
        func_stmt3 = HTMLDocument.Text(text=DATA_TRANSFER_JS_STMT)
        func_if_condn = HTMLDocument.Text(text=IF_CONDN)
        func_if_true = HTMLDocument.Text(text=IF_TRUE)
        func_if_true.setup(parent=func_if_condn)
        func_else = HTMLDocument.Text(text=ELSE_STMT)
        func_if_false = HTMLDocument.Text(text=IF_FALSE)
        func_if_false.setup(parent=func_else)
        func_return = HTMLDocument.Text(text=RETURN_STMT)
        func_footer = HTMLDocument.Text(text=GET_FILE_FUNCTION_FOOTER)

        #add them to the script element
        get_file_script_element.append(func_hdr)
        get_file_script_element.append(func_stmt1)
        get_file_script_element.append(func_stmt2)
        get_file_script_element.append(func_stmt3)
        get_file_script_element.append(func_if_condn)
        get_file_script_element.append(func_else)
        get_file_script_element.append(func_return)
        get_file_script_element.append(func_footer)
        
        return get_file_script_element

    def _build_auto_submit_JS_snippets(self, form_ids=[], timeout=3):
        """
        Builds autosubmit JS statements as a Text element to submit
        forms with form_refs as names with a delay of timeout secs 
        between each other.

        Default timeout value between each form submission is 3 seconds.
        """
        
        script_snippet = HTMLDocument.Script()
        for form_ref in form_ids:
            # add the form_ref safely
            snippet = AUTO_SUBMIT_JS_STMT_TEMPLATE.format(Encoder.encode_for_JS_data_values(form_ref),
                                                            timeout * 1000)
            # create a Text element for each snippet so that it's easy to format them
            snippet_element = HTMLDocument.Text(text=snippet)
            #timeout is a cumulative value
            timeout += 3
            script_snippet.append(snippet_element)
        return script_snippet

    def _build_CSRF_template_DOM(self):
        """
        Builds a simple HTML DOM to be used in CSRF.
        """

        html_dom    = HTMLDocument.HTML()
        html_head   = HTMLDocument.Head(parent=html_dom)
        html_title  = HTMLDocument.Title(title="Advanced CSRF POC!", parent=html_head)
        html_body   = HTMLDocument.Body(parent=html_dom)
        html_body_title = HTMLDocument.Heading(text='Advanced CSRF POC!')
        html_body.append(html_body_title)

        return html_dom
