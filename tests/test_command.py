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

from droppy.command import Subcommand


class MySubcommand(Subcommand):
    pass



class TestSubcommand(unittest.TestCase):

    def test_parsing(self):
        cmd = MySubcommand("test", "This is a test subcommand")
        pass


if __name__ == "__main__":
    unittest.main()
