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
from functools import update_wrapper
from copy import deepcopy

import yaml
from pyxdeco.advice import addClassAdvisor, getFrameInfo
from formencode import Schema, FancyValidator, Invalid
from formencode.api import NoDefault


_MARKER = object()


def _reset_fields(config_instance):
    for k, v in config_instance.fields.iteritems():
        if isinstance(v, ParsedDocument):
            _reset_fields(v)
            try:
                v.to_python("")
            except Invalid:
                pass


def get_defaults(config_cls):
    d = {}
    for k, v in config_cls.fields.iteritems():
        default = getattr(v, 'if_missing', _MARKER)
        if isinstance(default, ParsedDocument):
            default = get_defaults(default.__class__)
        if default is not _MARKER:
            d[k] = default
    return d


class ParsedDocument(Schema):
    """
    Represents a document loaded from YAML or JSON that may have properties
    defined.
    """
    NoDefault = NoDefault

    @classmethod
    def load(cls, raw):
        """
        Validate a parsed file or dictionary according to this schema.
        """
        inst = cls()
        _reset_fields(inst)

        if isinstance(raw, dict):
            loaded = raw
        else:
            loaded = yaml.load(raw)
        inst.to_python(loaded)
        return inst

    def list_properties(self):
        return self.fields.keys()

    @classmethod
    def default(cls):
        return cls.load({})

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
            try:
                default.if_missing = default.__class__.default()
            except Invalid:
                # No default is possible, because something underneath
                # is required.
                pass
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

