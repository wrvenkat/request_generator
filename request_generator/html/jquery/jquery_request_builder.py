from ..dom import simple_html_elements as HTMLDocument
from ..dom.Encoder import Encoder
from ..js_statements_template import MULTI_PART_ENCODED_FILE_NAME, MULTI_PART_DECODED_FILE_NAME, MULTI_PART_FILE_JS_ENCODED_STMT, MULTI_PART_FILE_JS_DECODED_STMT
from ..xhr_js_template import FORM_DATA_API_TEXT, XHR_FILE_ASSIGNMENT_STMT_1, XHR_FILE_ASSIGNMENT_STMT_2, FORM_DATA_FILE_APPEND_TEXT, FORM_DATA_PARAM_APPEND_TEXT

from ..html_request_builder import HtmlRequestBuilder, TargetType
from request_parser.http.request import HttpRequest

from jquery_js_template import *

class JQueryRequestBuilder(HtmlRequestBuilder):
    """
    Class that builds DOM to make requests using jQuery.
    """

    def __init__(self, requests=[]):
        super(JQueryRequestBuilder, self).__init__(requests=requests)

    def build(self, type=1, target_type=TargetType.iframe, auto_submit=False):
        self.request_dom = self.build_ajax_requests(target_type=target_type,
                                                    auto_submit=auto_submit)

    def generate(self):
        if self.request_dom is None:
            return ''
        
        return self.request_dom.generate()

    def build_ajax_requests(self, target_type=TargetType.iframe, auto_submit=False):
        """
        Builds an HTML DOM for jQuery/ajax based request.
        """
        
        if self.requests is None or len(self.requests) == 0:
            return None

        #get an HTML DOM
        html_dom = self.build_template_DOM(title='jQuery based request POC')
        #create a submit button
        button_attrs = {
            'id' : 'submitBtn'
        }
        submit_button = HTMLDocument.Button(text='Submit jQuery CSRF', attrs=button_attrs)
        
        #build jquery src element
        jquery_src_attrs = {
            "src" : JQUERY_INCLUDE_SRC
        }
        jquery_src_script = HTMLDocument.Script(attrs=jquery_src_attrs)        

        #Build jQuery template
        #build jQuery on ready block
        jquery_main_block_script = HTMLDocument.Script()
        jquery_main_block = HTMLDocument.Text(text=JQUERY_DOCUMENT_ONREADY_HDR)
        jquery_main_block_footer = HTMLDocument.Text(text=JQUERY_DOCUMENT_ONREADY_FOOTER)
        
        #setup the target
        jquery_success_function = None
        if target_type == TargetType.iframe:
            iframe_attrs = {
                'id' : 'iframe0',
                'name' : 'iframe0'
            }
            iframe = HTMLDocument.IFrame(attrs=iframe_attrs)
            html_dom.body[0].append(iframe)            
            jquery_success_function = self._build_success_function(iframe=iframe['id'])
            html_dom.body[0].append(HTMLDocument.BR())
        else:
            load_in_new_tab_function = self._build_XHR_load_in_new_tab_function()
            jquery_main_block_script.append(load_in_new_tab_function)
            load_in_new_tab_function.unwrap()
            jquery_success_function = self._build_success_function()

        if auto_submit:
            holder_script = HTMLDocument.Script()
            click_button_txt = JQUERY_CLICK_BUTTON.format(submit_button['id'])
            timeout_text = HTMLDocument.Text(text=AJAX_REQUEST_TIMEOUT.format(click_button_txt, 500))
            holder_script.append(timeout_text)
            html_dom.body[0].append(holder_script)

        #add button to the form body
        html_dom.body[0].append(submit_button)

        #add the success function to the main block
        jquery_main_block.append(jquery_success_function)
        jquery_success_function.unwrap()

        #build the submitAjaxRequest function
        submit_ajax_request = self._build_submit_ajax_request_function()
        
        #add the submitAjaxRequest element to the main block
        jquery_main_block.append(submit_ajax_request)
        submit_ajax_request.unwrap()

        #create the event binding snippet and add to the main jQuery block
        jquery_submit_bind_block = HTMLDocument.Script()
        jquery_submit_bind_function_text = AJAX_SUBMIT_BUTTON_BIND_HDR.format(submit_button['id'])
        jquery_submit_bind_function = HTMLDocument.Text(text=jquery_submit_bind_function_text)
        jquery_submit_bind_block.append(jquery_submit_bind_function)
        jquery_submit_bind_function_footer = HTMLDocument.Text(text=AJAX_SUBMIT_BUTTON_BIND_FOOTER)

        #create jQuery statements/snippet blocks for each request
        get_file_script_added = False
        for index, request in enumerate(self.requests):
            jquery_request_block, get_file_script = self._build_ajax_request(index=index, request=request)
            
            #if the get_file_script has not been added
            #and if it's not None, then add it
            if not get_file_script_added and get_file_script is not None:
                html_dom.body[0].append(get_file_script)
                get_file_script_added = True

            #append the block to the submit bind block
            jquery_submit_bind_function.append(jquery_request_block)
            jquery_request_block.unwrap()

            #add an empty line
            jquery_submit_bind_function.append(HTMLDocument.Text())

        #add the jQuery source snippet to the head
        html_dom.head[0].append(jquery_src_script)

        #add the submit button binding block to the main jquery block
        jquery_submit_bind_block.append(jquery_submit_bind_function_footer)
        jquery_main_block.append(jquery_submit_bind_block)
        jquery_submit_bind_block.unwrap()

        #complete the main block
        jquery_main_block_script.append(jquery_main_block)
        jquery_main_block_script.append(jquery_main_block_footer)

        #add the main block script to the head
        html_dom.head[0].append(jquery_main_block_script)        
        
        #return the constructed DOM
        return html_dom

    def _build_ajax_request(self, index=0,request=None):
        """
        Builds the ajax statements for a single request.
        """
        
        if request is None:
            return None

        #extract the info needed to construct a request
        method = request.method
        get_parameters = request.GET
        post_parameters = request.POST
        files = request.FILES
        req_content_type = request.content_type
                
        #get the safe URI with get_parameters
        action_url = request.get_uri()# + self._build_query_string(get_parameters)

        post_data = None
        get_file_script = None
        holder_script = HTMLDocument.Script()
        # if the content-type is multipart/form-data
        if req_content_type == "multipart/form-data":
            form_data_obj_text = FORM_DATA_API_TEXT.format(index)
            form_data_obj = HTMLDocument.Text(text=form_data_obj_text)
            holder_script.append(form_data_obj)

            #build JS statements for files
            for file_index, param_name in enumerate(files):
                #add the getFile function during the first iteration
                if file_index == 0:
                    get_file_script = self._build_get_file_JS_function()

                #get a script element that contains the JS statements
                file_JS_element = self._build_multipart_file_js_snippet(file_index=file_index,
                                        multipart_file=files[param_name],xhr=True)
                #add the received element
                holder_script.append(file_JS_element)
                #and unwrap it
                if file_JS_element is not None:
                    file_JS_element.unwrap()

                #build the statement to add file{} object to the
                #formData object
                form_data_file_append_text = FORM_DATA_FILE_APPEND_TEXT.format(index, param_name, file_index)
                form_data_file_append = HTMLDocument.Text(text=form_data_file_append_text)
                holder_script.append(form_data_file_append)
            
            #build JS statements to add POST params to
            #the formdata object
            for param_name, value in post_parameters.items():
                if req_content_type == "multipart/form-data":
                    value = value['data']
                form_data_param_append_text = FORM_DATA_PARAM_APPEND_TEXT.format(index,
                                                    Encoder.encode_for_JS_data_values(param_name),
                                                    Encoder.encode_for_JS_data_values(value))
                form_data_param_append = HTMLDocument.Text(text=form_data_param_append_text)
                holder_script.append(form_data_param_append)
        elif req_content_type == "text/plain":
            post_data = request.body()
        # if the content-type is something else
        elif req_content_type == "application/x-www-form-urlencoded":
            post_data = self._build_XHR_post_data(xhr_index=index, params=post_parameters)
        #any other content-type
        else:
            post_data = request.body()
        
        #complete the rest of the jQuery statements
        time_out = 3000        
        time_out = index * time_out
        if get_file_script is None:
            request_submit_statements = self._build_request_statements(index=index, url=action_url,
                                        method=method, data=post_data, content_type=req_content_type,
                                        time_out=time_out)
        else:
            form_data_obj_name = "formData{}".format(index)
            request_submit_statements = self._build_request_statements(index=index, url=action_url,
                                        method=method, data=form_data_obj_name, data_obj=True,
                                        content_type=req_content_type,
                                        time_out=time_out)
        
        #append to holder_script
        holder_script.append(request_submit_statements)
        request_submit_statements.unwrap()

        return holder_script, get_file_script

    def _build_submit_ajax_request_function(self):
        """
        Build the const submitAjaxRequest = .... block.
        """

        holder_script = HTMLDocument.Script()

        submit_ajax_req_hdr = HTMLDocument.Text(text=SUBMIT_AJAX_REQUEST_HDR)
        submit_ajax_req_1 = HTMLDocument.Text(text=SUBMIT_AJAX_REQUEST_IF_1_START)
        submit_ajax_req_1_1 = HTMLDocument.Text(text=SUBMIT_AJAX_REQUEST_IF_1_STMT_1)
        submit_ajax_req_1_2 = HTMLDocument.Text(text=SUBMIT_AJAX_REQUEST_IF_1_STMT_2)
        submit_ajax_req_1.append(submit_ajax_req_1_1)
        submit_ajax_req_1.append(submit_ajax_req_1_2)

        submit_ajax_req_hdr.append(submit_ajax_req_1)
        submit_ajax_req_hdr.append(HTMLDocument.Text(text=SUBMIT_AJAX_REQUEST_IF_1_END))

        #add the ajax block
        ajax_block = self._build_ajax_block()
        submit_ajax_req_hdr.append(ajax_block)
        ajax_block.unwrap()

        holder_script.append(submit_ajax_req_hdr)
        holder_script.append(HTMLDocument.Text(text=SUBMIT_AJAX_REQUEST_FOOTER))

        return holder_script

    def _build_ajax_block(self):
        """
        Builds and returns a holder script
        containing the $.ajax({}) block.                
        """

        holder_script = HTMLDocument.Script()

        ajax_block_hdr = HTMLDocument.Text(text=AJAX_BLOCK_HDR)
        ajax_block_hdr.append(HTMLDocument.Text(text=AJAX_BLOCK_URL))
        ajax_block_hdr.append(HTMLDocument.Text(text=AJAX_BLOCK_TYPE))
        ajax_block_hdr.append(HTMLDocument.Text(text=AJAX_BLOCK_DATA))
        ajax_block_hdr.append(HTMLDocument.Text(text=AJAX_BLOCK_CONTENT_TYPE))
        ajax_block_hdr.append(HTMLDocument.Text(text=AJAX_BLOCK_PROCESS_DATA))
        ajax_block_hdr.append(HTMLDocument.Text(text=AJAX_BLOCK_SUCCESS))
        
        holder_script.append(ajax_block_hdr)
        holder_script.append(HTMLDocument.Text(text=AJAX_BLOCK_FOOTER))

        return holder_script

    def _build_success_function(self, iframe=None):
        """
        Builds and returns a holder script
        containing the successFunction for the ajax
        request.

        Takes iframe ID argument which is the target for
        response.
        """

        holder_script = HTMLDocument.Script()

        success_function_hdr = HTMLDocument.Text(text=AJAX_BLOCK_SUCCESS_FUNCTION_HDR)
        success_function_stmt_txt = ''
        if iframe is not None:
            success_function_stmt_txt = AJAX_BLOCK_SUCCESS_FUNCTION_IFRAME_SRC_SET.format(iframe)
        else:
            success_function_stmt_txt = AJAX_BLOCK_SUCCESS_FUNCTION_NEW_TAB_CALL
        success_function_stmt = HTMLDocument.Text(text=success_function_stmt_txt)
        #append statement
        success_function_hdr.append(success_function_stmt)

        #append to holder script
        holder_script.append(success_function_hdr)
        holder_script.append(HTMLDocument.Text(text=AJAX_BLOCK_SUCCESS_FUNCTION_FOOTER))

        return holder_script

    def _build_request_statements(self, index=0, url='', method='GET', data=None,
                                data_obj=False, content_type='application/x-www-form-urlencoded', time_out=None):
        """
        Builds and returns the jQuery JS statements that construct a request and call
        submitAjaxRequest.

        Returns a holder script with these.
        """

        holder_script = HTMLDocument.Script()
        
        url_text = AJAX_REQUEST_URL_STMT.format(index, Encoder.encode_for_JS_data_values(url))
        method_text = AJAX_REQUEST_METHOD_STMT.format(index, Encoder.encode_for_JS_data_values(method))
        content_type_text = AJAX_REQUEST_CONTENT_TYPE_STMT.format(index, Encoder.encode_for_JS_data_values(content_type))
        data_text = ''
        if not data_obj:
            if data is None:
                data = ''
            data_text = AJAX_REQUEST_DATA_STMT_VALUE.format(index, Encoder.encode_for_JS_data_values(data))
        elif data_obj:
            data_text = AJAX_REQUEST_DATA_STMT_OBJ.format(index, data)
        
        #build the text elements
        url_stmt = HTMLDocument.Text(text=url_text)
        method_stmt = HTMLDocument.Text(text=method_text)
        content_type_stmt = HTMLDocument.Text(text=content_type_text)
        data_stmt  = HTMLDocument.Text(text=data_text)

        #add to holder script
        holder_script.append(url_stmt)
        holder_script.append(method_stmt)
        holder_script.append(content_type_stmt)
        holder_script.append(data_stmt)

        #should there be a timeout statement added?
        submit_request_function_call_text = AJAX_SUBMIT_REQUEST_CALL.format(index, index, index, index)
        if time_out is not None:
            timeout_text = AJAX_REQUEST_TIMEOUT.format(submit_request_function_call_text,
                            time_out)
            timeout_stmt = HTMLDocument.Text(text=timeout_text)
            holder_script.append(timeout_stmt)
        else:
            submit_request_function_call = HTMLDocument.Text(text=submit_request_function_call_text)
            holder_script.append(submit_request_function_call)
                
        return holder_script
