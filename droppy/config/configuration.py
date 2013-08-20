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
import logging
from droppy.validation import ParsedDocument, String, Int, ParsedProperty
from droppy.validation import DictConverter


_LEVEL_CONVERSIONS = {
    10: logging.DEBUG,
    20: logging.INFO,
    30: logging.WARN,
    40: logging.ERROR,
    50: logging.CRITICAL,
    "debug": logging.DEBUG,
    "DEBUG": logging.DEBUG,
    "info": logging.INFO,
    "INFO": logging.INFO,
    "warn": logging.WARN,
    "WARN": logging.WARN,
    "error": logging.ERROR,
    "ERROR": logging.ERROR,
    "critical": logging.CRITICAL,
    "CRITICAL": logging.CRITICAL
}


class Configuration(ParsedDocument):
    """
    Base class for configurations.
    """


class ServerConfiguration(Configuration):

    @String()
    def host(self):
        """
        Host to which the HTTP server should bind.
        """
        return '127.0.0.1'

    @Int()
    def port(self):
        """
        The TCP/IP port on which to listen for incoming connections.
        """
        return 5000
    
    @Int()
    def adminPort(self):
        """
        The TCP/IP port on which the admin server should listen for
        incoming connections.
        """
        return 55000


class LoggingConfiguration(Configuration):

    @String()
    def format(self):
        return "%(levelname)s  [%(asctime)-15s] %(name)s: %(msg)s"

    @DictConverter(_LEVEL_CONVERSIONS)
    def level(self):
        return logging.INFO


class DroppyConfiguration(Configuration):

    @ParsedProperty
    def http(self):
        return ServerConfiguration()

    @ParsedProperty
    def logging(self):
        return LoggingConfiguration()




