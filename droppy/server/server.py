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

from gevent import spawn
from gevent.pool import Pool
from gevent.event import Event


class ServerFarm(object):
    def __init__(self, size=None):
        self.started = False
        self.servers = []
        self.pool = Pool(size)
        self._stop_event = Event()
        self._stop_event.set()

    def add(self, server):
        self.servers.append(server)
        server.set_spawn(self.pool.spawn)

    def start(self):
        self.started = True
        self._stop_event.clear()
        for server in self.servers:
            server.start()

    def stop(self, timeout=None):
        self._stop_event.set()
        for server in self.servers[:]:
            server.stop()
        self.pool.join(timeout=timeout)
        self.pool.kill(block=True, timeout=1)

    def serve_forever(self, stop_timeout=None):
        if not self.started:
            self.start()
        try:
            self._stop_event.wait()
        except KeyboardInterrupt:
            sys.exit(0)
        finally:
            spawn(self.stop, timeout=stop_timeout).join()



