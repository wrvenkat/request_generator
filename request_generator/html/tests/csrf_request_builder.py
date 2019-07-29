import unittest
from os import path
from os import mkdir

from request_generator.utils.utils import get_abs_path
from request_parser.http.request import HttpRequest
from request_parser.conf.settings import Settings

from ..csrf_request_builder import SimpleCSRFDOMBuilder
from request_generator.utils.utils import get_abs_path

TEST_FILES_DIR = "html/tests"
GEN_OUTPUT_DIR = "gen_test_csrf_poc"

class SimpleCSRFDOMBuilderTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.test_files_dir = get_abs_path(TEST_FILES_DIR)

        put_request_multipart_file = "complex-request1.txt"
        cls.put_request_multipart_file = path.join(cls.test_files_dir, put_request_multipart_file)

        print "Generated CSRF POCs are written inside the '"+GEN_OUTPUT_DIR+\
                "' directory inside the tests package."
    
    def write_to_test_output_dir(self, file_name=None, data=None):
        """
        Writes the file with file_name to the test output directory inside the tests package.
        """

        if file_name is None or len(file_name) == 0:
            raise ValueError("write_to_test_output_dir(): file_name cannot be None or empty.")        
        
        if data is None:
            return
        
        #construct the absolute output dir for test CSRF POCs
        output_dir_name = path.join(TEST_FILES_DIR, GEN_OUTPUT_DIR)
        dir_path = get_abs_path(output_dir_name)

        #make the temp directory if it doesn't exist
        if not path.exists(dir_path):
            mkdir(dir_path)
                
        file_path = path.join(dir_path, file_name)
        file_handle = open(file_path, "w")
        file_handle.write(data)
        file_handle.close()

    def test_a_single_request_multi_part_csrf_form(self):
        """
        Tests building an HTML with form based CSRF request
        for a multipart/form-data request.
        """
        
        request_stream1 = open(self.put_request_multipart_file, 'r')

        #get a request handle
        request1 = HttpRequest(request_stream1)
        request1.parse_request_header()
        request1.parse_request_body()
        
        #create a request array
        requests = [ request1 ]
        
        #initialize a CSRF POC builder
        csrf_POC_builder = SimpleCSRFDOMBuilder(requests)

        #request a build of form based CSRF POC with auto-submit script
        csrf_POC_builder.build_CSRF_POC(type=SimpleCSRFDOMBuilder.Type.form_request,
                                            target_type=SimpleCSRFDOMBuilder.TargetType.iframe,auto_submit=True)
        
        #generate DOM code
        csrf_POC_code = csrf_POC_builder.generate()

        #generate file name
        csrf_POC_file_name = "single_request_multi_part_csrf_form"
        csrf_POC_file_name += ".html"

        #write the file
        self.write_to_test_output_dir(file_name=csrf_POC_file_name, data=csrf_POC_code)

        #close it out so the temp file is deleted
        request_stream1.close()

        #print that file generated
        print "Generated POC file: "+csrf_POC_file_name

    def test_b_single_request_multi_part_csrf_xhr(self):
        """
        Tests building an HTML with form based CSRF request
        for a multipart/form-data request.
        """
        
        request_stream1 = open(self.put_request_multipart_file, 'r')

        #get a request handle
        request1 = HttpRequest(request_stream1)
        request1.parse_request_header()
        request1.parse_request_body()
        
        #create a request array
        requests = [ request1 ]
        
        #initialize a CSRF POC builder
        csrf_POC_builder = SimpleCSRFDOMBuilder(requests)

        #request a build of form based CSRF POC with auto-submit script
        csrf_POC_builder.build_CSRF_POC(type=SimpleCSRFDOMBuilder.Type.xhr_request,
                                            target_type=SimpleCSRFDOMBuilder.TargetType.iframe,auto_submit=True)
        
        #generate DOM code
        csrf_POC_code = csrf_POC_builder.generate()

        #generate file name
        csrf_POC_file_name = "single_request_multi_part_csrf_xhr"
        csrf_POC_file_name += ".html"

        #write the file
        self.write_to_test_output_dir(file_name=csrf_POC_file_name, data=csrf_POC_code)

        #close it out so the temp file is deleted
        request_stream1.close()

        #print that file generated
        print "Generated POC file: "+csrf_POC_file_name

unittest.main()