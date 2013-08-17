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
import os.path as op

from droppy.config import DroppyConfiguration, load_configuration
from droppy.config import ConfigurationException
from droppy.validation import Int, String, Regex


_in_cfg = lambda *x:op.join(op.dirname(__file__), 'config', *x)

class MyConfig(DroppyConfiguration):
    @Int()
    def some_value(self):
        return 1

    @String()
    def another(self):
        return "abc"


class BadConfig(DroppyConfiguration):
    @Int()
    def some_value(self):
        return 1

    @Regex('^nomatch$')
    def another(self):
        return "abc"


class NotAConfiguration(object):
    pass


class TestLoading(unittest.TestCase):

    def test_load_by_extension(self):
        for fname in map(_in_cfg, (
            "myconfig.yaml", "myconfig.yml", "myconfig.json")):
            result = load_configuration(MyConfig, fname)
            self.assertEquals(result.some_value, 10)
            self.assertEquals(result.another, "a value")

    def test_load_no_extension(self):
        for fname in map(_in_cfg, ("myjsonconfig.conf", "myyamlconfig.conf")):
            result = load_configuration(MyConfig, fname)
            self.assertEquals(result.some_value, 10)
            self.assertEquals(result.another, "a value")

    def test_invalid(self):
        filename = _in_cfg("myconfig.yaml")
        self.assertRaises(ConfigurationException, load_configuration,
                          BadConfig, filename)

    def test_badfilename(self):
        filename = _in_cfg("notafilename.conf")
        self.assertRaises(ConfigurationException, load_configuration,
                          MyConfig, filename)

    def test_notconfiguration(self):
        filename = _in_cfg("myconfig.yaml")
        self.assertRaises(ConfigurationException, load_configuration,
                          NotAConfiguration, filename)

    def test_neither_yaml_nor_json(self):
        filename = _in_cfg("badconfig.conf")
        self.assertRaises(ConfigurationException, load_configuration,
                          MyConfig, filename)



if __name__ == "__main__":
    unittest.main()
