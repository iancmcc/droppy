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
from gevent.event import Event

_ONAPP = Event()
_ONAPP.clear()
_APP = {}

def app():
    if _APP:
        return _APP.itervalues().next()

def set_app(a):
    _APP[None] = a
    _ONAPP.set()

def wait_for_app():
    _ONAPP.wait()
    return app()
