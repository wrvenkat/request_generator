import re
from tag import Tag

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

    def __init__(self, name=None, attrs=None, text=None, cdata=None, self_closing=False, parent=None, child=None):
        super(SimpleHTMLElement, self).__init__()
            
        #tag name
        self.name = name

        #set 'text'
        if text:
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
        attr_text = ''
 
        for attr, attr_value in self.attrs.iteritems():
            attr_text += ' '
            attr_text += "{}=\"{}\"".format(attr, attr_value)
        
        return attr_text

    #TODO: Fix how the code is generated
    def generate(self, indent_level=0, prettify=True):
        """
        Generates code for tree rooted at self.
        """

        text = ''
        indent = self._get_indent(indent_level)
        #inspect self to see what type of tag were
        my_type = self._type
        if my_type == Tag.type.cdata:
            text = indent+"<![CDATA[{}]]>".format(self.value)
        elif my_type == Tag.type.text:
            text = indent+self.value
        else:
            #self-closing tags do not contain text
            attr_text = self.generate_for_attrs()
            if self.self_closing:
                text = indent+"<{}{}/>".format(self.name, attr_text)
            else:
                text = indent+"<{}{}>".format(self.name, attr_text)
                children_text = self.generate_from_children(indent_level+1, prettify=prettify)
                if children_text and len(children_text):
                    text += children_text+"\r\n"
                    text += indent+"</{}>".format(self.name)
                else:
                    text += "</{}>".format(self.name)
                
        return text

    # Methods for supporting CSS selectors.        
    tag_name_re = re.compile('^[a-zA-Z0-9][-.a-zA-Z0-9:_]*$')

    # /^([a-zA-Z0-9][-.a-zA-Z0-9:_]*)\[(\w+)([=~\|\^\$\*]?)=?"?([^\]"]*)"?\]$/
    #   \---------------------------/  \---/\-------------/    \-------/
    #     |                              |         |               |
    #     |                              |         |           The value
    #     |                              |    ~,|,^,$,* or =
    #     |                           Attribute
    #    Tag
    attribselect_re = re.compile(
        r'^(?P<tag>[a-zA-Z0-9][-.a-zA-Z0-9:_]*)?\[(?P<attribute>[\w-]+)(?P<operator>[=~\|\^\$\*]?)' +
        r'=?"?(?P<value>[^\]"]*)"?\]$'
        )
    
    def _attr_value_as_string(self, value, default=None):
        """Force an attribute value into a string representation.

        A multi-valued attribute will be converted into a
        space-separated stirng.
        """
        value = self.get(value, default)
        if isinstance(value, list) or isinstance(value, tuple):
            value =" ".join(value)
        return value
  
    def _tag_name_matches_and(self, function, tag_name):
        if not tag_name:
            return function
        else:
            def _match(tag):
                return tag.name == tag_name and function(tag)
            return _match
    
    def _attribute_checker(self, operator, attribute, value=''):
        """Create a function that performs a CSS selector operation.

        Takes an operator, attribute and optional value. Returns a
        function that will return True for elements that match that
        combination.
        """
        if operator == '=':
            # string representation of `attribute` is equal to `value`
            return lambda el: el._attr_value_as_string(attribute) == value
        elif operator == '~':
            # space-separated list representation of `attribute`
            # contains `value`
            def _includes_value(element):
                attribute_value = element.get(attribute, [])
                if not isinstance(attribute_value, list):
                    attribute_value = attribute_value.split()
                return value in attribute_value
            return _includes_value
        elif operator == '^':
            # string representation of `attribute` starts with `value`
            return lambda el: el._attr_value_as_string(
                attribute, '').startswith(value)
        elif operator == '$':
            # string represenation of `attribute` ends with `value`
            return lambda el: el._attr_value_as_string(
                attribute, '').endswith(value)
        elif operator == '*':
            # string representation of `attribute` contains `value`
            return lambda el: value in el._attr_value_as_string(attribute, '')
        elif operator == '|':
            # string representation of `attribute` is either exactly
            # `value` or starts with `value` and then a dash.
            def _is_or_starts_with_dash(element):
                attribute_value = element._attr_value_as_string(attribute, '')
                return (attribute_value == value or attribute_value.startswith(
                        value + '-'))
            return _is_or_starts_with_dash
        else:
            return lambda el: el.has_attr(attribute)

    # CSS selector code
    _selector_combinators = ['>', '+', '~']
    _select_debug = False
    
    def select_one(self, selector):
        """Perform a CSS selection operation on the current element."""
        value = self.select(selector, limit=1)
        if value:
            return value[0]
        return None
    
    def select(self, selector, _candidate_generator=None, limit=None):
        """Perform a CSS selection operation on the current element."""

        # Handle grouping selectors if ',' exists, ie: p,a
        if ',' in selector:
            context = []
            for partial_selector in selector.split(','):
                partial_selector = partial_selector.strip()
                if partial_selector == '':
                    raise ValueError('Invalid group selection syntax: %s' % selector)
                candidates = self.select(partial_selector, limit=limit)
                for candidate in candidates:
                    if candidate not in context:
                        context.append(candidate)

                if limit and len(context) >= limit:
                    break
            return context

        tokens = selector.split()
        current_context = [self]

        if tokens[-1] in self._selector_combinators:
            raise ValueError(
                'Final combinator "%s" is missing an argument.' % tokens[-1])

        if self._select_debug:
            print 'Running CSS selector "%s"' % selector

        for index, token in enumerate(tokens):
            new_context = []
            new_context_ids = set([])

            if tokens[index-1] in self._selector_combinators:
                # This token was consumed by the previous combinator. Skip it.
                if self._select_debug:
                    print '  Token was consumed by the previous combinator.'
                continue

            if self._select_debug:
                print ' Considering token "%s"' % token
            recursive_candidate_generator = None
            tag_name = None

            # Each operation corresponds to a checker function, a rule
            # for determining whether a candidate matches the
            # selector. Candidates are generated by the active
            # iterator.
            checker = None

            m = self.attribselect_re.match(token)
            if m is not None:
                # Attribute selector
                tag_name, attribute, operator, value = m.groups()
                checker = self._attribute_checker(operator, attribute, value)

            elif '#' in token:
                # ID selector
                tag_name, tag_id = token.split('#', 1)
                def id_matches(tag):
                    return tag.get('id', None) == tag_id
                checker = id_matches

            elif '.' in token:
                # Class selector
                tag_name, klass = token.split('.', 1)
                classes = set(klass.split('.'))
                def classes_match(candidate):
                    return classes.issubset(candidate.get('class', []))
                checker = classes_match

            elif ':' in token:
                # Pseudo-class
                tag_name, pseudo = token.split(':', 1)
                if tag_name == '':
                    raise ValueError(
                        "A pseudo-class must be prefixed with a tag name.")
                pseudo_attributes = re.match('([a-zA-Z\d-]+)\(([a-zA-Z\d]+)\)', pseudo)
                found = []
                if pseudo_attributes is None:
                    pseudo_type = pseudo
                    pseudo_value = None
                else:
                    pseudo_type, pseudo_value = pseudo_attributes.groups()
                if pseudo_type == 'nth-of-type':
                    try:
                        pseudo_value = int(pseudo_value)
                    except:
                        raise NotImplementedError(
                            'Only numeric values are currently supported for the nth-of-type pseudo-class.')
                    if pseudo_value < 1:
                        raise ValueError(
                            'nth-of-type pseudo-class value must be at least 1.')
                    class Counter(object):
                        def __init__(self, destination):
                            self.count = 0
                            self.destination = destination

                        def nth_child_of_type(self, tag):
                            self.count += 1
                            if self.count == self.destination:
                                return True
                            if self.count > self.destination:
                                # Stop the generator that's sending us
                                # these things.
                                raise StopIteration()
                            return False
                    checker = Counter(pseudo_value).nth_child_of_type
                else:
                    raise NotImplementedError(
                        'Only the following pseudo-classes are implemented: nth-of-type.')

            elif token == '*':
                # Star selector -- matches everything
                pass
            elif token == '>':
                # Run the next token as a CSS selector against the
                # direct children of each tag in the current context.
                recursive_candidate_generator = lambda tag: tag.children
            elif token == '~':
                # Run the next token as a CSS selector against the
                # siblings of each tag in the current context.
                recursive_candidate_generator = lambda tag: tag.next_siblings
            elif token == '+':
                # For each tag in the current context, run the next
                # token as a CSS selector against the tag's next
                # sibling that's a tag.
                def next_tag_sibling(tag):
                    yield tag.find_next_sibling(True)
                recursive_candidate_generator = next_tag_sibling

            elif self.tag_name_re.match(token):
                # Just a tag name.
                tag_name = token
            else:
                raise ValueError(
                    'Unsupported or invalid CSS selector: "%s"' % token)
            if recursive_candidate_generator:
                # This happens when the selector looks like  "> foo".
                #
                # The generator calls select() recursively on every
                # member of the current context, passing in a different
                # candidate generator and a different selector.
                #
                # In the case of "> foo", the candidate generator is
                # one that yields a tag's direct children (">"), and
                # the selector is "foo".
                next_token = tokens[index+1]
                def recursive_select(tag):
                    if self._select_debug:
                        print '    Calling select("%s") recursively on %s %s' % (next_token, tag.name, tag.attrs)
                        print '-' * 40
                    for i in tag.select(next_token, recursive_candidate_generator):
                        if self._select_debug:
                            print '(Recursive select picked up candidate %s %s)' % (i.name, i.attrs)
                        yield i
                    if self._select_debug:
                        print '-' * 40
                _use_candidate_generator = recursive_select
            elif _candidate_generator is None:
                # By default, a tag's candidates are all of its
                # children. If tag_name is defined, only yield tags
                # with that name.
                if self._select_debug:
                    if tag_name:
                        check = "[any]"
                    else:
                        check = tag_name
                    print '   Default candidate generator, tag name="%s"' % check
                if self._select_debug:
                    # This is redundant with later code, but it stops
                    # a bunch of bogus tags from cluttering up the
                    # debug log.
                    def default_candidate_generator(tag):
                        for child in tag.descendants:
                            if not isinstance(child, Tag):
                                continue
                            if tag_name and not child.name == tag_name:
                                continue
                            yield child
                    _use_candidate_generator = default_candidate_generator
                else:
                    _use_candidate_generator = lambda tag: tag.descendants
            else:
                _use_candidate_generator = _candidate_generator

            count = 0
            for tag in current_context:
                if self._select_debug:
                    print "    Running candidate generator on %s %s" % (
                        tag.name, repr(tag.attrs))
                for candidate in _use_candidate_generator(tag):
                    if not isinstance(candidate, Tag):
                        continue
                    if tag_name and candidate.name != tag_name:
                        continue
                    if checker is not None:
                        try:
                            result = checker(candidate)
                        except StopIteration:
                            # The checker has decided we should no longer
                            # run the generator.
                            break
                    if checker is None or result:
                        if self._select_debug:
                            print "     SUCCESS %s %s" % (candidate.name, repr(candidate.attrs))
                        if id(candidate) not in new_context_ids:
                            # If a tag matches a selector more than once,
                            # don't include it in the context more than once.
                            new_context.append(candidate)
                            new_context_ids.add(id(candidate))
                            if limit and len(new_context) >= limit:
                                break
                    elif self._select_debug:
                        print "     FAILURE %s %s" % (candidate.name, repr(candidate.attrs))


            current_context = new_context

        if self._select_debug:
            print "Final verdict:"
            for i in current_context:
                print " %s %s" % (i.name, i.attrs)
        return current_context

