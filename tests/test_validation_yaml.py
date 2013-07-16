import unittest

from droppy.validation import yaml_ as yaml


class TestYamlValidation(unittest.TestCase):

    def test_simple_parse(self):
        doc = """
        http: 8080
        """.strip()

        class HttpDoc(yaml.Document):

            @yaml.Document.YAMLProperty
            def http(self): 
                return None

        result = HttpDoc.load(doc)

        self.assertTrue(isinstance(result, HttpDoc))
        self.assertEquals(result.http, 8080)

    def test_nested(self):
        doc = """
        http: 
            port: 8080
        """.strip()

        class PortDoc(yaml.Document):
            @yaml.Document.YAMLProperty
            def port(self):
                return 0

        class HttpDoc(yaml.Document):

            @yaml.Document.YAMLProperty
            def http(self): 
                return PortDoc()

        result = HttpDoc.load(doc)

        self.assertTrue(isinstance(result, HttpDoc))
        self.assertEquals(result.http.port, 8080)

    def test_default(self):
        doc = """
        http:
            port: 8080
        """.strip()

        class PortDoc(yaml.Document):
            @yaml.Document.YAMLProperty
            def port(self):
                return 0

            @yaml.Document.YAMLProperty
            def ssl(self):
                return True

        class HttpDoc(yaml.Document):

            @yaml.Document.YAMLProperty
            def http(self): 
                return PortDoc()

        result = HttpDoc.load(doc)

        self.assertTrue(isinstance(result, HttpDoc))
        self.assertEquals(result.http.port, 8080)
        self.assertEquals(result.http.ssl, True)


    def test_bad(self):
        doc = """
        http:
            notanattribute: 9090
        """.strip()

        class ThingDoc(yaml.Document):

            @yaml.Document.YAMLProperty
            def whatever(self):
                return 0

        class HttpDoc(yaml.Document):

            @yaml.Document.YAMLProperty
            def http(self): 
                return ThingDoc()

        result = HttpDoc.load(doc)

        self.assertTrue(isinstance(result, HttpDoc))
        self.assertFalse(hasattr(result.http, 'notanattribute'))

if __name__ == "__main__":
    unittest.main()
