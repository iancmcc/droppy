import unittest

from formencode import Invalid

from droppy.validation.validation import NotEmpty, Int, ConfirmType, Constant
from droppy.validation.validation import OneOf, DictConverter, StringBool
from droppy.validation.validation import Bool, Number, UnicodeString
from droppy.validation.validation import Set, String, StripField, MaxLength
from droppy.validation.validation import MinLength, Regex, PlainText, Email
from droppy.validation.validation import IndexListConverter, URL, IPAddress
from droppy.validation.validation import CIDR, MACAddress
from droppy.validation.properties import Document, Property


class TestParsing(unittest.TestCase):

    def test_simple_parse(self):
        doc = """
        http: 8080
        """.strip()

        class HttpDoc(Document):

            @Property
            def http(self): 
                return None

        result = HttpDoc.loadYAML(doc)

        self.assertTrue(isinstance(result, HttpDoc))
        self.assertEquals(result.http, 8080)

    def test_nested(self):
        doc = """
        http: 
            port: 8080
        """.strip()

        class PortDoc(Document):
            @Property
            def port(self):
                return 0

        class HttpDoc(Document):

            @Property
            def http(self): 
                return PortDoc()

        result = HttpDoc.loadYAML(doc)

        self.assertTrue(isinstance(result, HttpDoc))
        self.assertEquals(result.http.port, 8080)

    def test_default(self):
        doc = """
        http:
            port: 8080
        """.strip()

        class PortDoc(Document):
            @Property
            def port(self):
                return 0

            @Property
            def ssl(self):
                return True

        class HttpDoc(Document):

            @Property
            def http(self): 
                return PortDoc()

        result = HttpDoc.loadYAML(doc)

        self.assertTrue(isinstance(result, HttpDoc))
        self.assertEquals(result.http.port, 8080)
        self.assertEquals(result.http.ssl, True)

    def test_bad(self):
        doc = """
        http:
            notanattribute: 9090
        """.strip()

        class ThingDoc(Document):

            @Property
            def whatever(self):
                return 0

        class HttpDoc(Document):

            @Property
            def http(self): 
                return ThingDoc()

        self.assertRaises(Invalid, HttpDoc.loadYAML, doc)

    def test_json(self):
        import json
        doc = json.dumps({'http':{'port':9090}})

        class PortDoc(Document):

            @Property
            def port(self):
                return 0

        class HttpDoc(Document):

            @Property
            def http(self): 
                return PortDoc()

        result = HttpDoc.loadJSON(doc)

        self.assertTrue(isinstance(result, HttpDoc))
        self.assertEquals(result.http.port, 9090)

    def test_json_file(self):
        import json
        from cStringIO import StringIO
        doc = StringIO(json.dumps({'http':{'port':9090}}))

        class PortDoc(Document):

            @Property
            def port(self):
                return 0

        class HttpDoc(Document):

            @Property
            def http(self): 
                return PortDoc()

        result = HttpDoc.loadJSON(doc)

        self.assertTrue(isinstance(result, HttpDoc))
        self.assertEquals(result.http.port, 9090)

    def test_yaml_file(self):
        from cStringIO import StringIO
        yamldoc = """
        http:
            port: 9090
        """.strip()
        doc = StringIO(yamldoc)


        class PortDoc(Document):

            @Property
            def port(self):
                return 0

        class HttpDoc(Document):

            @Property
            def http(self): 
                return PortDoc()

        result = HttpDoc.loadYAML(doc)

        self.assertTrue(isinstance(result, HttpDoc))
        self.assertEquals(result.http.port, 9090)



