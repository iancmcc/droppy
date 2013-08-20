###############################################################################
##
##  Copyright 2013 Ian McCracken
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################
import unittest

from formencode import Invalid

from droppy.validation.validators import NotEmpty, Int, ConfirmType, Constant
from droppy.validation.validators import OneOf, DictConverter, StringBool
from droppy.validation.validators import Bool, Number, UnicodeString
from droppy.validation.validators import Set, String, StripField, MaxLength
from droppy.validation.validators import MinLength, Regex, PlainText, Email
from droppy.validation.validators import IndexListConverter, URL, IPAddress
from droppy.validation.validators import CIDR, MACAddress
from droppy.validation.properties import ParsedDocument, ParsedProperty


class TestParsing(unittest.TestCase):

    def test_simple_parse(self):
        doc = """
        http: 8080
        """.strip()

        class HttpDoc(ParsedDocument):

            @ParsedProperty
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

        class PortDoc(ParsedDocument):
            @ParsedProperty
            def port(self):
                return 0

        class HttpDoc(ParsedDocument):

            @ParsedProperty
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

        class PortDoc(ParsedDocument):
            @ParsedProperty
            def port(self):
                return 0

            @ParsedProperty
            def ssl(self):
                return True

        class HttpDoc(ParsedDocument):

            @ParsedProperty
            def http(self): 
                return PortDoc()

        result = HttpDoc.load(doc)

        self.assertTrue(isinstance(result, HttpDoc))
        self.assertEquals(result.http.port, 8080)
        self.assertEquals(result.http.ssl, True)

        result = HttpDoc.load("")

        self.assertTrue(isinstance(result, HttpDoc))
        self.assertEquals(result.http.port, 0)
        self.assertEquals(result.http.ssl, True)

        result = HttpDoc.load(doc)

        self.assertTrue(isinstance(result, HttpDoc))
        self.assertEquals(result.http.port, 8080)
        self.assertEquals(result.http.ssl, True)


    def test_defaults_with_notempty(self):

        doc = """
        http:
            port: 8080
            whatever: abc
        """.strip()

        class HttpDoc(ParsedDocument):

            @String()
            def whatever(self): 
                return self.NoDefault

            @Int()
            @NotEmpty()
            def port(self): 
                return 100

        class TestDoc(ParsedDocument):
            @ParsedProperty
            def http(self):
                return HttpDoc()

        result = TestDoc.load(doc)

        self.assertTrue(isinstance(result, TestDoc))
        self.assertEquals(result.http.port, 8080)
        self.assertEquals(result.http.whatever, "abc")

        self.assertRaises(Invalid, HttpDoc.load, "")


    def test_bad(self):
        doc = """
        http:
            notanattribute: 9090
        """.strip()

        class ThingDoc(ParsedDocument):

            @ParsedProperty
            def whatever(self):
                return 0

        class HttpDoc(ParsedDocument):

            @ParsedProperty
            def http(self): 
                return ThingDoc()

        self.assertRaises(Invalid, HttpDoc.load, doc)

    def test_json(self):
        import json
        doc = json.dumps({'http':{'port':9090}})

        class PortDoc(ParsedDocument):

            @ParsedProperty
            def port(self):
                return 0

        class HttpDoc(ParsedDocument):

            @ParsedProperty
            def http(self): 
                return PortDoc()

        result = HttpDoc.load(doc)

        self.assertTrue(isinstance(result, HttpDoc))
        self.assertEquals(result.http.port, 9090)

    def test_json_file(self):
        import json
        from cStringIO import StringIO
        doc = StringIO(json.dumps({'http':{'port':9090}}))

        class PortDoc(ParsedDocument):

            @ParsedProperty
            def port(self):
                return 0

        class HttpDoc(ParsedDocument):

            @ParsedProperty
            def http(self): 
                return PortDoc()

        result = HttpDoc.load(doc)

        self.assertTrue(isinstance(result, HttpDoc))
        self.assertEquals(result.http.port, 9090)

    def test_yaml_file(self):
        from cStringIO import StringIO
        yamldoc = """
        http:
            port: 9090
        """.strip()
        doc = StringIO(yamldoc)


        class PortDoc(ParsedDocument):

            @ParsedProperty
            def port(self):
                return 0

        class HttpDoc(ParsedDocument):

            @ParsedProperty
            def http(self): 
                return PortDoc()

        result = HttpDoc.load(doc)

        self.assertTrue(isinstance(result, HttpDoc))
        self.assertEquals(result.http.port, 9090)



