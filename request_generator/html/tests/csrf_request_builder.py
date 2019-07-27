import unittest
from os.path import join

from request_generator.utils.utils import get_abs_path
from request_parser.http.request import HttpRequest
from request_parser.conf.settings import Settings

from ..csrf_request_builder import SimpleCSRFDOMBuilder

class SimpleCSRFDOMBuilderTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        test_files_dir = "html/tests"
        cls.test_files_dir = get_abs_path(test_files_dir)

        put_request_multipart_file = "complex-request1.txt"
        cls.put_request_multipart_file = join(cls.test_files_dir, put_request_multipart_file)
    
    def test_a_multi_part_csrf_form(self):
        """
        Tests building an HTML with form based CSRF request
        for a multipart/form-data request.
        """
        
        multipart_request_stream = open(self.put_request_multipart_file, 'r')

        #get a request handle
        multipart_request = HttpRequest(multipart_request_stream)
        multipart_request.parse_request_header()
        multipart_request.parse_request_body()
        
        #create a request array
        requests = [ multipart_request ]
        
        #initialize a CSRF POC builder
        csrf_POC_builder = SimpleCSRFDOMBuilder(requests)

        #request a build of form based CSRF POC with auto-submit script
        csrf_POC_builder.build_CSRF_POC(type=SimpleCSRFDOMBuilder.Type.form_request,
                                            target_type=SimpleCSRFDOMBuilder.TargetType.iframe,auto_submit=True)
        
        #generate DOM code
        csrf_POC_code = csrf_POC_builder.generate()

        #print the POC
        print "Generated POC:\n"+csrf_POC_code

        #close it out so the temp file is deleted
        multipart_request_stream.close()

unittest.main()