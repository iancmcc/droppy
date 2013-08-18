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

class Subcommand(object):
    """
    Represents a subcommand that may be executed from the command line.
    You can add custom parser options.
    """
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def configure(self, parser):
        """
        Add options to the subparser for this command.
        """
        raise NotImplementedError

    def run(self, app):
        """
        Do whatever you would do with this guy.
        """
        raise NotImplementedError

