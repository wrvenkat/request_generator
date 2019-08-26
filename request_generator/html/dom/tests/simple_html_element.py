import unittest
from ..simple_html_element import SimpleHTMLElement

class SimpleHTMLElementTest(unittest.TestCase):
    """
    Tests SimpleHTMLElement and by extension tests Tag.
    """
    
    def setUp(self):
        """
        Sets up an HTML DOM tree.
        """

        #HTML
        self.html_tag = SimpleHTMLElement(name='html')

        #HEAD
        self.head_tag = SimpleHTMLElement(name='head')
        self.head_text = SimpleHTMLElement(name='text', text = "Test Document!")

        self.title_tag = SimpleHTMLElement(name='title')
        self.title_text = SimpleHTMLElement(text='Test HTML document title!')

        self.meta_desc = SimpleHTMLElement(name="meta", attrs={'name':'description','content':'Simple description text.'}, self_closing=True)

        #body
        self.body_tag = SimpleHTMLElement(name="body")
        iframe1_attrs = {
            'src' : 'https://www.w3schools.com',
            'width' : "500",
            'height' : "500"
        }

        #iframe
        self.iframe1 = SimpleHTMLElement(name="iframe", attrs=iframe1_attrs)

        #href
        self.ahref1 = SimpleHTMLElement(name="a", attrs={'href':'https://www.w3schools.com'})
        self.a1_text = SimpleHTMLElement(text="Visit W3Schools")

        #form1
        form1_attrs = {
            'action':'https:/weaweas.com/asdasd',
            'method':'post'
        }
        self.form1 = SimpleHTMLElement(name='form', attrs=form1_attrs)

        #Name label
        self.label1 = SimpleHTMLElement(name='label', attrs={'for':'name'})
        self.label1_text = SimpleHTMLElement(text='Name:')
        #Name input field
        name_input_attrs = {
            'type'  : 'text',
            'id'    : 'name',
            'name'  : 'user_name'
        }
        self.name_input = SimpleHTMLElement(name="input", attrs=name_input_attrs)

        #email label
        self.label2 = SimpleHTMLElement(name='label', attrs={'for':'mail'})
        self.label2_text = SimpleHTMLElement(text='E-mail:')
        email_input_attrs = {
            'type'  : 'email',
            'id'    : 'mail',
            'name'  : 'user_email'
        }
        self.email_input = SimpleHTMLElement(name="input", attrs=email_input_attrs)

        #submit button
        submit_button_attrs = {
            'type'  : 'submit',
            'value' : 'Submit'
        }
        self.submit_button = SimpleHTMLElement(name="input", attrs=submit_button_attrs)

        #construct the DOM tree

        #Fix the labels
        self.label1_text.setup(parent=self.label1)
        self.label2_text.setup(parent=self.label2)

        #href
        self.a1_text.setup(parent=self.ahref1)

        #construct the form
        self.form1.append(self.label1)
        self.form1.append(self.name_input)
        self.form1.append(self.label2)
        self.form1.append(self.email_input)
        self.form1.append(self.submit_button)

        #construct body
        self.body_tag.append(self.iframe1)
        self.body_tag.append(self.ahref1)
        self.body_tag.append(self.form1)

        #construct title        
        self.title_tag.append(self.title_text)

        #construct head
        self.head_tag.append(self.head_text)
        self.head_tag.append(self.meta_desc)
        self.head_tag.append(self.title_tag)

        #add to root
        self.html_tag.append(self.head_tag)
        self.html_tag.append(self.body_tag)
    
    def test_a_setUp(self):
        """
        Tests if the tree was created as expected.

        As a result, ends up testing a few methods below,
            __eq__
            contents
            index
            parent
            next, previous
            next_sibling, prev_sibling
        """
        
        #check if root of the document has no parent
        self.assertIsNone(self.html_tag.parent)
        #assert that the root has 2 direct children
        self.assertEqual(2, len(self.html_tag.contents))

        #assert that the a tag has index 1 (2nd child) of body tag
        body_tag = self.html_tag.contents[1]
        self.assertEqual(1, body_tag.index(self.ahref1))

        #assert that the tag at position 0 is self.iframe1
        #asserts that __eq__ and is_equal() is working
        iframe1 = body_tag.contents[0]
        self.assertEqual(iframe1, self.iframe1)

        #assert that iframe's next/next_sibling is ahref
        self.assertEqual(self.ahref1,iframe1.next)

        #assert that title's previous/previous_sibling of title is meta
        title_tag = self.html_tag.contents[0].contents[2]
        self.assertEqual(self.meta_desc, title_tag.previous)

        #assert that submit input tag's next is None
        self.assertIsNone(self.submit_button.next)

    def test_b_replace_with(self):
        #replaces post form with a get form to a different URL
        get_form_attrs = {
            'action'    :   'https://kjimojno/jojygj',
            'method'    :   'GET'
        }

        #print "test_b_replace_with_before"
        #print self.html_tag.generate()

        get_form = SimpleHTMLElement(name="form", attrs=get_form_attrs)
        self.form1.replace_with(get_form)

        #print "test_b_replace_with_after"
        #print self.html_tag.generate()

        #assert that the form has been replaced and the neighbourly relations
        #are fine
        self.assertEqual(self.body_tag.contents[2], get_form)
        self.assertEqual(self.body_tag.contents[1], get_form.previous)
        self.assertEqual(get_form, self.body_tag.contents[1].next)

        #assert that the children are copied over
        self.assertEqual(get_form.contents[1], self.name_input)
 
    def test_c_unwrap(self):
        """
        Test unwrap.

        Also tests,
            extract
        """

        #unwrap the form
        self.form1.unwrap()

        #print "test_c_unwrap_after"
        #print self.html_tag.generate()
        
        #assert that all children of form1 is now part of body
        self.assertEqual(2, self.body_tag.index(self.label1))
        #assert that label1's parent is body
        self.assertEqual(self.body_tag, self.label1.parent)
        #assert that ahref's next is lable1
        self.assertEqual(self.ahref1.next, self.label1)

        #assert that self.form1 doesn't have a parent, siblings or children
        self.assertIsNone(self.form1.parent)
        self.assertIsNone(self.form1.next)
        self.assertIsNone(self.form1.previous)
        self.assertEqual(0, len(self.form1.contents))
    
    def test_d_wrap_with(self):
        """
        Tests wrap_with
        """

        #print "test_d_wrap_with_before"
        #print self.html_tag.generate()

        #wrap form1 with div
        div_tag = SimpleHTMLElement(name="div")
        self.form1.wrap_with(div_tag)

        #print "test_d_wrap_with_after"
        #print self.html_tag.generate()

        #div_tag's child should be self.form1
        self.assertEqual(div_tag.contents[0], self.form1)
        #likewise form1's parent should be div_tag
        self.assertEqual(div_tag, self.form1.parent)
        #div_tag should also be the third child of body
        self.assertEqual(self.body_tag.contents[2], div_tag)

        #make sure that the neighbhors of div are also good
        self.assertIsNone(div_tag.next)
        self.assertEqual(div_tag.previous, self.ahref1)
        self.assertEqual(div_tag, self.ahref1.next)

    def test_e_insert_before(self):

        form_temp_attrs = {
            'action' : 'https://asdasdasdas.com',
            'method' : 'POST'
        }
        form_temp = SimpleHTMLElement(name="form", attrs=form_temp_attrs)
        self.form1.insert_before(form_temp)

        #assert the neighbors
        self.assertEqual(form_temp.next, self.form1)
        self.assertEqual(self.form1.previous, form_temp)
        self.assertEqual(len(form_temp.contents), 0)
        self.assertEqual(form_temp.previous, self.ahref1)
    
    def test_f_insert_after(self):

        form_temp_attrs = {
            'action' : 'https://asdasdasdas.com',
            'method' : 'POST'
        }
        form_temp = SimpleHTMLElement(name="form", attrs=form_temp_attrs)
        self.form1.insert_after(form_temp)

        #assert the neighbors
        self.assertIsNone(form_temp.next)
        self.assertEqual(self.form1.next, form_temp)
        self.assertEqual(len(form_temp.contents), 0)
        self.assertEqual(form_temp.previous, self.form1)

    def test_g_siblings(self):
        """
        Test *_siblings iterator.
        """

        for i,sibling in enumerate(self.iframe1.next_siblings):
            if i == 0:
                self.assertEqual(sibling, self.ahref1)
            if i == 1:
                self.assertEqual(sibling, self.form1)
        
        for i,sibling in enumerate(self.form1.previous_siblings):
            if i == 0:
                self.assertEqual(sibling, self.ahref1)
            if i == 1:
                self.assertEqual(sibling, self.iframe1)
    
    def test_h_ancestors_descendants(self):
        """
        Tests ancestors and descendants iterators.
        """

        #Ancestors
        for i, ancestor in enumerate(self.label2_text.parents):
            if i==0:
                self.assertEqual(ancestor,self.label2)
            if i==1:
                self.assertEqual(ancestor,self.form1)
            if i==2:
                self.assertEqual(ancestor,self.body_tag)
            if i==3:
                self.assertEqual(ancestor,self.html_tag)
        
        #descendants just goes through all of the children
        #so a curated list of children is asserted here
        for i,descendant in enumerate(self.body_tag.descendants):
            if i==0:
                self.assertEqual(descendant,self.iframe1)
            if i==1:
                self.assertEqual(descendant,self.ahref1)
            if i==2:
                self.assertEqual(descendant,self.a1_text)
            if i==3:
                self.assertEqual(descendant,self.form1)
            if i==4:
                self.assertEqual(descendant,self.label1)
            if i==5:
                self.assertEqual(descendant,self.label1_text)
            if i==6:
                self.assertEqual(descendant,self.name_input)
            if i==7:
                self.assertEqual(descendant,self.label2)
            if i==8:
                self.assertEqual(descendant,self.label2_text)
            if i==9:
                self.assertEqual(descendant,self.email_input)
            if i==10:
                self.assertEqual(descendant,self.submit_button)

    def test_i_attribs(self):
        """
        Tests calling tag by name.
        """
        
        self.assertEqual("500", self.iframe1['height'])
        del self.iframe1['width']
        with self.assertRaises(KeyError):
            self.iframe1['width']
        self.iframe1['width'] = 500
        self.assertEqual(500, self.iframe1['width'])

    def test_j_misc(self):
        """
        Tests,
             __contains__, __len__.
        """

        #__contains__
        self.assertTrue(self.body_tag in self.html_tag)
        self.assertFalse(self.form1 in self.html_tag)

        #__len__
        self.assertEqual(3, len(self.body_tag))
        self.assertNotEqual(2, len(self.head_tag))
    
    def test_k_decompose(self):

        my_index = self.form1.parent.index(self.form1)
        self.form1.decompose()

        self.assertFalse(hasattr(self.form1, '_parent'))
        self.assertFalse(hasattr(self.form1, 'contents'))

        #assert that previous neighbours don't have a reference to this
        self.assertIsNone(self.ahref1.next)
        #assert that body doesn't have a child at this location
        with self.assertRaises(IndexError):
            self.body_tag.contents[my_index]
    
    def test_l_copy(self):
        """
        Test SimpleHTMLElement's shallow copy = __copy__
        """
        form1_copy = self.form1.copy()
        self.assertTrue(self.form1.is_equal(form1_copy))

        name_input_copy = self.name_input.copy()
        self.assertTrue(self.name_input.is_equal(name_input_copy))

    def test_m_search(self):
        """
        Test the search functionality.
        """

        #tests __getattr__
        #als tests find, find_all by name
        self.assertEqual(self.html_tag.body, [self.body_tag])
        self.assertEqual(self.html_tag.label, [self.label1, self.label2])

        #tests find_all with attrs
        attr = { "for" : "mail" }
        self.assertEqual(self.html_tag.find_all('label', attrs=attr), [self.label2])
        self.assertEqual(self.html_tag.find_all(name='label'), [self.label1, self.label2])

        #find_next_siblings
        test_array = []
        test_array.append(self.label2)
        test_array.append(self.email_input)
        test_array.append(self.submit_button)
        self.assertEqual(self.name_input.find_next_siblings(_type="html"), test_array)

        #find_next_sibling
        attr = { "type" : "mail"}
        self.assertEqual(self.html_tag.form[0].input[0].find_next_sibling(attrs=attr),
                         self.email_input)
        
        #find_previous_siblings
        test_array = [self.label2, self.name_input, self.label1]
        self.assertEqual(self.email_input.find_previous_siblings(_type=SimpleHTMLElement.type.html), test_array)

        #find_previous_sibling
        attr = { "type" : "text" }
        self.assertEqual(self.email_input.find_previous_sibling(attrs=attr), self.name_input)

        #find_parent
        self.assertEqual(self.label2_text.find_parent(name='body'), self.body_tag)

        #find_parents
        attr = { "for" : "mail"}
        self.assertEqual(self.label2_text.find_parents(attrs=attr), [self.label2])
        self.assertEqual(self.label2_text.find_parents('html'), [self.html_tag])

        #find_all
        test_array = [self.a1_text, self.label1_text, self.label2_text]
        self.assertEqual(self.body_tag.find_all(_type=SimpleHTMLElement.type.text), test_array)

    def pretty_print(self):
        pretty_code = self.html_tag.generate()
        print(pretty_code)

unittest.main()