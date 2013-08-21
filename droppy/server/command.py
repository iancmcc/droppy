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
from gevent import monkey, wsgi
monkey.patch_all()

import logging

import bottle

from droppy.command import Subcommand
from .server import ServerFarm


log = logging.getLogger("droppy.server")


class ServerSubcommand(Subcommand):
    def __init__(self):
        Subcommand.__init__(self, "server", "Run the server")

    def configure(self, parser):
        parser.add_argument("--test", help="A test")

    def _log_routes(self, app):
        msg = ["The following routes were found:", ""]
        for route in sorted(app.routes, key=lambda r: r.rule):
            msg.append("\t{method}\t{rule}\t{module}.{func}".format(module=route.callback.__module__,
                                                                    func=route.callback.__name__, **route.__dict__))
        msg.append("")
        log.info('\n'.join(msg))

    def configure_logging(self, config):
        logging.basicConfig(format=config.logging.format,
                            level=config.logging.level)

    def run(self, app):
        self.configure_logging(app.config)

        http = app.config.http
        host, port, admin = http.host, http.port, http.adminPort
        servers = []

        class DroppyGeventServer(bottle.ServerAdapter):
            def run(self, handler):
                servers.append(wsgi.WSGIServer((self.host, self.port), handler, log="default"))

        farm = ServerFarm(2)

        app._main_bottle = main_app = bottle.default_app()
        app._admin_bottle = admin_app = bottle.Bottle()
        app._on_server.set()

        log.info("Starting %s" % app.name)

        log.info("Starting admin server...")
        admin_app.run(host=host, port=admin, server=DroppyGeventServer)
        self._log_routes(admin_app)

        log.info("Starting main server...")
        main_app.run(host=host, port=port, server=DroppyGeventServer)
        self._log_routes(main_app)

        for server in servers:
            farm.add(server)

        farm.serve_forever(2)

