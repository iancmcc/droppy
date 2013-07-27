import unittest

from formencode import Invalid

from droppy.validation.validation import NotEmpty, Int, ConfirmType, Constant
from droppy.validation.validation import OneOf, DictConverter, StringBool
from droppy.validation.validation import Bool, Number, UnicodeString
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

        doc = """
        """
        result = TestDoc.loadYAML(doc)
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


if __name__ == "__main__":
    unittest.main()
