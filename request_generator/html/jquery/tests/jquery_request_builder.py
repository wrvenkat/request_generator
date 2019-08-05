import unittest
from os import path
from os import mkdir

from request_generator.utils.utils import get_abs_path
from request_generator.builders import Type
from request_parser.http.request import HttpRequest
from request_parser.conf.settings import Settings

from ..jquery_request_builder import JQueryRequestBuilder
from ....html.html_request_builder import TargetType

TEST_REQUESTS_FILES_DIR = "html/tests/raw_http_requests"
GEN_OUTPUT_DIR = "html/jquery/tests/gen_test_jquery_poc"

class JQueryRequestBuilderTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.simple_get_request                      = "get-request-no-query-string.txt"
        cls.simple_get_request_with_query_string    = "get-request-with-query-string.txt"
        cls.post_request_with_query_string          = "post-request-with-query-string.txt"
        cls.post_request_plain_text                 = "post-request-plain-text.txt"
        cls.put_request_multipart_file              = "multi-part-post-request.txt"

        print "Generated HTML files are written inside the '"+GEN_OUTPUT_DIR+\
                "' directory inside the tests package."
    
    def get_abs_path_file(self, file_name=None):
        if file_name is None or len(file_name) == 0:
            return None
        
        self.test_files_dir = get_abs_path(TEST_REQUESTS_FILES_DIR)
        
        return path.join(self.test_files_dir, file_name)

    def parse_and_build_dom(self, request_file_names=[], type=Type.jquery_request,
                                    target_type=TargetType.iframe, auto_submit=True):
        """
        Method that takes care of the most repeated part - parse requests and generate the request DOM.
        """

        request_dom = None
        if request_file_names is None or len(request_file_names) == 0:
            return request_dom

        request_streams = []
        requests_raw = []

        #create streams out of file_names
        for index, request_file_name in enumerate(request_file_names):
            request_file_name = self.get_abs_path_file(request_file_name)
            request_file_names[index] = request_file_name
            request_stream = open(request_file_name, 'r')
            request_streams.append(request_stream)
        
        #create requests handle for each of the stream
        for request_stream in request_streams:
            request = HttpRequest(request_stream=request_stream)
            requests_raw.append(request)

        #start parsing each of the request
        for request in requests_raw:
            request.parse_request_header()
            request.parse_request_body()
        
        #generate request DOM for the combined requests
        request_dom = JQueryRequestBuilder(requests=requests_raw)
        
        #trigger build
        request_dom.build(target_type=target_type, auto_submit=auto_submit)

        #for each of the stream close them
        for request_stream in request_streams:
            request_stream.close()

        #return the built DOM ready
        #for generation
        return request_dom

    def generate_and_write(self, dom=None, file_name=None):
        """
        Generates code from dom and write to file_name.
        """

        if dom is None:
            return
        
        html_code = dom.generate()
        self.write_to_test_output_dir(file_name=file_name, data=html_code)

    def write_to_test_output_dir(self, file_name=None, data=None):
        """
        Writes the file with file_name to the test output directory inside the tests package.
        """

        if file_name is None or len(file_name) == 0:
            raise ValueError("write_to_test_output_dir(): file_name cannot be None or empty.")        
        
        if data is None:
            return
        
        #construct the absolute output dir for test CSRF POCs        
        dir_path = get_abs_path(GEN_OUTPUT_DIR)

        #make the temp directory if it doesn't exist
        if not path.exists(dir_path):
            mkdir(dir_path)
                
        file_path = path.join(dir_path, file_name)
        file_handle = open(file_path, "w")
        file_handle.write(data)
        file_handle.close()

    def test_a_single_request_get_jquery_form_1(self):
        request_file_names = [self.simple_get_request]

        request_file_name = "a_single_request_get_jquery_form_1"
        #iframe
        dom = self.parse_and_build_dom(request_file_names=request_file_names,
                                type=Type.jquery_request,
                                target_type=TargetType.iframe,
                                auto_submit=True)
        file_name = request_file_name+"_iframe.html"
        self.generate_and_write(dom=dom, file_name=file_name)

        #newtab        
        dom = self.parse_and_build_dom(request_file_names=request_file_names,
                                type=Type.jquery_request,
                                target_type=TargetType.new_tab,
                                auto_submit=True)
        file_name = request_file_name+"_new_tab.html"
        self.generate_and_write(dom=dom, file_name=file_name)
        
    def test_b_single_request_get_jquery_form_2(self):
        request_file_names = [self.simple_get_request_with_query_string]

        #generate file name
        request_file_name = "c_single_request_get_jquery_form_2"
        dom = self.parse_and_build_dom(request_file_names=request_file_names,
                                type=Type.jquery_request,
                                target_type=TargetType.iframe,
                                auto_submit=True)
        
        #generate file name
        file_name = request_file_name+"_iframe.html"
        self.generate_and_write(dom=dom, file_name=file_name)

        #newtab
        dom = self.parse_and_build_dom(request_file_names=request_file_names,
                                type=Type.jquery_request,
                                target_type=TargetType.new_tab,
                                auto_submit=True)
        file_name = request_file_name+"_new_tab.html"
       	self.generate_and_write(dom=dom, file_name=file_name)
  
    def test_c_single_request_post_jquery_form(self):
        request_file_names = [self.post_request_with_query_string]

        request_file_name = "e_single_request_post_jquery_form_1"
        dom = self.parse_and_build_dom(request_file_names=request_file_names,
                                type=Type.jquery_request,
                                target_type=TargetType.iframe,
                                auto_submit=True)
        
        #generate file name
        file_name = request_file_name+"_iframe.html"
        self.generate_and_write(dom=dom, file_name=file_name)

        #newtab
        dom = self.parse_and_build_dom(request_file_names=request_file_names,
                                type=Type.jquery_request,
                                target_type=TargetType.new_tab,
                                auto_submit=True)
        file_name = request_file_name+"_new_tab.html"
       	self.generate_and_write(dom=dom, file_name=file_name)
    
    def test_d_single_request_post_plain_text_jquery_form(self):
        request_file_names = [self.post_request_plain_text]
        
        request_file_name = "g_single_request_post_plain_text_jquery_form"
        dom = self.parse_and_build_dom(request_file_names=request_file_names,
                                type=Type.jquery_request,
                                target_type=TargetType.iframe,
                                auto_submit=True)
        
        #generate file name
        file_name = request_file_name+"_iframe.html"
        self.generate_and_write(dom=dom, file_name=file_name)

        #newtab
        dom = self.parse_and_build_dom(request_file_names=request_file_names,
                                type=Type.jquery_request,
                                target_type=TargetType.new_tab,
                                auto_submit=True)
        file_name = request_file_name+"_new_tab.html"
       	self.generate_and_write(dom=dom, file_name=file_name)
  
    def test_e_single_request_multi_part_post_jquery_form(self):
        """
        Tests building an HTML with form based CSRF request
        for a multipart/form-data request.
        """
        
        request_file_names = [self.put_request_multipart_file]

        request_file_name = "i_single_request_multi_part_jquery_form"
        dom = self.parse_and_build_dom(request_file_names=request_file_names,
                                type=Type.jquery_request,
                                target_type=TargetType.iframe,
                                auto_submit=True)
        #generate DOM code
        csrf_POC_code = dom.generate()
        #generate file name
        file_name = request_file_name+"_iframe.html"
        self.generate_and_write(dom=dom, file_name=file_name)

        #newtab
        dom = self.parse_and_build_dom(request_file_names=request_file_names,
                                type=Type.jquery_request,
                                target_type=TargetType.new_tab,
                                auto_submit=True)
        file_name = request_file_name+"_new_tab.html"
       	self.generate_and_write(dom=dom, file_name=file_name)
       
    def test_f_multi_request_jquery_form(self):
        request_file_names = [  self.simple_get_request,
                                self.simple_get_request_with_query_string,
                                self.post_request_with_query_string,
                                self.post_request_plain_text,
                                self.put_request_multipart_file
                            ]
        
        request_file_name = "k_multi_request_jquery_form"
        dom = self.parse_and_build_dom(request_file_names=request_file_names,
                                type=Type.jquery_request,
                                target_type=TargetType.iframe,
                                auto_submit=True)
        
        #generate file name
        file_name = request_file_name+"_iframe.html"
        self.generate_and_write(dom=dom, file_name=file_name)

        #newtab
        dom = self.parse_and_build_dom(request_file_names=request_file_names,
                                type=Type.jquery_request,
                                target_type=TargetType.new_tab,
                                auto_submit=True)
        file_name = request_file_name+"_new_tab.html"
       	self.generate_and_write(dom=dom, file_name=file_name)
    
unittest.main()