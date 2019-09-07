# -*- coding: utf-8 -*-
from ..Encoder import Encoder
import unittest

class EncoderTest(unittest.TestCase):

    def test_a_get_UTF8(self):
        """
        Tests _getUTF8.
        """
        
        #empty input
        self.assertEquals(Encoder.get_UTF8(), '')

        #input is an str that's valid in
        #Windows-1252 alphabets
        #See: https://en.wikipedia.org/wiki/Windows-1252
        non_utf8_input_str = 'ÀÁÂÃÄÅ'
        utf8_str = Encoder.get_UTF8(non_utf8_input_str)
        self.assertTrue(isinstance(utf8_str, unicode))

        utf8_compatible_str = u'Ångström'
        utf8_str = Encoder.get_UTF8(utf8_compatible_str)
        self.assertTrue(isinstance(utf8_str, unicode))

        #input that's not a value str or bytes object
        self.assertEqual(u'90909', Encoder.get_UTF8(90909))
    
    def test_b_get_hex_entity(self):
        """
        Tests _getCodePoint and getHexEntity.
        """

        codepoint = Encoder.get_code_point(u'ç')
        self.assertEquals(u'&#x00E7;', Encoder.get_hex_entity(codepoint))

    def test_c_encode_for_HTML_content(self):
        
        input_1 = '<script>alert(1);</script>'
        input_2 = '/><a href='
        xss_locator = 'javascript:/*--></title></style></textarea></script></xmp><svg/onload=\'+/"/+/onmouseover=1/+/[*/[]/+alert(1)//\'>'

        self.assertEquals(u'&#x003C;script&#x003E;alert(1);&#x003C;&#x002F;script&#x003E;', Encoder.encode_for_HTML_content(input_1))
        self.assertEquals(u'&#x002F;&#x003E;&#x003C;a href=',
            Encoder.encode_for_HTML_content(input_2))
        self.assertEquals(u'javascript:&#x002F;*--&#x003E;&#x003C;&#x002F;title&#x003E;&#x003C;&#x002F;style&#x003E;&#x003C;&#x002F;textarea&#x003E;&#x003C;&#x002F;script&#x003E;&#x003C;&#x002F;xmp&#x003E;&#x003C;svg&#x002F;onload=&#x0027;+&#x002F;&#x0022;&#x002F;+&#x002F;onmouseover=1&#x002F;+&#x002F;[*&#x002F;[]&#x002F;+alert(1)&#x002F;&#x002F;&#x0027;&#x003E;', Encoder.encode_for_HTML_content(xss_locator))

    def test_c_encode_for_HTML_attrib(self):
        """
        Tests encode_for_HTML_attrib.
        """

        attrib_single_quote = "'post context' text ®¾"
        attrib_dbl_quote = '"post context text ®¾"'
        attrib_no_quotes = '"post context text ®¾" asda\'asda\''
                
        self.assertEqual(u'&#x0027;post context&#x0027; text ®¾',Encoder.encode_for_HTML_attrib(attrib_single_quote, quoted_context=True, single_quotes=True))
        self.assertEqual(u'&#x0022;post context text ®¾&#x0022;',Encoder.encode_for_HTML_attrib(attrib_dbl_quote, quoted_context=True))
        self.assertEqual(u'&#x0022;post&#x0020;context&#x0020;text&#x0020;&#x00AE;&#x00BE;&#x0022;&#x0020;asda&#x0027;asda&#x0027;',Encoder.encode_for_HTML_attrib(attrib_no_quotes))

    def test_d_encode_for_JS_data_values(self):
        """
        Tests encode_for_JS_data_values() and escape_for_css().
        """
        val1 = "alert('test xss')"
        val2 = "javascript:alert(1)"
        val3 = "location.href='http://attacker.com'"
        
        self.assertEqual(u'alert\\x28\\x27test\\x20xss\\x27\\x29', Encoder.encode_for_JS_data_values(val1))
        self.assertEqual(u'javascript\\x3Aalert\\x281\\x29', Encoder.encode_for_JS_data_values(val2))
        self.assertEqual(u'location\\x2Ehref\\x3D\\x27http\\x3A\\x2F\\x2Fattacker\\x2Ecom\\x27', Encoder.encode_for_JS_data_values(val3))
    
    def test_e_escape_for_url_parameters(self):
        """
        Tests escape_for_url_parameters.
        """
        url_param_value = 'title<script>alert("XSS injected")</script>'
        self.assertEqual(u'title%3Cscript%3Ealert%28%22XSS%20injected%22%29%3C%2Fscript%3E', Encoder.escape_for_url_parameter_value(url_param_value))

unittest.main()