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
from formencode import Invalid
from .exceptions import ConfigurationException
from .configuration import DroppyConfiguration


__all__ = ["ConfigurationException", "DroppyConfiguration",
           "load_configuration"]


def load_configuration(klass, filename):
    if not issubclass(klass, DroppyConfiguration):
        raise ConfigurationException(
            "Configuration must subclass droppy.config.DroppyConfiguration")
    try:
        with open(filename, 'r') as config_file:
            try:
                return klass.load(config_file)
            except ValueError:
                raise ConfigurationException(
                    "Unable to parse {0} as either YAML or JSON.".format(
                        filename))
            except Invalid as e:
                raise ConfigurationException("{0} failed to validate: {1}".format(
                    filename, e.msg))
    except IOError:
        raise ConfigurationException(
            "Couldn't open file {0}; does it exist?".format(filename))

