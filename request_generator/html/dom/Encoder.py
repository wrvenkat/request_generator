# -*- coding: utf-8 -*-
import unicodedata

class Encoder:
    """
    Utility class used to safely encode dangerous characters in specific contexts.

    Returns UTF-8 type hex entity encoded codepoint values for sensitive characters.

    Based on OWASP's guidance: https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.md
    """

    @classmethod
    def encode_for_HTML_content(cls, input):
        """
        UTF-8 hex entity encodes the input character
        if it is not one of the below characters.
        &, <, >, ", ', /
        """

        input = cls.get_UTF8(input)
        if len(input) == 0:
            return ''

        ampersand = cls.get_code_point('&')
        less_than = cls.get_code_point('<')
        grtr_than = cls.get_code_point('>')
        dbl_quote = cls.get_code_point('"')
        sgl_quote = cls.get_code_point("'")
        fwd_slash = cls.get_code_point('/')

        output_encoded_input = ''
        for char in input:
            char_codepoint = cls.get_code_point(char)
            replacement = cls.get_UTF8(char)

            if (char_codepoint == ampersand):
                replacement = cls.get_hex_entity(ampersand)
            elif (char_codepoint == less_than):
                replacement = cls.get_hex_entity(less_than)
            elif (char_codepoint == grtr_than):
                replacement = cls.get_hex_entity(grtr_than)
            elif (char_codepoint == dbl_quote):
                replacement = cls.get_hex_entity(dbl_quote)
            elif (char_codepoint == sgl_quote):
                replacement = cls.get_hex_entity(sgl_quote)
            elif (char_codepoint == fwd_slash):
                replacement = cls.get_hex_entity(fwd_slash)

            output_encoded_input += replacement
        
        return output_encoded_input
    
    @classmethod
    def encode_for_HTML_attrib(cls, input, quoted_context=False, single_quotes=False):
        """
        HTML Hex encodes for HTML attrib context.

        Takes,
            input = input string
            
            quoted_context = whether output encoding needs to take place inside
            a quoted_context or not. By default, no quoting is assumed.
            
            single_quotes = if quoted_context is true, single_quotes when true
            means enclosing context is inside single quotes (''). When false, it
            means enclosing context is inside double quotes ("").
        """
        input = cls.get_UTF8(input)
        if len(input) == 0:
            return ''

        single_quotes_context = False
        if quoted_context and single_quotes:
            single_quotes_context = True        
        
        encoded_output = ''
        for char in input:
            char_codepoint = cls.get_code_point(char)
            replacement = cls.get_UTF8(char)

            if quoted_context:
                if single_quotes_context:
                    single_quote_code_point = cls.get_code_point('\'')
                    if single_quote_code_point == char_codepoint:
                        replacement = cls.get_hex_entity(single_quote_code_point)
                #double quotes context
                else:
                    double_quotes_code_point = cls.get_code_point('"')
                    if double_quotes_code_point == char_codepoint:
                        replacement = cls.get_hex_entity(double_quotes_code_point)
            else:
                # hex entity encode any character that's less than 256 and not
                # alphanumeric in ASCII (includes extended ASCII as well)
                # UTF-8 supports extended ASCII                            
                small_a_code_point = Encoder.get_code_point('a')
                small_z_code_point = Encoder.get_code_point('z')
                caps_a_code_point = Encoder.get_code_point('A')
                caps_z_code_point = Encoder.get_code_point('Z')
                zero_code_point = Encoder.get_code_point(0)
                nine_code_point = Encoder.get_code_point(9)

                if not  ((char_codepoint >= small_a_code_point and char_codepoint <= small_z_code_point) or
                        (char_codepoint >= caps_a_code_point and char_codepoint <= caps_z_code_point) or
                        (char_codepoint >= zero_code_point and char_codepoint <= nine_code_point) and 
                        char_codepoint < 256):
                        replacement = cls.get_hex_entity(char_codepoint)

            encoded_output += replacement
       
        return encoded_output

    @classmethod
    def encode_for_JS_data_values(cls, input):
        """
        Encodes input into \\xHH format for use in a JS data value context enclosed
        in single quotes.

        Examples of those contexts include event handler attributes,
        JS variable assignment.
        """
        """
        See: https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.md#rule-3---javascript-escape-before-inserting-untrusted-data-into-javascript-data-values
        """

        input = cls.get_UTF8(input)
        if len(input) == 0:
            return ''
        
        encoded_output = ''
        for char in input:
            char_codepoint = cls.get_code_point(char)
            replacement = cls.get_UTF8(char)

            # \xHH encode any character that's less than 256 and not
            # alphanumeric in ASCII (includes extended ASCII as well)
            # UTF-8 supports extended ASCII            
            small_a_code_point = Encoder.get_code_point('a')
            small_z_code_point = Encoder.get_code_point('z')
            caps_a_code_point = Encoder.get_code_point('A')
            caps_z_code_point = Encoder.get_code_point('Z')
            zero_code_point = Encoder.get_code_point(0)
            nine_code_point = Encoder.get_code_point(9)

            if not  ((char_codepoint >= small_a_code_point and char_codepoint <= small_z_code_point) or
                    (char_codepoint >= caps_a_code_point and char_codepoint <= caps_z_code_point) or
                    (char_codepoint >= zero_code_point and char_codepoint <= nine_code_point) and 
                    char_codepoint < 256):
                    replacement = str('\\x{:02X}'.format(char_codepoint))

            encoded_output += replacement
       
        return encoded_output

    @classmethod
    def escape_for_css(cls, input):
        """
        Encodes input into \\xHH format for use CSS property value or 
        HTML style property.

        It's important that you only use untrusted data in a property value and not into other places in style data. You should stay away from putting untrusted data into complex properties like url, behavior, and custom (-moz-binding).
        """
        """
        See https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.md#rule-4---css-escape-and-strictly-validate-before-inserting-untrusted-data-into-html-style-property-values
        """
        return cls.encode_for_JS_data_values(input)

    @classmethod
    def escape_for_url_parameter_value(cls,input):
        """
        URL Escapes (%HH) input for safe use in URL parmater values.
        """
        """
        See https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.md#rule-5---url-escape-before-inserting-untrusted-data-into-html-url-parameter-values
        """

        input = cls.get_UTF8(input)
        if len(input) == 0:
            return ''
        
        encoded_output = ''
        for char in input:
            char_codepoint = cls.get_code_point(char)
            replacement = cls.get_UTF8(char)

            # \xHH encode any character that's less than 256 and not
            # alphanumeric in ASCII (includes extended ASCII as well)
            # UTF-8 supports extended ASCII            
            small_a_code_point = Encoder.get_code_point('a')
            small_z_code_point = Encoder.get_code_point('z')
            caps_a_code_point = Encoder.get_code_point('A')
            caps_z_code_point = Encoder.get_code_point('Z')
            zero_code_point = Encoder.get_code_point(0)
            nine_code_point = Encoder.get_code_point(9)

            if not  ((char_codepoint >= small_a_code_point and char_codepoint <= small_z_code_point) or
                    (char_codepoint >= caps_a_code_point and char_codepoint <= caps_z_code_point) or
                    (char_codepoint >= zero_code_point and char_codepoint <= nine_code_point) and 
                    char_codepoint < 256):
                    replacement = str('%{:02X}'.format(char_codepoint))

            encoded_output += replacement
       
        return encoded_output

    @classmethod
    def get_hex_entity(cls, codepoint):
        """
        Returns the hex entity equivalent for the codepoint.
        """

        try:
            codepoint = int(codepoint)
            return str('&#x{:04X};'.format(codepoint))
        except ValueError:
            raise TypeError("get_hex_entity(): Requires an input of type int.")    

    @classmethod
    def get_UTF8(cls, input=None):
        """
        Returns UTF-8 encoding of input.
        """
        
        if input is None:
            return ""

        try:
            input_length = len(input)
        except TypeError:
            # if len() doesn't apply to input, then
            # try to get the str() of input
            input_length = len(str(input))
        
        if input_length == 0:
            return ''
            #raise TypeError("get_UTF8() takes atleast one argument. (0 given)")

        #if the input is not of UNICODE type,
        #then we transform it to unicode
        if not isinstance(input, str):
            #convert the input to str
            input = str(input)
        
        return input

    @classmethod
    def get_code_point(cls,input):
        """
        Returns the NFC normalized codepoint for the input character.

        Raises TypeError.
        """

        #get UTF-8 value of input
        input = cls.get_UTF8(input)
        
        if (len(input) > 1):
            raise TypeError("get_code_point() takes exactly one argument. ({} given)".format(len(input)))

        codepoint = unicodedata.normalize('NFC', input)        
        codepoint = ord(input)        
        return codepoint
    