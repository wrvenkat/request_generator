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

        input = cls._get_UTF8(input)

        ampersand = cls._get_code_point('&')
        less_than = cls._get_code_point('<')
        grtr_than = cls._get_code_point('>')
        dbl_quote = cls._get_code_point('"')
        sgl_quote = cls._get_code_point("'")
        fwd_slash = cls._get_code_point('/')

        output_encoded_input = ''
        for char in input:
            char_codepoint = cls._get_code_point(char)
            replacement = char

            if (char_codepoint == ampersand):
                replacement = cls._get_hex_entity(ampersand)
            elif (char_codepoint == less_than):
                replacement = cls._get_hex_entity(less_than)
            elif (char_codepoint == grtr_than):
                replacement = cls._get_hex_entity(grtr_than)
            elif (char_codepoint == dbl_quote):
                replacement = cls._get_hex_entity(dbl_quote)
            elif (char_codepoint == sgl_quote):
                replacement = cls._get_hex_entity(sgl_quote)
            elif (char_codepoint == fwd_slash):
                replacement = cls._get_hex_entity(fwd_slash)

            output_encoded_input += replacement
        
        return output_encoded_input
    
    @classmethod
    def encode_for_HTML_attrib(cls, input):
        """
        HTML Hex encodes for HTML attrib context.
        """
        pass

    @classmethod
    def _get_hex_entity(cls, codepoint):
        """
        Returns the hex entity equivalent for the codepoint.
        """

        try:
            codepoint = int(codepoint)
            return unicode('&#x{:04X};'.format(codepoint))
        except ValueError:
            raise TypeError("_getHexEntity(): Requires an input of type int.")    

    @classmethod
    def _get_UTF8(cls, input):
        """
        Returns UTF-8 encoding of input.
        """

        if (len(input) == 0):
            raise TypeError("_getUTF8() takes atleast one argument. (0 given)")

        #if the input is not of UNICODE type,
        #then we transform it to unicode
        if not isinstance(input, unicode):
            #convert the input to bytes and
            #decode that as UTF-8
            input = bytes(input).decode('UTF-8')
        
        return input

    @classmethod
    def _get_code_point(cls,input):
        """
        Returns the NFC normalized codepoint for the input character.

        Raises TypeError.
        """
        
        if (len(input) == 0):
            return 0

        #if the input is not of UNICODE type,
        #then we transform it to unicode
        if not isinstance(input, unicode):
            #convert the input to bytes and
            #decode that as UTF-8
            input = bytes(input).decode('UTF-8')
        
        if (len(input) > 1):
            raise TypeError("getCodePoint() takes exactly one argument. ({} given)".format(len(input)))

        codepoint = unicodedata.normalize('NFC', input)
        codepoint = ord(input)        
        return codepoint
    