from simple_html_element import SimpleHTMLElement as Element

"""
Class that houses the various HTML Tags/Elements like form, iframe, input, label etc.
"""

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
        if child is None:
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
    
    def generate(self, indent_level=0):
        indent = self.get_indent(indent_level)
        return indent+'<{}>'.format(self.name)