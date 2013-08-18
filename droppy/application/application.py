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
import sys
import argparse

from droppy.server import ServerSubcommand


class Application(object):
    """
    A droppy application.
    """
    def __init__(self, name, config_class=None):
        self._name = name
        self._config_class = config_class
        self._subcommands = {}
        self._setup_parser()
        self.arguments = None

    @property
    def name(self):
        return self._name

    @property
    def subcommands(self):
        return self._subcommands.values()

    def initialize(self):
        """
        This is where you set stuff up.
        """
        pass

    def add_subcommand(self, subcommand):
        if subcommand.name in self._subcommands:
            raise ValueError("Subcommand {0} has already been registered."
                             .format(subcommand.name))
        self._subcommands[subcommand.name] = subcommand
        subparser = self._subparsers.add_parser(
            subcommand.name, help=subcommand.description)
        subparser.set_defaults(subcommand=subcommand)
        subcommand.configure(subparser)

    def _setup_parser(self):
        parser = self._parser = argparse.ArgumentParser(
            description=self.__class__.__doc__)
        self._subparsers = parser.add_subparsers(help="Subcommands")
        parser.add_argument('-c', '--config', default=None, 
                            help="Path to configuration file")

    def run(self):
        self.initialize()
        self.add_subcommand(ServerSubcommand())
        self.arguments = self._parser.parse_args()
        self.arguments.subcommand.run(self)


if __name__ == "__main__":
    Application("droppy").run()


