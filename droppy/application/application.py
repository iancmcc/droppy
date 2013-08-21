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
from gevent import monkey
monkey.patch_all()

import sys
import argparse
from gevent.event import Event

import droppy
from droppy.server import ServerSubcommand
from droppy.config import DroppyConfiguration


class Application(object):
    """
    A droppy application.
    """

    def __init__(self, name, config_class=DroppyConfiguration):
        self._name = name
        self._config_class = config_class
        self._subcommands = {}
        self._setup_parser()
        self._server_started = False
        self._on_server = Event()
        self._on_server.clear()
        self.arguments = None

        self._main_bottle = None
        self._admin_bottle = None

        # Set the global instance
        droppy.set_app(self)

    @property
    def name(self):
        return self._name

    @property
    def subcommands(self):
        return self._subcommands.values()

    def initialize(self):
        """
        This is where you add commands.
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
        parser.add_argument('-c', '--config', default=None,
                            help="Path to configuration file")
        self._subparsers = parser.add_subparsers(help="Subcommands")

    def _load_configuration(self, filename):
        if filename is None:
            self.config = self._config_class.load("")
        else:
            with open(filename, 'r') as f:
                self.config = self._config_class.load(f)

    def _add_server_subcommand(self):
        self.add_subcommand(ServerSubcommand())

    @property
    def started(self):
        return self._server_started

    @property
    def server(self):
        self._on_server.wait()
        return self._main_bottle

    @property
    def admin(self):
        self._on_server.wait()
        return self._admin_bottle

    def _split_args(self, args):
        droppy, passthrough = [], []
        gen = (x for x in args)
        for arg in gen:
            if arg == '--':
                break
            droppy.append(arg)
        passthrough.extend(gen)
        return droppy, passthrough

    def run(self):
        args = list(sys.argv)
        self.initialize()
        self._add_server_subcommand()
        args, sys.argv[1:] = self._split_args(args)
        self.arguments = self._parser.parse_args(args[1:])
        self._load_configuration(self.arguments.config)
        self.arguments.subcommand.run(self)


if __name__ == "__main__":

    from bottle import get
    from droppy.validation import String
    import droppy

    class MyConfiguration(DroppyConfiguration):
        @String()
        def name(self):
            return "droppy"

    @get("/name")
    def get_name():
        return droppy.app().config.name

    Application("droppy", MyConfiguration).run()

