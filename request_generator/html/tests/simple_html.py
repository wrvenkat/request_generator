import unittest
from ..simple_html import *

class SimpleHTMLTest(unittest.TestCase):
    """
    Tests DOM generated using elements in simple_html module.
    """

    def setUp(self):
        """
        Sets up an HTML DOM tree.
        """

        #malicious payloads
        xss_attempt1 = "</head><body><script>alert('XSS Attrmpt1')</script></body>"
        html_attrib_xss1 = ' "src="javascript:alert("XSS Here")">'
        url_parameter_xss = "document.location=\"https:/ascsavwb.com\""

        #HTML
        self.html_tag = HTML()

        #HEAD        
        self.head_tag = Head(text = "Test Document!"+xss_attempt1)

        #title
        self.title_tag = Title(title='Test HTML document title!')
        #meta
        meta_attrs = {
            'name':'description',
            'content':'Simple description text.',
            'charset':'UTF-8'
        }
        self.meta_desc = Meta(attrs=meta_attrs)

        #body
        self.body_tag = Body()

        #iframe with default width and height
        iframe1_attrs = {
            'src' : 'https://demo.testfire.net/'+html_attrib_xss1
        }        
        self.iframe1 = IFrame(attrs=iframe1_attrs)

        #href
        self.ahref1 = AHref(href='https://demo.testfire.net/src='+url_parameter_xss
                            , text='Visit Demo.TestFire')

        #form1
        form1_attrs = {
            'action':'https:/weaweas.com/asdasd',
            'method':'post'
        }
        self.form1 = Form(attrs=form1_attrs)

        #Name label
        self.label1 = Label(text='Name:',attrs={'for':'name'})
        
        #Name input field
        name_input_attrs = {
            'type'  : 'text',
            'id'    : 'name',
            'name'  : 'user_name'
        }
        self.name_input = Input(attrs=name_input_attrs)

        #email label
        self.label2 = Label(text='E-mail:',attrs={'for':'mail'})
        email_input_attrs = {
            'type'  : 'email',
            'id'    : 'mail',
            'name'  : 'user_email'
        }
        self.email_input = Input(attrs=email_input_attrs)

        #submit button
        submit_button_attrs = {
            'type'  : 'submit',
            'value' : 'Submit'
        }
        self.submit_button = Input(attrs=submit_button_attrs)

        #construct the DOM tree

        #construct the form
        self.form1.append(self.label1)
        self.form1.append(self.name_input)
        self.form1.append(BR())
        self.form1.append(self.label2)
        self.form1.append(self.email_input)
        self.form1.append(BR())
        self.form1.append(self.submit_button)

        #construct body
        self.body_tag.append(BR())
        self.body_tag.append(self.iframe1)
        self.test_br = BR()
        self.body_tag.append(self.test_br)
        self.body_tag.append(self.ahref1)
        self.body_tag.append(BR())
        self.body_tag.append(self.form1)

        #construct head
        #self.head_tag.append(self.head_text)
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

        #assert that the a tag has index 3 (2nd child) of body tag
        body_tag = self.html_tag.contents[1]
        self.assertEquals(3, body_tag.index(self.ahref1))

        #assert that the tag at position 1 of body is self.iframe1
        #asserts that __eq__ and is_equal() is working
        iframe1 = body_tag.contents[1]
        self.assertEquals(iframe1, self.iframe1)

        #assert that iframe's next/next_sibling is br
        self.assertEquals(self.test_br,iframe1.next)

        #assert that title's previous/previous_sibling of title is meta
        title_tag = self.html_tag.contents[0].contents[2]
        self.assertEquals(self.meta_desc, title_tag.previous)

        #assert that submit input tag's next is None
        self.assertIsNone(self.submit_button.next)

    def test_z_generate(self):
        print "\nSave the below HTML as a .html file and open in any browser."
        print "If any scripts/alert pops, then this case is a fail."
        print self.html_tag.generate()

unittest.main()