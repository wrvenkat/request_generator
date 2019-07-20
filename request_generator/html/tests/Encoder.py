# -*- coding: utf-8 -*-
from ..Encoder import Encoder
import unittest

class EncoderTest(unittest.TestCase):

    def test_a_getUTF8(self):
        """
        Tests _getUTF8.
        """

        #input is an str that's valid in
        #Windows-1252 alphabets
        #See: https://en.wikipedia.org/wiki/Windows-1252
        non_utf8_input_str = 'ÀÁÂÃÄÅ'
        utf8_str = Encoder._get_UTF8(non_utf8_input_str)
        self.assertTrue(isinstance(utf8_str, unicode))

        utf8_compatible_str = u'Ångström'
        utf8_str = Encoder._get_UTF8(utf8_compatible_str)
        self.assertTrue(isinstance(utf8_str, unicode))

        with self.assertRaises(TypeError):
            Encoder._get_UTF8('')
    
    def test_b_getHexEntity(self):
        """
        Tests _getCodePoint and getHexEntity.
        """

        codepoint = Encoder._get_code_point(u'ç')
        self.assertEquals(u'&#x00E7;', Encoder._get_hex_entity(codepoint))

    def test_c_encode_for_HTML_content(self):
        
        input_1 = '<script>alert(1);</script>'
        input_2 = '/><a href='
        xss_locator = 'javascript:/*--></title></style></textarea></script></xmp><svg/onload=\'+/"/+/onmouseover=1/+/[*/[]/+alert(1)//\'>'

        self.assertEquals(u'&#x003C;script&#x003E;alert(1);&#x003C;&#x002F;script&#x003E;', Encoder.encode_for_HTML_content(input_1))
        self.assertEquals(u'&#x002F;&#x003E;&#x003C;a href=',
            Encoder.encode_for_HTML_content(input_2))
        self.assertEquals(u'javascript:&#x002F;*--&#x003E;&#x003C;&#x002F;title&#x003E;&#x003C;&#x002F;style&#x003E;&#x003C;&#x002F;textarea&#x003E;&#x003C;&#x002F;script&#x003E;&#x003C;&#x002F;xmp&#x003E;&#x003C;svg&#x002F;onload=&#x0027;+&#x002F;&#x0022;&#x002F;+&#x002F;onmouseover=1&#x002F;+&#x002F;[*&#x002F;[]&#x002F;+alert(1)&#x002F;&#x002F;&#x0027;&#x003E;', Encoder.encode_for_HTML_content(xss_locator))

unittest.main()