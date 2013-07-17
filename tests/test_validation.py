import unittest

from formencode import Invalid

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

        result = HttpDoc.loadYAML(doc)

        self.assertTrue(isinstance(result, HttpDoc))
        self.assertFalse(hasattr(result.http, 'notanattribute'))

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


from droppy.validation.validation import NotEmpty

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


if __name__ == "__main__":
    unittest.main()