class TestValidators(unittest.TestCase):

    def test_notempty(self):

        class TestDoc(Document):
            @NotEmpty
            def a(self): 
                return "default"

        doc = """
        a: blah
        """
        result = TestDoc.loadYAML(doc)
        self.assertEquals(result.a, "blah")

        doc = """
        a: 
        b: 1
        """
        self.assertRaises(Invalid, TestDoc.loadYAML, doc)

        doc = """
        """
        result = TestDoc.loadYAML(doc)
        self.assertEquals(result.a, "default")

    def test_int(self):

        class TestDoc(Document):
            @Int
            def a(self): 
                return 1

        doc = """
        a: 12345
        """
        result = TestDoc.loadYAML(doc)
        self.assertEquals(result.a, 12345)
        result = TestDoc.loadYAML("")
        self.assertEquals(result.a, 1)

    def test_int_called(self):

        class TestDoc(Document):
            @Int()
            def a(self): 
                return 1

        doc = """
        a: 12345
        """
        result = TestDoc.loadYAML(doc)
        self.assertEquals(result.a, 12345)
        result = TestDoc.loadYAML("")
        self.assertEquals(result.a, 1)

    def test_confirm_type(self):

        class TestDoc(Document):
            @ConfirmType(subclass=int)
            def a(self): 
                return 1

        doc = """
        a: notanint
        """
        self.assertRaises(Invalid, TestDoc.loadYAML, doc)
        result = TestDoc.loadYAML("")
        self.assertEquals(result.a, 1)

    def test_constant(self):

        class TestDoc(Document):
            @Constant("XYZ")
            def a(self): 
                return 1

        doc = """
        a: notanint
        """
        result = TestDoc.loadYAML(doc)
        self.assertEquals(result.a, "XYZ")

        result = TestDoc.loadYAML("")
        self.assertEquals(result.a, 1)

    def test_oneof(self):

        class TestDoc(Document):
            @OneOf((1, 2, 3))
            def a(self): 
                return 1

        doc = """
        a: 2
        """
        result = TestDoc.loadYAML(doc)
        self.assertEquals(result.a, 2)

        doc = """
        a: 4
        """
        self.assertRaises(Invalid, TestDoc.loadYAML, doc)

        result = TestDoc.loadYAML("")
        self.assertEquals(result.a, 1)

    def test_dictconverter(self):
        class TestDoc(Document):
            @DictConverter({1:'one', 2:'two'})
            def a(self): 
                return 'one'

        doc = """
        a: 2
        """
        result = TestDoc.loadYAML(doc)
        self.assertEquals(result.a, 'two')

        doc = """
        a: 4
        """
        self.assertRaises(Invalid, TestDoc.loadYAML, doc)

        result = TestDoc.loadYAML("")
        self.assertEquals(result.a, 'one')

    def test_stringbool(self):
        class TestDoc(Document):
            @StringBool
            def a(self): 
                return True

        doc = """
        a: yes
        """
        result = TestDoc.loadYAML(doc)
        self.assertEquals(result.a, True)

        doc = """
        a: f
        """
        result = TestDoc.loadYAML(doc)
        self.assertEquals(result.a, False)

        doc = """
        a: j
        """
        self.assertRaises(Invalid, TestDoc.loadYAML, doc)

        result = TestDoc.loadYAML("")
        self.assertEquals(result.a, True)

    def test_bool(self):
        class TestDoc(Document):
            @Bool
            def a(self): 
                return True

        doc = """
        a: 1
        """
        result = TestDoc.loadYAML(doc)
        self.assertEquals(result.a, True)

        doc = """
        a: 0
        """
        result = TestDoc.loadYAML(doc)
        self.assertEquals(result.a, False)

        doc = """
        a: 
        """
        result = TestDoc.loadYAML(doc)
        self.assertEquals(result.a, False)

        result = TestDoc.loadYAML("")
        self.assertEquals(result.a, True)

    def test_number(self):
        class TestDoc(Document):
            @Number
            def a(self): 
                return 1

        doc = """
        a: 1
        """
        result = TestDoc.loadYAML(doc)
        self.assertEquals(result.a, 1)
        self.assertTrue(isinstance(result.a, int))

        doc = """
        a: 0.56
        """
        result = TestDoc.loadYAML(doc)
        self.assertEquals(result.a, 0.56)

        doc = """
        a: abc
        """
        self.assertRaises(Invalid, TestDoc.loadYAML, doc)

        result = TestDoc.loadYAML("")
        self.assertEquals(result.a, 1)

    def test_unicode(self):
        class TestDoc(Document):
            @UnicodeString
            def a(self): 
                return u"abcde"

        doc = """
        a: whatever
        """
        result = TestDoc.loadYAML(doc)
        self.assertEquals(result.a, u"whatever")
        self.assertTrue(isinstance(result.a, unicode))

        result = TestDoc.loadYAML("")
        self.assertEquals(result.a, u'abcde')

    def test_set(self):
        class TestDoc(Document):
            @Set
            def a(self): 
                return [1, 2, 3]

        doc = """
        a: 1
        """
        result = TestDoc.loadYAML(doc)
        self.assertEquals(result.a, [1])

        doc = """
        a: 
            - 1
            - 2
            - 3
            - 3
        """
        result = TestDoc.loadYAML(doc)
        self.assertEquals(result.a, [1, 2, 3, 3])

        result = TestDoc.loadYAML("")
        self.assertEquals(result.a, [1, 2, 3])

        class TestDoc(Document):
            @Set(use_set=True)
            def a(self): 
                return {1, 2, 3}

        doc = """
        a: 
            - 1
            - 2
            - 3
            - 3
        """
        result = TestDoc.loadYAML(doc)
        self.assertEquals(result.a, {1, 2, 3})

        result = TestDoc.loadYAML("")
        self.assertEquals(result.a, {1, 2, 3})

    def test_string(self):
        class TestDoc(Document):
            @String
            def a(self): 
                return "jkfd"

        doc = """
        a: 1
        """
        result = TestDoc.loadYAML(doc)
        self.assertEquals(result.a, "1")

        result = TestDoc.loadYAML("")
        self.assertEquals(result.a, 'jkfd')

    def test_stripfield(self):
        class TestDoc(Document):
            @StripField('test')
            def a(self): 
                return (0, {'a':1})

        doc = """
        a: 
            test: 1
            b: 2
        """
        result = TestDoc.loadYAML(doc)
        self.assertEquals(result.a, (1, {'b':2}))

        result = TestDoc.loadYAML("")
        self.assertEquals(result.a, (0, {'a':1}))

    def test_indexlistconverter(self):
        class TestDoc(Document):
            @IndexListConverter(["zero", "one", "two", "three"])
            def a(self): 
                return "one"

        doc = """
        a: 2
        """
        result = TestDoc.loadYAML(doc)
        self.assertEquals(result.a, "two")

        result = TestDoc.loadYAML("")
        self.assertEquals(result.a, "one")

    def test_nodefault(self):
        class TestDoc(Document):
            @Property
            def a(self): 
                return Document.NoDefault

        self.assertRaises(Invalid, TestDoc.loadYAML, "")

    def test_maxlength(self):
        class TestDoc(Document):
            @MaxLength(4)
            def a(self): 
                return "one"

        doc = """
        a: abcd
        """
        result = TestDoc.loadYAML(doc)
        self.assertEquals(result.a, "abcd")

        doc = """
        a: abcdefg
        """
        self.assertRaises(Invalid, TestDoc.loadYAML, doc)

        result = TestDoc.loadYAML("")
        self.assertEquals(result.a, "one")

    def test_minlength(self):
        class TestDoc(Document):
            @MinLength(2)
            def a(self): 
                return "one"

        doc = """
        a: abcd
        """
        result = TestDoc.loadYAML(doc)
        self.assertEquals(result.a, "abcd")

        doc = """
        a: a
        """
        self.assertRaises(Invalid, TestDoc.loadYAML, doc)

        result = TestDoc.loadYAML("")
        self.assertEquals(result.a, "one")

    def test_regex(self):
        class TestDoc(Document):
            @Regex(r'^[a-z]ne$')
            def a(self): 
                return "one"

        doc = """
        a: zne
        """
        result = TestDoc.loadYAML(doc)
        self.assertEquals(result.a, "zne")

        doc = """
        a: znx
        """
        self.assertRaises(Invalid, TestDoc.loadYAML, doc)

        result = TestDoc.loadYAML("")
        self.assertEquals(result.a, "one")
        
    def test_plaintext(self):
        class TestDoc(Document):
            @PlainText
            def a(self): 
                return "one"

        doc = """
        a: this_is_a_test
        """
        result = TestDoc.loadYAML(doc)
        self.assertEquals(result.a, "this_is_a_test")

        doc = """
        a: this is a test
        """
        self.assertRaises(Invalid, TestDoc.loadYAML, doc)

        result = TestDoc.loadYAML("")
        self.assertEquals(result.a, "one")

    def test_email(self):
        class TestDoc(Document):
            @Email
            def a(self): 
                return "ian@example.com"

        doc = """
        a: testing@gmail.com
        """
        result = TestDoc.loadYAML(doc)
        self.assertEquals(result.a, "testing@gmail.com")

        doc = """
        a: this is a test
        """
        self.assertRaises(Invalid, TestDoc.loadYAML, doc)

        result = TestDoc.loadYAML("")
        self.assertEquals(result.a, "ian@example.com")

    def test_url(self):
        class TestDoc(Document):
            @URL
            def a(self): 
                return "http://www.google.com"

        for url in (
            "http://example.com",
            "https://example.com",
            "http://example.com:9090",
            "http://example.com:9090/path/to/resource",
        ):

            doc = """
            a: %s
            """ % url
            result = TestDoc.loadYAML(doc)
            self.assertEquals(result.a, url)

        doc = """
        a: this is a test
        """
        self.assertRaises(Invalid, TestDoc.loadYAML, doc)

        result = TestDoc.loadYAML("")
        self.assertEquals(result.a, "http://www.google.com")

    def test_ipaddress(self):
        class TestDoc(Document):
            @IPAddress
            def a(self): 
                return "10.1.2.3"

        doc = """
        a: 10.10.10.10
        """ 
        result = TestDoc.loadYAML(doc)
        self.assertEquals(result.a, '10.10.10.10')

        doc = """
        a: 350.2.300.1
        """
        self.assertRaises(Invalid, TestDoc.loadYAML, doc)

        result = TestDoc.loadYAML("")
        self.assertEquals(result.a, "10.1.2.3")

    def test_cidr(self):
        class TestDoc(Document):
            @CIDR
            def a(self): 
                return "10.1.2.3/24"

        doc = """
        a: 10.10.10.10
        """ 
        result = TestDoc.loadYAML(doc)
        self.assertEquals(result.a, '10.10.10.10')

        doc = """
        a: 10.10.10.10/24
        """ 
        result = TestDoc.loadYAML(doc)
        self.assertEquals(result.a, '10.10.10.10/24')

        doc = """
        a: 350.2.300.1
        """
        self.assertRaises(Invalid, TestDoc.loadYAML, doc)

        doc = """
        a: 10.10.10.10/2
        """
        self.assertRaises(Invalid, TestDoc.loadYAML, doc)

        result = TestDoc.loadYAML("")
        self.assertEquals(result.a, "10.1.2.3/24")

    def test_macaddress(self):
        class TestDoc(Document):
            @MACAddress
            def a(self): 
                return "aabbccddeeff"

        doc = """
        a: 00:11:22:33:44:55
        """ 
        result = TestDoc.loadYAML(doc)
        self.assertEquals(result.a, "001122334455")

        doc = """
        a: 00:11:22:33:44:jj
        """
        self.assertRaises(Invalid, TestDoc.loadYAML, doc)

        result = TestDoc.loadYAML("")
        self.assertEquals(result.a, "aabbccddeeff")

if __name__ == "__main__":
    unittest.main()

