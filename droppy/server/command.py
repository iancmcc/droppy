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

    def run(self, app):
        http = app.config.http
        host, port, admin = http.host, http.port, http.adminPort
        servers = []

        class DroppyGeventServer(bottle.ServerAdapter):
            def run(self, handler):
                from gevent import pywsgi
                log = 'default'
                servers.append(pywsgi.WSGIServer((self.host, self.port), handler, log=log))

        farm = ServerFarm(2)

        self.main_app = bottle.default_app()
        self.admin_app = bottle.Bottle()

        self.main_app.run(host=host, port=port, server=DroppyGeventServer)
        self.admin_app.run(host=host, port=admin, server=DroppyGeventServer)

        for server in servers:
            farm.add(server)

        farm.serve_forever(2)
