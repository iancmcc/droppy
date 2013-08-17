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
import json
from functools import update_wrapper

import yaml
from pyxdeco.advice import addClassAdvisor, getFrameInfo
from formencode import Schema, FancyValidator
from formencode.api import NoDefault


class ParsedDocument(Schema):
    """
    Represents a document loaded from YAML or JSON that may have properties
    defined.
    """
    NoDefault = NoDefault

    @classmethod
    def loadYAML(cls, raw):
        """
        Parse a document according to this schema.
        """
        inst = cls()
        loaded = yaml.load(raw)
        inst.to_python(loaded)
        return inst

    @classmethod
    def loadJSON(cls, raw):
        """
        Parse a JSON document.
        """
        inst = cls()
        if isinstance(raw, basestring):
            loaded = json.loads(raw)
        else:
            loaded = json.load(raw)
        inst.to_python(loaded)
        return inst

    @classmethod
    def loadDict(cls, raw):
        """
        Build a document from a dictionary.
        """
        inst = cls()
        inst.to_python(raw)
        return inst

    def list_properties(self):
        return self.fields.keys()

    def to_python(self, *args, **kwargs):
        results = super(ParsedDocument, self).to_python(*args, **kwargs)
        for k, v in results.iteritems():
            field = self.fields.get(k)
            if isinstance(field, ParsedDocument):
                v = field
            setattr(self, k, v)
        return results


class ParsedProperty(FancyValidator):
    def __init__(self, func):
        self._func = func
        self.accept_iterator = True
        update_wrapper(self, func)
        _addClassAdvisorToNearestClass(self._on_class)
        super(FancyValidator, self).__init__()

    def _on_class(self, cls):
        method = self._func.__get__(cls(), cls)
        default = method()
        if isinstance(default, Schema):
            cls.fields[self.__name__] = default
        else:
            self.if_missing = default
        return cls


def _addClassAdvisorToNearestClass(advisor):
    """
    Walk frames until a class is found, rather than using a static depth.
    """
    depth = 0
    while True:
        try:
            frame = sys._getframe(depth)
        except ValueError:
            raise Exception(
                "Droppy validators must be used to decorate methods")
        kind, module, caller_locals, caller_globals = getFrameInfo(frame)
        if kind == 'class':
            break
        depth += 1
    addClassAdvisor(advisor, depth + 1)

