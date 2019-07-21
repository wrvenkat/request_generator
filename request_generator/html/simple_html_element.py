from tag import Tag
from Encoder import Encoder

class SimpleHTMLElement(Tag):
    """
    A Tag object forms the basic constructive unit of a DOM.

    A simplistic representation of an HTML/XML tag.
    """

    """
    A SimpleHTMLElement Tag has the following properties:
    1. Attributes of an element are represented as dictionaries.
    2. The 'text' of a Tag is contained in the contents attribute.
    3. When generate is called on an Element, the output is generated for 
        the subtree rooted at that Element by an appropriate generator depending
        on the type represented by _type.
    """

    class type:
        script  = "script"
        html    = "html"
        text    = "html_text"
        cdata   = "cdata"

    def __init__(self, name=None, attrs=None, text=None, cdata=None, self_closing=False, parent=None, child=None, encoder=Encoder):
        super(SimpleHTMLElement, self).__init__()
            
        #tag name
        self.name = name

        #set 'text'
        if text is not None:
            self.value = text
            self.name = ''
            self._type = self.type.text
        else:
            self.value = ''

        #attributes
        if not attrs:
            #init with empty dict
            self.attrs = {}
        elif isinstance(attrs, dict):
            self.attrs = attrs
        else:
            raise TypeError("provided attrs is not a dict type")

        #set the type
        if self.name.lower() == "script":
            self._type = self.type.script
        elif self.name and len(self.name) > 0:
            self._type = self.type.html
        
        #set the encoder object
        self._encoder = encoder

        #set if self closing or not
        self._self_closing = self_closing
        
        self.setup(parent, child)

    @property    
    def is_script(self, name=None):
        """
        Returns True if the type of an element is "script"
        """

        return self._type == Tag.type.script
    
    @property
    def string(self):
        """
        Convenience property to get the single string within this tag.

        :Return:
            String of form ClassName:type:name:value
            where, 
                1. name is present if type is self._type is self.type.html.
                value is addition of all type.text children. "None" otherwise.
                2. name is empty with value "None" if type is self.type.script.
                3. name is empty with value from self.value if type is self.type.text
                or self.type.cdata.
        """

        string = "{}:{}".format(self.__class__, self._type)

        if self._type is self.type.text or self._type is self.type.cdata:
            string += ":{}".format(self.value)
        elif self._type is self.type.script:
            string += ":None"
        elif self._type is self.type.html:
            string += ":{}".format(self.name)

            child_text = ''
            count_text_child = 0
            for child in self.children:
                if child._type is self.type.text:
                    count_text_child += 1
                    child_text += child.value
            if count_text_child <= 0:
                child_text = "None"
            string += ":{}".format(child_text)
        
        return string

    def generate_for_attrs(self):
        """
        Generates code for attributes.

        This is a generic implementation. Subclassing elements
        can override whenever required.
        """

        attr_text = ''
        for attr, attr_value in self.attrs.iteritems():
            attr_text += ' '
            attr_name_text = attr
            attr_value_text = attr_value
            if self.encoder is not None:
                # technically one's supposed to use an HTML sanitizer to
                # construct HTML tags/attr names form user input. But
                # for now, we'll go with Encoder's encode for HTML.
                attr_name_text = self.encoder.encode_for_HTML_content(attr_name_text)
                attr_value_text = self.encoder.encode_for_HTML_attrib(attr_value_text, quoted_context=True)
            attr_text += "{}=\"{}\"".format(attr_name_text, attr_value_text)        
        return attr_text

    def generate(self, indent_level=0):
        """
        Generates code for tree rooted at self.

        This is a generic implementation. Subclassing elements
        can override whenever required.
        """

        text = ''
        indent = self.get_indent(indent_level)
        #inspect self to see what type of tag were
        my_type = self._type
        if my_type == SimpleHTMLElement.type.cdata:
            text = indent+"<![CDATA[{}]]>".format(self.value)
        elif my_type == SimpleHTMLElement.type.text:
            text = self.value
            if self.encoder is not None:
                text = self.encoder.encode_for_HTML_content(text)
            text = indent+text
        elif my_type == SimpleHTMLElement.type.html:
            attr_text = self.generate_for_attrs()
            #self-closing tags do not contain text
            if self.self_closing:
                text = indent+"<{}{}/>".format(self.name, attr_text)
            else:
                text = indent+"<{}{}>".format(self.name, attr_text)
                children_text = self.generate_from_children(indent_level+1)
                if children_text and len(children_text):
                    text += children_text+"\r\n"
                    text += indent+"</{}>".format(self.name)
                else:
                    text += "</{}>".format(self.name)
                
        return text
