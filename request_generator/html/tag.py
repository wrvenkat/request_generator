import re
import warnings

DEFAULT_OUTPUT_ENCODING = 'utf-8'

#Tabs or spaces
SPACES=True

class Tag(object):
    """
    A Tag object forms the basic constructive unit of a DOM.

    A simplistic representation of an element in a tree.
    """

    """
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
   
    def __init__(self):
        #main meta data
        self.name = None
        self.attrs = {}
        #namespace attribute. Just incase we require it.
        self.namespace = None
        self._self_closing = False
        self._type = None

        #sub meta_data        
        self._encoder = None
                    
        #tree info
        self._parent = None
        self._next_sibling = None
        self._previous_sibling = None
        #current list of direct children
        self.contents = []        
    
    def index(self, element):
        """
        Find the index of a child by identity, not value. Avoids issues with
        tag.contents.index(element) getting the index of equal elements.
        """
        for i, child in enumerate(self.children):
            if child is element:
                return i
        raise ValueError("element not in subtree")

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
        if child is not None:
            self.append(child)
        
        if next_sibling is not None and self._next_sibling is not None:
            self._next_sibling._previous_sibling = next_sibling            
            next_sibling._next_sibling = self._next_sibling
            self._next_sibling = next_sibling
            next_sibling._previous_sibling = self
        elif next_sibling is not None and not self._next_sibling is not None:
            self._next_sibling = next_sibling
            next_sibling._previous_sibling = self
        
        if previous_sibling is not None and self._previous_sibling is not None:
            self._previous_sibling._next_sibling = previous_sibling
            previous_sibling._previous_sibling = self._previous_sibling
            previous_sibling._next_sibling = self
            self._previous_sibling = previous_sibling
        elif previous_sibling is not None and not self._previous_sibling is not None:
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
        return self._self_closing
    
    @property    
    def encoder(self):
        """
        Return the encoder for this tag.
        """
        return self._encoder    

    def last_descendant(self, accept_self=True):
        """
        Finds the last direct child of this element.
        """

        last_child = self.contents[len(self.contents)-1]
        return last_child    

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
            self.attrs != other.attrs or
            self.namespace != other.namespace or
            self._self_closing != other._self_closing or
            self._type != other._type):
            return False
        return True
    
    #Python fundamentals
    def copy(self):
        """
        Return a shallow copy of self.

        A copy of a Tag is a new Tag, unconnected to a tree.
        Its contents are a copy of the old Tag's main and sub meta data.
        """
        return self.__copy__()

    def __copy__(self):
        """
        A copy of a Tag is a new Tag, unconnected to a tree.
        Its contents are a copy of the old Tag's main and sub meta data.
        """

        clone = Tag()
        setattr(clone, 'name', getattr(self, 'name'))
        setattr(clone, 'attrs', getattr(self, 'attrs'))
        setattr(clone, 'namespace', getattr(self, 'namespace'))
        setattr(clone, '_self_closing', getattr(self, '_self_closing'))
        setattr(clone, '_type', getattr(self, '_type'))        
        setattr(clone, '_encoder', getattr(self, '_encoder'))

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

    def get_indent(self, indent_level):
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
        
    def generate_from_children(self, indent_level=0):
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

    #sub-class specific implementations
    def generate_for_attrs(self):
        """
        Subclasses must implement this.
        """
        return ''

    def generate(self, indent_level=0):
        """
        Generates code for tree rooted at self.

        Inheriting classes need to implement this.
        """

        return ''
    
    @property
    def string(self):
        """
        Convenience property to get the single string within this tag.

        Subclasses should reimplement this.
        """
        return ''
    