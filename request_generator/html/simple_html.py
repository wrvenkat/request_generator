from simple_html_element import SimpleHTMLElement as Element

"""
Class that houses the various HTML Tags/Elements like form, iframe, input, label etc.
"""

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
        self.setup(parent, child)

class IFrame(Element):
    def __init__(self, src='', width="500", height="500", attrs=None, parent=None, child=None):
        #attrs in attrs take precedence
        if attrs is None or len(attrs) == 0:
            if attrs is None:
                attrs = {}
            
            if 'src' not in attrs:
                attrs['src'] = src
            if 'width' not in attrs:
                attrs['width'] = width
            if 'height' not in attrs:
                attrs['height'] = height

        super(IFrame, self).__init__('iframe', attrs=attrs, parent=parent, child=child)
        self.setup(parent, child)

class Input(Element):
    class Type:
        text = "text"
        password = "password"
        file = "file"
        hidden = "hidden"
        submit = "submit"

    def __init__(self, name='', _type=Input.Type.text, value='', attrs=None, parent=None, child=None):
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
        self.setup(parent, child)

class AHref(Element):
    def __init__(self, href='', text='', attrs=None, parent=None, child=None):
        #attrs in attrs take precedence
        if attrs is None or len(attrs) == 0:
            if attrs is None:
                attrs = {}            
            if 'href' not in attrs:
                attrs['href'] = href
        
        child_text = child
        if child_text is None:
            child_text = Element(text=text)
                    
        super(AHref, self).__init__('a', attrs=attrs, parent=parent, child=child)
        self.setup(parent, child)

class Img(Element):
    def __init__(self, src='', width='20', height='20', attrs=None, parent=None, child=None):
        #attrs in attrs take precedence
        if attrs is None or len(attrs) == 0:
            if attrs is None:
                attrs = {}
            
            if 'src' not in attrs:
                attrs['src'] = src
            if 'width' not in attrs:
                attrs['type'] = width
            if 'height' not in attrs:
                attrs['value'] = height

        super(Img, self).__init__('img', attrs=attrs, parent=parent, child=child)
        self.setup(parent, child)

class Label(Element):
    def __init__(self, text='', attrs=None, parent=None, child=None):
        #child element takes precedence over 'text' arg
        child_text = child
        if child_text is None:
            child_text = Element(text=text)

        super(Label, self).__init__('label', attrs=attrs, parent=parent, child=child)
        self.setup(parent, child)

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

        super(Meta, self).__init__('meta', attrs=attrs, parent=parent, child=child)
        self.setup(parent, child)

class Title(Element):
    def __init__(self, title='', parent=None, child=None):
        #child element takes precedence over 'title' arg
        child_text = child
        if child_text is None:
            child_text = Element(text=title)
        
        super(Title, self).__init__('title', parent=parent, child=child_text)
        self.setup(parent, child)

class Head(Element):
    def __init__(self, parent=None, child=None):
        super(Head, self).__init__('head', parent=parent, child=child)
        self.setup(parent, child)

class Body(Element):
    def __init__(self, parent=None, child=None):
        super(Body, self).__init__('body', parent=parent, child=child)
        self.setup(parent, child)

class BR(Element):
    def __init__(self,parent=None, child=None):
        super(BR, self).__init__('br', parent=parent, child=child)
        self.setup(parent, child)
    
    def generate(self):
        return '<{}>'.format(self.name)