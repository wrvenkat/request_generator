from simple_html_element import SimpleHTMLElement as Element

"""
Class that houses the various HTML Tags/Elements like form, iframe, input, label etc.
"""

class Font(Element):
    class Color:
        red     = 'red'
        blue    = 'blue'
        green   = 'yellow'
        #etc

    def __init__(self,text='', color=Color.red, attrs=None, parent=None):
        """
        text    - text to which the font applies to.
        color   - color property of the style attribute. Default is red.
        """
        if attrs is None or len(attrs) == 0:
            if attrs is None:
                attrs = {}

        if 'color' not in attrs:
            attrs['style'] = 'color:'+color
        
        text_child = Text(text=text)
        super(Font, self).__init__('font', attrs=attrs, parent=parent, child=text_child)

class Button(Element):
    def __init__(self,text='Click Me!', onclick='', attrs=None, parent=None):
        """
        text    - text that goes on the button.
        onlick  - function name to be called
        """
        if attrs is None or len(attrs) == 0:
            if attrs is None:
                attrs = {}

        if 'onclick' not in attrs:
            attrs['onclick'] = onclick
        
        text_child = Text(text=text)
        super(Button, self).__init__('button', attrs=attrs, parent=parent, child=text_child)

class Script(Element):
    """
    Creates a <script> element where the default value for the
    type attribute is Type.javascript.

    By default script elements don't have any encoding for text
    elements
    """

    class Type:
        javascript = "text/javascript"
        vbscript = "text/vbscript"

    def __init__(self, type=Type.javascript):
        attrs = {
            'type' : type
        }
        #no encoder for a script tag as it requires that the code be properly
        #set in the DOM and doesn't encode during code generation.
        super(Script, self).__init__('script', attrs=attrs, encoder=None)        

class Text(Element):
    def __init__(self,text='', parent=None, child=None):
        super(Text, self).__init__(text=text, parent=parent, child=child)

class Form(Element):
    def __init__(self,action='', method='GET', attrs=None, parent=None, child=None):
        #the action and method if present in attrs, overrides the one provided/default
        if attrs is None or len(attrs) == 0:
            if attrs is None:
                attrs = {}
            
        if 'method' not in attrs:
            attrs['method'] = method
        if 'action' not in attrs:
            attrs['action'] = action

        super(Form, self).__init__('form', attrs=attrs, parent=parent, child=child)

class IFrame(Element):
    def __init__(self, src='', width="500", height="500", attrs=None, parent=None, child=None):
        #attrs in attrs take precedence
        if attrs is None:
            attrs = {}
        
        if 'src' not in attrs:
            attrs['src'] = src
        if 'width' not in attrs:
            attrs['width'] = width
        if 'height' not in attrs:
            attrs['height'] = height        
        super(IFrame, self).__init__('iframe', attrs=attrs, parent=parent, child=child)

class Input(Element):
    class Type:
        text = "text"
        password = "password"
        file = "file"
        hidden = "hidden"
        submit = "submit"

    def __init__(self, name='', _type=Type.text, value='', attrs=None, parent=None, child=None):
        """
        Default type is 'text'.
        """

        #attrs in attrs take precedence
        if attrs is None or len(attrs) == 0:
            if attrs is None:
                attrs = {}
            
        if 'name' not in attrs:
            attrs['name'] = name
        if 'type' not in attrs:
            attrs['type'] = _type
        if 'value' not in attrs:
            attrs['value'] = value

        super(Input, self).__init__('input', attrs=attrs, parent=parent, child=child)

class AHref(Element):
    def __init__(self, href='', text='', attrs=None, parent=None):
        #attrs in attrs take precedence
        if attrs is None or len(attrs) == 0:
            if attrs is None:
                attrs = {}
            if 'href' not in attrs:
                attrs['href'] = href

        if text is None:
            text=''
        text_child = Text(text=text)
                    
        super(AHref, self).__init__('a', attrs=attrs, parent=parent, child=text_child)        

class Img(Element):
    def __init__(self, src='', width='20', height='20', attrs=None, parent=None, child=None):
        #attrs in attrs take precedence
        if attrs is None:
            attrs = {}
            
        if 'src' not in attrs:
            attrs['src'] = src
        if 'width' not in attrs:
            attrs['type'] = width
        if 'height' not in attrs:
            attrs['value'] = height

        super(Img, self).__init__('img', attrs=attrs, parent=parent, child=child)

class Label(Element):
    def __init__(self, text='', attrs=None, parent=None, child=None):
        #child element takes precedence over 'text' arg
        text_child = child
        if text_child is None:
            text_child = Text(text=text)

        super(Label, self).__init__('label', attrs=attrs, parent=parent, child=text_child)        

class Heading(Element):
    class size:
        level1 = 1
        level2 = 2
        level3 = 3
        level4 = 4
        level5 = 5
        level6 = 6

    def __init__(self, size=size.level3, text='', parent=None):
        """
        Default size is 3.
        """

        if size is None or not isinstance(size, int):
            size = size.level3
        _name = 'h{}'.format(size)

        #since Heading represents something, it's best
        #to have an empty place holder when no 'text'
        #is provided
        if text is None or len(text) == 0:
            text = 'empty_heading_value'
        text_child = Text(text=text)

        super(Heading, self).__init__(_name, parent=parent, child=text_child)

class Meta(Element):
    def __init__(self, name='', content='', attrs=None, parent=None, child=None):
        #attrs in attrs take precedence
        if attrs is None or len(attrs) == 0:
            if attrs is None:
                attrs = {}
            
        if 'name' not in attrs:
            attrs['name'] = name
        if 'content' not in attrs:
            attrs['content'] = content

        super(Meta, self).__init__('meta', attrs=attrs, self_closing=True, parent=parent, child=child)        

class Title(Element):
    def __init__(self, title='', parent=None, child=None):
        #child element takes precedence over 'title' arg
        text_child = child
        if text_child is None:
            text_child = Text(text=title)
        
        super(Title, self).__init__('title', parent=parent, child=text_child)        

class Head(Element):
    def __init__(self, text='',parent=None, child=None):
        if child is None and len(text)>0:
            child = Text(text=text)
        super(Head, self).__init__('head', parent=parent, child=child)

class Body(Element):
    def __init__(self, parent=None, child=None):
        super(Body, self).__init__('body', parent=parent, child=child)        

class HTML(Element):
    def __init__(self, child=None):
        super(HTML, self).__init__('html', child=child)        

class BR(Element):
    def __init__(self,parent=None, child=None):
        super(BR, self).__init__('br', parent=parent, child=child)        
    
    def generate(self, indent_level=0, encode=None):
        indent = self.get_indent(indent_level)
        return indent+'<{}>'.format(self.name)