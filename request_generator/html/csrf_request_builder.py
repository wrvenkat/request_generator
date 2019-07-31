from dom.Encoder import Encoder
from base64 import b64encode

from request_parser.http.request import HttpRequest, QueryDict
from request_parser.conf.settings import Settings
from request_parser.http.constants import MetaDict

from js_statements_template import *
from xhr_js_template import *
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
        
    def build_XHR_request(self, auto_submit=False):
        """
        Builds HTML DOM to make XHR request
        """
        
        if self.http_requests is None:
            return None

        #get an HTML DOM
        html_dom = self._build_CSRF_template_DOM()

        #build an iframe to show the responses onto
        iframe_attrs = {
            'id' : 'iframe0'
        }
        iframe = HTMLDocument.IFrame(attrs=iframe_attrs)
        html_dom.body[0].append(iframe)
        #add a BR element
        html_dom.body[0].append(HTMLDocument.BR())
        
        #create a script element to which a lot of the XHR
        #related JS code will be added
        xhr_script = HTMLDocument.Script()
        html_dom.body[0].append(xhr_script)

        #iframe reference code
        iframe_reference_snippet = HTMLDocument.Text(text=IFRAME_REF_STMT_TEXT)
        xhr_script.append(iframe_reference_snippet)

        #createCORSrequest function
        create_cors_req_function_snippet_1 = HTMLDocument.Text(text=CREATE_XHR_FUNCTION_TEXT1)
        create_cors_req_function_snippet_2 = HTMLDocument.Text(text=CREATE_XHR_FUNCTION_TEXT2)
        onreadystatechangetrigger_function_snippet_1 = HTMLDocument.Text(text=XHR_ONREADYSTATECHANGE_FUNCTION_TEXT1)
        onreadystatechangetrigger_function_snippet_2 = HTMLDocument.Text(text=XHR_ONREADYSTATECHANGE_FUNCTION_TEXT2)
        xhr_script.append(create_cors_req_function_snippet_1)
        xhr_script.append(create_cors_req_function_snippet_2)
        #add a new line
        xhr_script.append(HTMLDocument.Text(text=" "))
        xhr_script.append(onreadystatechangetrigger_function_snippet_1)
        xhr_script.append(onreadystatechangetrigger_function_snippet_2)

        #create header for sendXHR() function
        send_XHR_function_header_snippet = HTMLDocument.Text(text=SEND_XHR_FUNCTION_HEADER_TEXT)
        send_XHR_function_footer_snippet = HTMLDocument.Text(text=SEND_XHR_FUNCTION_FOOTER_TEXT)
        xhr_script.append(send_XHR_function_footer_snippet)

        #for each request, build XHR for them
        #and add them to send_XHR_function_header_snippet
        for index, request in enumerate(self.http_requests):
            self._build_XHR_snippets(parent_script=xhr_script, send_xhr=send_XHR_function_header_snippet,
                                    index=index, request=request)
        
        #add the header and footer of sendXHR()
        xhr_script.append(send_XHR_function_header_snippet)
        xhr_script.append(send_XHR_function_footer_snippet)

        #add a click Button
        send_xhr_function_name = SEND_XHR_FUNCTION_NAME+"();"
        click_me_button = HTMLDocument.Button(text="Submit XHR CSRF", onclick=send_xhr_function_name)
        html_dom.body[0].append(click_me_button)

        return html_dom
    
    def _build_XHR_snippets(self, parent_script=None, send_xhr=None, index=0, request=None):
        """
        Builds XHR JS statements that get added onto sendXHR function.

        Returns a set of Text elements containing JS statements required
        to make that XHR request.
        """        

        if parent_script is None or send_xhr is None or request is None:
            return None

        #get info about the request
        method = request.method
        get_parameters = request.GET
        post_parameters = request.POST
        files = request.FILES
        req_content_type = request.content_type

        #get the safe URI with get_parameters
        action_url = request.get_uri() + self._build_query_string(get_parameters)

        post_data = None
        # if the content-type is multipart/form-data
        if req_content_type == "multipart/form-data":
            form_data_obj_text = FORM_DATA_API_TEXT.format(index)
            form_data_obj = HTMLDocument.Text(text=form_data_obj_text)
            send_xhr.append(form_data_obj)

            #build JS statements for files
            for file_index, param_name in enumerate(files):
                #add the getFile function during the first iteration
                if file_index == 0:
                    get_file_js = self._build_get_file_JS_function()
                    parent_script.append(get_file_js)
                    get_file_js.unwrap()
                    #add a line break
                    parent_script.append(HTMLDocument.Text(text=' '))

                #get a script elemetn that contains the JS statements
                file_JS_element = self._build_multipart_file_js_snippet(file_index=file_index,
                                        multipart_file=files[param_name],xhr=True)
                #add the received element
                send_xhr.append(file_JS_element)
                #and unwrap it
                if file_JS_element is not None:
                    file_JS_element.unwrap()

                #build the statement to add file{} object to the
                #formData object
                form_data_file_append_text = FORM_DATA_FILE_APPEND_TEXT.format(index, param_name, file_index)
                form_data_file_append = HTMLDocument.Text(text=form_data_file_append_text)
                send_xhr.append(form_data_file_append)               
            
            #build JS statements to add POST params to
            #the formdata object
            for param_name, value in post_parameters.items():
                if req_content_type == "multipart/form-data":
                    value = value['data']
                form_data_param_append_text = FORM_DATA_PARAM_APPEND_TEXT.format(index,
                                                    Encoder.encode_for_JS_data_values(param_name),
                                                    Encoder.encode_for_JS_data_values(value))
                form_data_param_append = HTMLDocument.Text(text=form_data_param_append_text)
                send_xhr.append(form_data_param_append)
            
            #add an empty line
            send_xhr.append(HTMLDocument.Text(text=' '))
        elif req_content_type == "text/plain":
            post_data = request.body()
        # if the content-type is something else
        elif req_content_type == "application/x-www-form-urlencoded":
            post_data = self._build_XHR_post_data(xhr_index=index, params=post_parameters)
        else:
            post_data = request.body()
        
        #complete the rest of the statements
        create_xhr_text_1 = CREATE_XHR_STMT_TEXT_1.format(index, method, action_url)
        create_xhr_text_2 = CREATE_XHR_STMT_TEXT_2.format(index)
        create_xhr_text_3 = CREATE_XHR_STMT_TEXT_3
        create_xhr_text_4 = CREATE_XHR_STMT_TEXT_4.format(index, index)
        
        #create text elements out of it
        create_xhr_1 = HTMLDocument.Text(text=create_xhr_text_1)
        create_xhr_2 = HTMLDocument.Text(text=create_xhr_text_2)
        create_xhr_3 = HTMLDocument.Text(text=create_xhr_text_3)
        create_xhr_4 = HTMLDocument.Text(text=create_xhr_text_4)
        create_xhr_2.append(create_xhr_3)
        
        #build the xhr.send() statement
        xhr_send_text = ''
        if req_content_type == 'multipart/form-data':
            xhr_send_text = XHR_SEND.format(index, "formData{}".format(index))
        else:
            if post_data is not None:
                xhr_send_text = XHR_SEND.format(index,
                                "'"+Encoder.encode_for_JS_data_values(post_data)+"'")
            else:
                xhr_send_text = XHR_SEND.format(index, '')
        timeout_function_text = XHR_SEND_TIMEOUT.format(xhr_send_text, XHR_TIMEOUT * (index+1))
        timeout_function = HTMLDocument.Text(text=timeout_function_text)

        #append to send_xhr
        send_xhr.append(create_xhr_1)
        send_xhr.append(create_xhr_2)
        send_xhr.append(create_xhr_4)

        #set credentials required to true
        xhr_creds_text = XHR_WITH_CREDS_TEXT.format(index)
        xhr_creds = HTMLDocument.Text(text=xhr_creds_text)
        send_xhr.append(xhr_creds)
    
        #then set the content-type header and other
        #custom headers
        xhr_content_type_hdr_text = XHR_HDR_STMT_TEXT.format(index,
                                        'Content-Type',
                                        Encoder.encode_for_JS_data_values(req_content_type))
        xhr_content_type_hdr = HTMLDocument.Text(text=xhr_content_type_hdr_text)
        send_xhr.append(xhr_content_type_hdr)
        
        for header_statements in self._build_XHR_header_JS_snippets(xhr_index=index,
                                                                request=request):
            send_xhr.append(header_statements)
        
        #append to send_xhr        
        send_xhr.append(timeout_function)
        #add an empty line
        send_xhr.append(HTMLDocument.Text(text=' '))

    def _build_form(self, id=1, request=None):
        """
        Builds and returns an HTML form for the provided
        http_request obejct.

        Accepts an optional id argument for the value of the id parameter.
        """
        if request is None:
            return None
        
        #build a generic form
        #extract the info needed to construct a form
        method = request.method
        get_parameters = request.GET
        post_parameters = request.POST
        req_content_type = request.content_type
        if  req_content_type != "application/x-www-form-urlencoded" and\
            req_content_type != "multipart/form-data" and\
            req_content_type != "text/plain":
            raise UnsupportedContentTypeException("{}".format(req_content_type))
                
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
        
        #handle text/plain content
        if req_content_type == 'text/plain':
            #add a warning as we're creating a form for text/plain
            warning_text = HTMLDocument.Font(text='Warning: text/plain type form might not work as expected.')
            text_plain_content = request.body()
            text_plain_content = Encoder.encode_for_HTML_attrib(text_plain_content)
            text_plain_input_element = HTMLDocument.Input(name=text_plain_content,
                                                          _type=HTMLDocument.Input.Type.hidden)
            form.append(HTMLDocument.BR())
            form.append(warning_text)
            form.append(text_plain_input_element)

        #construct JS statements to assign files to their input elements
        for index, param_name in enumerate(files):
            file_object = files[param_name]
            file_JS_element = self._build_multipart_file_js_snippet(file_index=index, multipart_file=file_object)
            #append to the form
            form.append(file_JS_element)

        #add the submit button
        form.append(HTMLDocument.BR())
        form.append(HTMLDocument.Input(_type=HTMLDocument.Input.Type.submit, value="Submit CSRF POC"))

        return form
    
    def _build_query_string(self, query_dict={}):
        """
        Builds the query string part of a request URL.
        """

        if len(query_dict) == 0:
            return ''
        
        query_string = ''
        index = 0
        
        for key, value in query_dict.items():
            q_string = '{}={}'
            q_string = q_string.format(Encoder.escape_for_url_parameter_value(key), 
                                       Encoder.escape_for_url_parameter_value(value))
            if index == 0:
                query_string += '?'+q_string
            else:
                query_string += '&'+q_string
            index +=1
        return query_string

    def _build_multipart_file_js_snippet(self, file_index = 0, multipart_file=None, xhr=False):
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
            template_ = ''
            if not xhr:
                template_ = MULTI_PART_FILE_INPUT_ASSIGNMENT_STMT_1                
            elif xhr:
                template_ = XHR_FILE_ASSIGNMENT_STMT_1
            file_input_assignment_text = template_.format(file_index,
                                            decoded_file_name, Encoder.encode_for_JS_data_values(file_name),
                                            Encoder.encode_for_JS_data_values(content_type))
        else:
            template_ = ''
            if not xhr:
                template_ = MULTI_PART_FILE_INPUT_ASSIGNMENT_STMT_2                
            elif xhr:
                template_ = XHR_FILE_ASSIGNMENT_STMT_2
            file_input_assignment_text = template_.format(file_index,
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
        func_hdr = HTMLDocument.Text(text=GET_FILES_FUNCTION_HEADER)
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
        func_footer = HTMLDocument.Text(text=GET_FILES_FUNCTION_FOOTER)

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
        csrf_title_text = "Enhanced CSRF POC."
        html_dom    = HTMLDocument.HTML()
        html_head   = HTMLDocument.Head(parent=html_dom)
        html_title  = HTMLDocument.Title(title=csrf_title_text, parent=html_head)
        html_body   = HTMLDocument.Body(parent=html_dom)
        html_body_title = HTMLDocument.Heading(text=csrf_title_text)
        html_body.append(html_body_title)

        return html_dom

    #TODO: Add only custom headers and not standard headers.
    def _build_XHR_header_JS_snippets(self, xhr_index=0, request=None):
        """
        Builds JS statements for custom headers in request.
        """
        xhr_header_statements = []
        if request is None:
            return xhr_header_statements            

        request_headers = request.META[MetaDict.Info.REQ_HEADERS]
        #add all the headers
        #CAUTION: request_headers is a MultivalueDict and calling
        #.items() returns (key, value) pairs where value is the 
        #last item in the list!
        for header, value in request_headers.items():
            header_lower = header.lower()
            if header_lower == 'content-type':
                continue                
            elif header_lower == 'user-agent':
                continue
            elif header_lower == 'host':
                continue
            elif header_lower == 'content-length':
                continue
            elif header_lower == 'connection':
                continue
            elif header_lower == 'accept-encoding':
                continue
            elif header_lower == 'accept-charset':
                continue
            
            xhr_header_text = XHR_HDR_STMT_TEXT.format(xhr_index,
                                        Encoder.encode_for_JS_data_values(header),
                                        Encoder.encode_for_JS_data_values(value))
            xhr_header = HTMLDocument.Text(text=xhr_header_text)
            xhr_header_statements.append(xhr_header)

        return xhr_header_statements

    def _build_XHR_post_data(self, xhr_index=0, params=None):
        """
        Builds the POST body for an XHR request.
        """
        post_data = ''
        if params is None or len(params) == 0:
            return post_data

        index = 0
        for param_name, value in params.items():
            if index == 0:
                post_data += '?'
            
            if index != 0:
                    post_data += '&'    
            post_data += param_name+'='+value
            index += 1
        
        return post_data
