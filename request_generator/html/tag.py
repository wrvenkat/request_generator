import re
import warnings

DEFAULT_OUTPUT_ENCODING = 'utf-8'

#Tabs or spaces
SPACES=True

class Tag(object):
    """
    A Tag object forms the basic constructive unit of a DOM.

    A simplistic representation of an HTML/XML tag.
    """

    """
    An HTML Tag has the following properties:
    1. Attributes of a Tag are represented as dictionaries.
    2. The 'text' of a Tag is contained in the contents attribute.
    3. When generate/prettify is called on an Tag, the output is generated
        by an appropriate generator depending on the type represented by _type.

    Sample tree:
    ------------
    |------------------| -----> |----------|
    | name = A         |        | name = D |
    | contents = [B,C] |        ------------
    | next_sib = D     |
    | prev_sib = E     |
    --------------------
        |
        |
       |---------|
       | name = B| 
       -----------
        |
        |
       |---------|
       | name = C|
       -----------

    """

    class type:
        script  = "script"
        html    = "html"
        text    = "html_text"
        cdata   = "cdata"
   
    def __init__(self, name=None, attrs=None, text=None, cdata=None, self_closing=False, parent=None, child=None):
        #namespace attribute. Just incase we require it.
        self.namespace = None

        #tag name
        #Note that special names can be
        #CData and text
        self.name = name
        #CData and text types have contents in value
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
        self.self_closing = self_closing
                    
        #tree info
        self._parent = None
        self._next_sibling = None
        self._previous_sibling = None
        #current list of direct children
        self.contents = []
        
        #setup self's position in the tree
        self.setup(parent, child)

    @property    
    def _is_script(self, name=None):
        """
        Returns True if the type of an element is "script"
        """

        return self._type == Tag.type.script
    
    def index(self, element):
        """
        Find the index of a child by identity, not value. Avoids issues with
        tag.contents.index(element) getting the index of equal elements.
        """
        for i, child in enumerate(self.children):
            if child is element:
                return i
        raise ValueError("element not in subtree")

    #PARTIALLY DONE
    #TODO: Change the return value types.
    def _formatter_for_name(self, name):
        """
        Look up a formatter function based on the tag name.
        """

        if self._is_script:
            return 1
        else:
            return 2

    #Tree manipulation operations    
    def setup(self, parent=None, child=None,
              previous_sibling=None, next_sibling=None):
        """
        Sets up the initial relations between self and
        other elements.
        """

        if self.parent is not None:
            raise ValueError("Cannot replace current parent."
            "To change parent, manipulate current parent's children or extract and append as child"
            "to target parent.")
        elif parent is not None and self.parent is None:
            self.parent = parent

        #append child to self's children
        if child:
            self.append(child)
        
        if next_sibling and self._next_sibling:
            self._next_sibling._previous_sibling = next_sibling            
            next_sibling._next_sibling = self._next_sibling
            self._next_sibling = next_sibling
            next_sibling._previous_sibling = self
        elif next_sibling and not self._next_sibling:
            self._next_sibling = next_sibling
            next_sibling._previous_sibling = self
        
        if previous_sibling and self._previous_sibling:
            self._previous_sibling._next_sibling = previous_sibling
            previous_sibling._previous_sibling = self._previous_sibling
            previous_sibling._next_sibling = self
            self._previous_sibling = previous_sibling
        elif previous_sibling and not self._previous_sibling:
            self._previous_sibling = previous_sibling
            previous_sibling._next_sibling = self

    def replace_with(self, replacement):
        """
        Replace self with replacement.
        """

        if replacement is self:
            return

        if replacement is self.parent:
            #QUESTION: Why not?
            raise ValueError("Cannot replace an element with its immediate parent.")
        
        if replacement._previous_sibling or replacement._next_sibling:
            raise ValueError("Replacement cannot have siblings.")
        
        if replacement.contents:
            raise ValueError("Replacemenet element must be an individual and not a tree.")
            
        my_index = self.parent.index(self)
        #insert at my_index
        self.parent.insert(replacement, my_index)

        #copy children over
        replacement.contents = self.contents
        #exatract self
        self.extract()

        return self
    
    def unwrap(self):
        """
        Extracts self and promotes self's children to the same level as self.
        """
        my_parent = self.parent
        if not self.parent:
            raise ValueError(
                "Cannot replace an element with its contents when that"
                "element is not part of a tree.")
        my_index = self.parent.index(self)

        #the children get promoted to be the parent level siblings
        for i,child in enumerate(self):
            my_parent.insert(child, my_index+i)

        #extract the subtree rooted at self
        self.extract()
        #unlink children
        del self.contents[:]

        return self
    
    def wrap_with(self, wrapper):
        """
        Wrap's self with wrapper.

        Returns the wrapper.
        """

        my_index = self.parent.index(self)
        my_parent = self.parent

        #extract self
        self.extract()
        #insert wrapper at my_index
        my_parent.insert(wrapper, my_index)
        #self becomes first child of wrapper
        wrapper.insert(self, 0)
        return wrapper
    
    def extract(self):
        """
        Rips self out of the current tree including the children.
        
        As a result, there's another sub-tree rooted at self.
        """

        if not self.parent and (self.next or self.previous or len(self.contents)):
            raise ValueError("Cannot extract the root of a tree.")
        #if I'm an individual Tag, then I'm already "extracted"
        elif not self.parent and not self.next and not self.previous and not len(self.contents):
            return self

        #re-link our siblings and unlink self from the siblings
        if self._previous_sibling is not None:
            self._previous_sibling._next_sibling = self._next_sibling        
        if self._next_sibling is not None:
            self._next_sibling._previous_sibling = self._previous_sibling

        self._previous_sibling = None
        self._next_sibling = None
        self.parent = None

        return self
    
    def insert(self, new_child, position=None):
        """
        Inserts new_child into tree at position from tree root self.

        By default, appends as the last child of self.

        Also adjusts new_child's sibling relationship.
        """

        if new_child is None:
            raise ValueError("Cannot insert None into a tag.")
        if new_child is self:
            raise ValueError("Cannot insert a tag into itself.")
        if isinstance(new_child, basestring):
            new_child = Tag(text=new_child)
        
        #if a -ve position then insert at head
        if position and position < 0:
            position = 0
        elif not position:
            position = len(self.contents)

        position = min(position, len(self.contents))
        
        if hasattr(new_child, 'parent') and new_child.parent is not None:
            # We're 'inserting' an element that's already one
            # of this object's children.
            if new_child.parent is self:
                current_index = self.index(new_child)
                if current_index < position:
                    # We're moving this element further down the list
                    # of this object's children. That means that when
                    # we extract this element, our target index will
                    # jump down one.
                    position -= 1
            new_child.extract()

        new_child._parent = self
        current_child = None

        #fix the chain of siblings
        if len(self.contents):

            #insert new_child after
            insert_after = False

            #if insert at head
            if position == 0:
                current_child = self.contents[position]                
            #if insert at tail
            elif position == len(self.contents):
                current_child = self.contents[len(self.contents)-1]
                insert_after = True
            else:
                current_child = self.contents[position]

            if insert_after:
                current_child._next_sibling = new_child
                new_child._previous_sibling = current_child
            else:
                new_child._next_sibling = current_child
                new_child._previous_sibling = current_child._previous_sibling
                if current_child._previous_sibling is not None:
                    current_child._previous_sibling._next_sibling = new_child                
                current_child._previous_sibling = new_child                
                
        self.contents.insert(position, new_child)
    
    def append(self, tag):
        """Appends the given tag to the contents of this tag."""
        
        self.insert(tag)
    
    def insert_before(self, predecessor):
        """
        Makes the given element the immediate previous sibling of self.

        The two elements will have the same parent, and the given element
        will be immediately before self.
        """

        if self is predecessor:
            raise ValueError("Can't insert an element before itself.")
        parent = self.parent
        if parent is None:
            raise ValueError("Element has no parent, so 'before' has no meaning.")
        
        # Extract first so that the index won't be screwed up if they
        # are siblings.
        if isinstance(predecessor, Tag):
            predecessor.extract()
        index = parent.index(self)
        parent.insert(predecessor, index)
    
    def insert_after(self, successor):
        """Makes the given element the immediate successor of this one.

        The two elements will have the same parent, and the given element
        will be immediately after this one.
        """

        if self is successor:
            raise ValueError("Can't insert an element after itself.")
        parent = self.parent
        if parent is None:
            raise ValueError("Element has no parent, so 'after' has no meaning.")
        
        # Extract first so that the index won't be screwed up if they
        # are siblings.
        if isinstance(successor, Tag):
            successor.extract()
        index = parent.index(self)
        parent.insert(successor, index+1)

    @property
    def parent(self):
        return self._parent
        
    @parent.setter
    def parent(self, my_parent):
        if my_parent is not None:
            self._parent = my_parent
            #update the parent's children list
            self._parent.contents.append(self)
        #if my_parent is None, then it means we need
        #to remove self from self._parent's children
        else:
            my_index = self.parent.index(self)
            self.parent.contents.pop(my_index)
            self._parent = None
    
    @property
    def next(self):
        return self._next_sibling
    
    @property
    def previous(self):
        return self._previous_sibling

    #GENERATORS    
    @property
    def next_siblings(self):
        """
        Generator that yields all of self's younger siblings starting with the earliest.
        """
        i = self._next_sibling
        while i is not None:
            yield i
            i = i._next_sibling
    
    @property
    def previous_siblings(self):
        """
        Generator that yields all of self's elder siblings starting with the earliest.
        """
        i = self._previous_sibling
        while i is not None:
            yield i
            i = i._previous_sibling
    
    @property
    def parents(self):
        """
        Generator that yields all of self's parent starting with the earliest.
        """

        i = self.parent
        while i is not None:
            yield i
            i = i.parent

    @property
    def descendants(self):
        """
        Iterator that does a DFS for all descendants recusrsively.
        """

        #yield first from children
        for child in self.contents:
            yield child
            for grand__child in child.descendants:
                yield grand__child
    
    @property
    def children(self):
        return self
        
    def _last_descendant(self, accept_self=True):
        """
        Finds the last direct child of this element.
        """

        last_child = self.contents[len(self.contents)-1]
        return last_child
 
    @property
    def is_empty_element(self):
        """Is this tag an empty-element tag? (aka a self-closing tag)

        A tag that has contents is never an empty-element tag.

        A tag that has no contents may or may not be an empty-element
        tag. It depends on the builder used to create the tag. If the
        builder has a designated list of empty-element tags, then only
        a tag whose name shows up in that list is considered an
        empty-element tag.

        If the builder has no designated list of empty-element tags,
        then any tag with no contents is an empty-element tag.
        """
        return len(self.contents) == 0 and self.self_closing

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
    
    def decompose(self):
        """
        Recursively destroys the contents of tree rooted at self.
        """
        self.extract()
        i = self

        #decompose children
        for child in i.children:
            child.decompose()
        del i.contents[:]

        #decompose self
        i.__dict__.clear()
    
    def clear_children(self, decompose=False):
        """
        Extract all children. If decompose is True, decompose instead.
        """

        if decompose:
            for element in self.contents[:]:
                if isinstance(element, Tag):
                    element.decompose()
                else:
                    element.extract()
        else:
            for element in self.contents[:]:
                element.extract()
    
    def get(self, key, default=None):
        """
        Returns the value of the 'key' attribute for the tag, or
        the value given for 'default' if it doesn't have that
        attribute.
        """
        return self.attrs.get(key, default)
    
    def has_attr(self, key):
        return key in self.attrs
    
    #Python fundamentals    
    def __copy__(self):
        """A copy of a Tag is a new Tag, unconnected to the parse tree.
        Its contents are a copy of the old Tag's contents.
        """
        clone = Tag(name=self.name, attrs=self.attrs)
        for attr in ('can_be_empty_element', 'hidden'):
            setattr(clone, attr, getattr(self, attr))
        for child in self.contents:
            clone.append(child.__copy__())
        return clone

    def __hash__(self):
        return str(self).__hash__()
    
    def __getitem__(self, key):
        """tag[key] returns the value of the 'key' attribute for the tag,
        and throws an exception if it's not there."""
        return self.attrs[key]
    
    def __iter__(self):
        """
        Iterating over a tag iterates over (a copy of)its children.
        """

        # return iter() to make the purpose of the method clear
        #also iterate over a copy since there's a legitimate possibility
        #that the loop that iterates with self.children might also be
        #modifying self.contents
        return iter(list(self.contents))
    
    def __len__(self):
        "The length of a tag is the length of its list of contents."
        return len(self.contents)
    
    def __contains__(self, x):
        """
        Returns True if x is a direct child of self.
        """
        return x in self.contents
    
    def __setitem__(self, key, value):
        """Setting tag[key] sets the value of the 'key' attribute for the
        tag."""
        self.attrs[key] = value
    
    def __delitem__(self, key):
        "Deleting tag[key] deletes all 'key' attributes for the tag."
        self.attrs.pop(key, None)
    
    def is_equal(self, other):
        """
        Compares self with another tag to see if the individual Tag has the same
        properties as the other exluding the relationships.
        """

        if self is other:
            return True
        if not isinstance(other, Tag):
            return False
        #compare only the properties and not the relationship
        if (not hasattr(other, 'name') or
            not hasattr(other, 'attrs') or
            not hasattr(other, 'contents') or
            self.name != other.name or
            self._type != other._type or
            self.attrs != other.attrs or
            self.self_closing != other.self_closing):
            return False
        return True

    def __eq__(self, other):
        """
        Returns true iff this tag has the same name, the same attributes,
        and the same contents (recursively) as the given tag.
        """

        if self.is_equal(other):
            if self is other:
                return True
            #if the properties match, compare the
            #relationship excluding my parents
            if len(self) != len(other):
                return False
        else:
            return False
        
        for i, my_child in enumerate(self.contents):
            if my_child != other.contents[i]:
                return False
        return True
    
    def __ne__(self, other):
        """
        Returns true iff this tag is not identical to the other tag,
        as defined in __eq__.
        """
        return not self == other
    
    def __repr__(self, encoding="unicode-escape"):
        """
        Renders this tag as a string.
        """
        return self.string
    
    def __str__(self):
        return self.string
    
    def _get_indent(self, indent_level):
        """
        Returns indent_level number of tabs or spaces.
        """

        indents =''
        indent_char = ''
        if SPACES:
            indent_char = ' '
        else:
            indent_char = '\t'
        
        while indent_level > 0:
            indents += indent_char
            indent_level -= 1
        
        return indents
    
    def generate_for_attrs(self):
        attr_text = ''
 
        for attr, attr_value in self.attrs.iteritems():           
            attr_text += ' '
            attr_text += "{}=\"{}\"".format(attr, attr_value)
        
        return attr_text
    
    def generate_from_children(self, indent_level=0, prettify=True):
        """
        Returns code generated from children.
        """

        text = ''
        for child in self.children:
            child_text = child.generate(indent_level)
            if child_text and len(child_text):
                text += "\r\n"+child_text
            child_text = ''
        return text
    
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

    def __getattr__(self, tag_name):
        """
        Returns the first child tag that matches tag_name.
        """

        #print "Getattr %s.%s" % (self.__class__, tag)
        #if len(tag_name) > 3 and tag_name.endswith('Tag'):
        #    # BS3: soup.aTag -> "soup.find("a")
        #    tag_name = tag_name[:-3]
        #    warnings.warn(
        #        '.%sTag is deprecated, use .find("%s") instead.' % (
        #            tag_name, tag_name))
        #    return self.find(tag_name)
        # We special case contents to avoid recursion.
        if not tag_name.startswith("_") and not tag_name=="contents":
            return self.find(tag_name)
        raise AttributeError(
            "'%s' object has no attribute '%s'" % (self.__class__, tag_name))
    
    #See: https://stackoverflow.com/questions/9663562/what-is-the-difference-between-init-and-call
    def __call__(self, *args, **kwargs):
        """
        Calling a tag like a function is the same as calling its
        find_all() method. Eg. tag('a') returns a list of all the A tags
        found within this tag.
        """
        return self.find_all(*args, **kwargs)

    #Search methods    
    def find(self, name=None, attrs={}, recursive=True, text=None, _type=None,
             **kwargs):
        """
        Return only the first child of this Tag matching the given
        criteria.
        """
        r = None
        l = self.find_all(name, attrs, recursive, text, _type, 1, **kwargs)
        if l:
            r = l[0]
        return r
    
    def find_all(self, name=None, attrs={}, recursive=True, text=None, _type=None,
                 limit=None, **kwargs):
        """
        Extracts a list of Tag objects that match the given
        criteria.  You can specify the name of the Tag and any
        attributes you want the Tag to have.

        The value of a key-value pair in the 'attrs' map can be a
        string, a list of strings.
        """

        generator = self.descendants
        if not recursive:
            generator = self.children
        return self._find_all(name, attrs, text, _type, limit, generator, **kwargs)
    
    def find_next_sibling(self, name=None, attrs={}, text=None, _type=None, **kwargs):
        """
        Returns the closest sibling to this Tag that matches the
        given criteria and appears after this Tag in the document.
        """
        return self._find_one(self.find_next_siblings, name, attrs, text, _type, 
                             **kwargs)
    
    def find_next_siblings(self, name=None, attrs={}, text=None, _type=None, limit=None,
                           **kwargs):
        """
        Returns the siblings of this Tag that match the given
        criteria and appear after this Tag in the document.
        """
        return self._find_all(name, attrs, text, _type, limit, self.next_siblings ,**kwargs)
    
    def find_previous_sibling(self, name=None, attrs={}, text=None, _type=None, **kwargs):
        """
        Returns the closest sibling to this Tag that matches the
        given criteria and appears before this Tag in the document.
        """
        return self._find_one(self.find_previous_siblings, name, attrs, text, _type,
                             **kwargs)
    
    def find_previous_siblings(self, name=None, attrs={}, text=None, _type=None,
                               limit=None, **kwargs):
        """
        Returns the siblings of this Tag that match the given
        criteria and appear before this Tag in the document.
        """
        return self._find_all(name, attrs, text, _type, limit,
                              self.previous_siblings, **kwargs)
    
    def find_parent(self, name=None, attrs={}, _type=None, **kwargs):
        """
        Returns the closest parent of this Tag that matches the given
        criteria.
        """
        # NOTE: We can't use _find_one because findParents takes a different
        # set of arguments.
        r = None
        l = self.find_parents(name, attrs, _type, 1, **kwargs)
        if l:
            r = l[0]
        return r
    
    def find_parents(self, name=None, attrs={}, _type=None, limit=None, **kwargs):
        """
        Returns the parents of this Tag that match the given
        criteria.
        """
        return self._find_all(name, attrs, None, _type, limit, self.parents,
                             **kwargs)
    
    def _find_one(self, method, name, attrs, text, _type=None, **kwargs):
        """
        Proxy method that calls the 'method' argument and returns the first item from
        the result list.
        """

        r = None
        l = method(name, attrs, text, _type, 1, **kwargs)
        if l:
            r = l[0]
        return r

    #Does the real heavy lifting.
    def _find_all(self, name, attrs, text, _type, limit, generator, **kwargs):
        """
        Iterates over a generator looking for things that match.
        """

        results = []
        more_than_one = 0
        for tag in generator:
            if limit is not None and len(results) >= limit:
                break
            
            more_than_one += 1
            result = True
            tag_name    = tag.name
            tag_type    = tag._type
            tag_attrs   = tag.attrs
            tag_text    = tag.text            

            if name is not None:
                if not name == tag_name:
                    result = result and False
            if _type is not None:
                _type = _type.lower()
                result = result and _type == tag_type
            if text is not None:
                result_ = True
                if tag_text is not None:
                    result_ = text in tag_text                    
                else:
                    result_ = False                
                result = result and result_
            if attrs is not None and len(attrs) > 0:
                result_ = None
                if tag_attrs is not None:
                    result_ = True
                    for key, value in attrs.iteritems():
                        if key in tag_attrs and value in tag_attrs[key]:
                            result_ = result_ and True
                        else:
                            result_ = result_ and False
                            break
                else:
                    result_ = False
                result = result and result_
            
            if result and more_than_one >0:
                results.append(tag)
    
        return results

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