class TestValidators(unittest.TestCase):

    def test_notempty(self):

        class TestDoc(ParsedDocument):
            @NotEmpty()
            def a(self): 
                return "default"

        doc = """
        a: blah
        """
        result = TestDoc.load(doc)
        self.assertEquals(result.a, "blah")

        doc = """
        a: 
        b: 1
        """
        self.assertRaises(Invalid, TestDoc.load, doc)

        doc = """
        """
        result = TestDoc.load(doc)
        self.assertEquals(result.a, "default")

    def test_int(self):

        class TestDoc(ParsedDocument):
            @Int()
            def a(self): 
                return 1

        doc = """
        a: 12345
        """
        result = TestDoc.load(doc)
        self.assertEquals(result.a, 12345)
        result = TestDoc.load("")
        self.assertEquals(result.a, 1)

    def test_confirm_type(self):

        class TestDoc(ParsedDocument):
            @ConfirmType(subclass=int)
            def a(self): 
                return 1

        doc = """
        a: notanint
        """
        self.assertRaises(Invalid, TestDoc.load, doc)
        result = TestDoc.load("")
        self.assertEquals(result.a, 1)

    def test_constant(self):

        class TestDoc(ParsedDocument):
            @Constant("XYZ")
            def a(self): 
                return 1

        doc = """
        a: notanint
        """
        result = TestDoc.load(doc)
        self.assertEquals(result.a, "XYZ")

        result = TestDoc.load("")
        self.assertEquals(result.a, 1)

    def test_oneof(self):

        class TestDoc(ParsedDocument):
            @OneOf((1, 2, 3))
            def a(self): 
                return 1

        doc = """
        a: 2
        """
        result = TestDoc.load(doc)
        self.assertEquals(result.a, 2)

        doc = """
        a: 4
        """
        self.assertRaises(Invalid, TestDoc.load, doc)

        result = TestDoc.load("")
        self.assertEquals(result.a, 1)

    def test_dictconverter(self):
        class TestDoc(ParsedDocument):
            @DictConverter({1:'one', 2:'two'})
            def a(self): 
                return 'one'

        doc = """
        a: 2
        """
        result = TestDoc.load(doc)
        self.assertEquals(result.a, 'two')

        doc = """
        a: 4
        """
        self.assertRaises(Invalid, TestDoc.load, doc)

        result = TestDoc.load("")
        self.assertEquals(result.a, 'one')

    def test_stringbool(self):
        class TestDoc(ParsedDocument):
            @StringBool()
            def a(self): 
                return True

        doc = """
        a: yes
        """
        result = TestDoc.load(doc)
        self.assertEquals(result.a, True)

        doc = """
        a: f
        """
        result = TestDoc.load(doc)
        self.assertEquals(result.a, False)

        doc = """
        a: j
        """
        self.assertRaises(Invalid, TestDoc.load, doc)

        result = TestDoc.load("")
        self.assertEquals(result.a, True)

    def test_bool(self):
        class TestDoc(ParsedDocument):
            @Bool()
            def a(self): 
                return True

        doc = """
        a: 1
        """
        result = TestDoc.load(doc)
        self.assertEquals(result.a, True)

        doc = """
        a: 0
        """
        result = TestDoc.load(doc)
        self.assertEquals(result.a, False)

        doc = """
        a: 
        """
        result = TestDoc.load(doc)
        self.assertEquals(result.a, False)

        result = TestDoc.load("")
        self.assertEquals(result.a, True)

    def test_number(self):
        class TestDoc(ParsedDocument):
            @Number()
            def a(self): 
                return 1

        doc = """
        a: 1
        """
        result = TestDoc.load(doc)
        self.assertEquals(result.a, 1)
        self.assertTrue(isinstance(result.a, int))

        doc = """
        a: 0.56
        """
        result = TestDoc.load(doc)
        self.assertEquals(result.a, 0.56)

        doc = """
        a: abc
        """
        self.assertRaises(Invalid, TestDoc.load, doc)

        result = TestDoc.load("")
        self.assertEquals(result.a, 1)

    def test_unicode(self):
        class TestDoc(ParsedDocument):
            @UnicodeString()
            def a(self): 
                return u"abcde"

        doc = """
        a: whatever
        """
        result = TestDoc.load(doc)
        self.assertEquals(result.a, u"whatever")
        self.assertTrue(isinstance(result.a, unicode))

        result = TestDoc.load("")
        self.assertEquals(result.a, u'abcde')

    def test_set(self):
        class TestDoc(ParsedDocument):
            @Set()
            def a(self): 
                return [1, 2, 3]

        #doc = """
        #a: 1
        #"""
        #result = TestDoc.loadYAML(doc)
        #self.assertEquals(result.a, [1])

        #doc = """
        #a: 
        #    - 1
        #    - 2
        #    - 3
        #    - 3
        #"""
        #result = TestDoc.loadYAML(doc)
        #self.assertEquals(result.a, [1, 2, 3, 3])

        result = TestDoc.load("")
        self.assertEquals(result.a, [1, 2, 3])

        #class TestDoc(Document):
        #    @Set(use_set=True)
        #    def a(self): 
        #        return {1, 2, 3}

        #doc = """
        #a: 
        #    - 1
        #    - 2
        #    - 3
        #    - 3
        #"""
        #result = TestDoc.loadYAML(doc)
        #self.assertEquals(result.a, {1, 2, 3})

        #result = TestDoc.loadYAML("")
        #self.assertEquals(result.a, {1, 2, 3})

    def test_string(self):
        class TestDoc(ParsedDocument):
            @String()
            def a(self): 
                return "jkfd"

        doc = """
        a: 1
        """
        result = TestDoc.load(doc)
        self.assertEquals(result.a, "1")

        result = TestDoc.load("")
        self.assertEquals(result.a, 'jkfd')

    def test_stripfield(self):
        class TestDoc(ParsedDocument):
            @StripField('test')
            def a(self): 
                return (0, {'a':1})

        doc = """
        a: 
            test: 1
            b: 2
        """
        result = TestDoc.load(doc)
        self.assertEquals(result.a, (1, {'b':2}))

        result = TestDoc.load("")
        self.assertEquals(result.a, (0, {'a':1}))

    def test_indexlistconverter(self):
        class TestDoc(ParsedDocument):
            @IndexListConverter(["zero", "one", "two", "three"])
            def a(self): 
                return "one"

        doc = """
        a: 2
        """
        result = TestDoc.load(doc)
        self.assertEquals(result.a, "two")

        result = TestDoc.load("")
        self.assertEquals(result.a, "one")

    def test_nodefault(self):
        class TestDoc(ParsedDocument):
            @ParsedProperty
            def a(self): 
                return ParsedDocument.NoDefault

        self.assertRaises(Invalid, TestDoc.load, "")

    def test_maxlength(self):
        class TestDoc(ParsedDocument):
            @MaxLength(4)
            def a(self): 
                return "one"

        doc = """
        a: abcd
        """
        result = TestDoc.load(doc)
        self.assertEquals(result.a, "abcd")

        doc = """
        a: abcdefg
        """
        self.assertRaises(Invalid, TestDoc.load, doc)

        result = TestDoc.load("")
        self.assertEquals(result.a, "one")

    def test_minlength(self):
        class TestDoc(ParsedDocument):
            @MinLength(2)
            def a(self): 
                return "one"

        doc = """
        a: abcd
        """
        result = TestDoc.load(doc)
        self.assertEquals(result.a, "abcd")

        doc = """
        a: a
        """
        self.assertRaises(Invalid, TestDoc.load, doc)

        result = TestDoc.load("")
        self.assertEquals(result.a, "one")

    def test_regex(self):
        class TestDoc(ParsedDocument):
            @Regex(r'^[a-z]ne$')
            def a(self): 
                return "one"

        doc = """
        a: zne
        """
        result = TestDoc.load(doc)
        self.assertEquals(result.a, "zne")

        doc = """
        a: znx
        """
        self.assertRaises(Invalid, TestDoc.load, doc)

        result = TestDoc.load("")
        self.assertEquals(result.a, "one")
        
    def test_plaintext(self):
        class TestDoc(ParsedDocument):
            @PlainText()
            def a(self): 
                return "one"

        doc = """
        a: this_is_a_test
        """
        result = TestDoc.load(doc)
        self.assertEquals(result.a, "this_is_a_test")

        doc = """
        a: this is a test
        """
        self.assertRaises(Invalid, TestDoc.load, doc)

        result = TestDoc.load("")
        self.assertEquals(result.a, "one")

    def test_email(self):
        class TestDoc(ParsedDocument):
            @Email()
            def a(self): 
                return "ian@example.com"

        doc = """
        a: testing@gmail.com
        """
        result = TestDoc.load(doc)
        self.assertEquals(result.a, "testing@gmail.com")

        doc = """
        a: this is a test
        """
        self.assertRaises(Invalid, TestDoc.load, doc)

        result = TestDoc.load("")
        self.assertEquals(result.a, "ian@example.com")

    def test_url(self):
        class TestDoc(ParsedDocument):
            @URL()
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
            result = TestDoc.load(doc)
            self.assertEquals(result.a, url)

        doc = """
        a: this is a test
        """
        self.assertRaises(Invalid, TestDoc.load, doc)

        result = TestDoc.load("")
        self.assertEquals(result.a, "http://www.google.com")

    def test_ipaddress(self):
        class TestDoc(ParsedDocument):
            @IPAddress()
            def a(self): 
                return "10.1.2.3"

        doc = """
        a: 10.10.10.10
        """ 
        result = TestDoc.load(doc)
        self.assertEquals(result.a, '10.10.10.10')

        doc = """
        a: 350.2.300.1
        """
        self.assertRaises(Invalid, TestDoc.load, doc)

        result = TestDoc.load("")
        self.assertEquals(result.a, "10.1.2.3")

    def test_cidr(self):
        class TestDoc(ParsedDocument):
            @CIDR()
            def a(self): 
                return "10.1.2.3/24"

        doc = """
        a: 10.10.10.10
        """ 
        result = TestDoc.load(doc)
        self.assertEquals(result.a, '10.10.10.10')

        doc = """
        a: 10.10.10.10/24
        """ 
        result = TestDoc.load(doc)
        self.assertEquals(result.a, '10.10.10.10/24')

        doc = """
        a: 350.2.300.1
        """
        self.assertRaises(Invalid, TestDoc.load, doc)

        doc = """
        a: 10.10.10.10/2
        """
        self.assertRaises(Invalid, TestDoc.load, doc)

        result = TestDoc.load("")
        self.assertEquals(result.a, "10.1.2.3/24")

    def test_macaddress(self):
        class TestDoc(ParsedDocument):
            @MACAddress()
            def a(self): 
                return "aabbccddeeff"

        doc = """
        a: 00:11:22:33:44:55
        """ 
        result = TestDoc.load(doc)
        self.assertEquals(result.a, "001122334455")

        doc = """
        a: 00:11:22:33:44:jj
        """
        self.assertRaises(Invalid, TestDoc.load, doc)

        result = TestDoc.load("")
        self.assertEquals(result.a, "aabbccddeeff")

    def test_chaining(self):

        class TestDoc(ParsedDocument):
            @Regex("^([a-dz0-9][a-dz0-9]:?){6}$")
            @MACAddress()
            def a(self): 
                return "aaaaaaaaaaaa"

        # Fail the mac address but not the regex
        doc = """
        a: az:11:22:33:44:55
        """ 
        self.assertRaises(Invalid, TestDoc.load, doc)

        # Fail the regex but not the mac address
        doc = """
        a: af:11:22:33:44:55
        """ 
        self.assertRaises(Invalid, TestDoc.load, doc)

        # Fail both
        doc = """
        a: xx:11:22:33:44:55
        """ 
        self.assertRaises(Invalid, TestDoc.load, doc)

        # Succeed both
        doc = """
        a: aa:11:22:33:44:55
        """ 
        result = TestDoc.load(doc)
        self.assertEquals(result.a, "aa1122334455")

        class TestDoc(ParsedDocument):
            @MACAddress()
            @String()
            def a(self): 
                return "aaaaaaaaaaaa"

        doc = """
        a: af:11:22:33:44:55
        """ 
        result = TestDoc.load(doc)
        self.assertEquals(result.a, "af1122334455")

        doc = """
        a: b
        """ 
        self.assertRaises(Invalid, TestDoc.load, doc)


if __name__ == "__main__":
    unittest.main()

