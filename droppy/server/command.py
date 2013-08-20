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

import bottle

from droppy.command import Subcommand
from .server import ServerFarm


class ServerSubcommand(Subcommand):
    def __init__(self):
        Subcommand.__init__(self, "server", "Run the server")

    def configure(self, parser):
        parser.add_argument("--test", help="A test")

    def _log_routes(self, app):
        print "Serving routes:"
        for route in sorted(app.routes, key=lambda r: r.rule):
            print "\t{method} {rule} {module}.{func}".format(module=route.callback.__module__,
                                                             func=route.callback.__name__, **route.__dict__)

    def run(self, app):
        http = app.config.http
        host, port, admin = http.host, http.port, http.adminPort
        servers = []

        class DroppyGeventServer(bottle.ServerAdapter):
            def run(self, handler):
                from gevent import wsgi
                log = 'default'
                servers.append(wsgi.WSGIServer((self.host, self.port), handler, log=log))

        farm = ServerFarm(2)

        app._main_bottle = main_app = bottle.default_app()
        app._admin_bottle = admin_app = bottle.Bottle()
        app._on_server.set()

        print "Starting admin server"
        admin_app.run(host=host, port=admin, server=DroppyGeventServer)
        self._log_routes(admin_app)

        print "Starting main server"
        main_app.run(host=host, port=port, server=DroppyGeventServer)
        self._log_routes(main_app)

        for server in servers:
            farm.add(server)


        farm.serve_forever(2)

