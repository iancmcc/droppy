#
# Copyright (c) 2013 Ian McCracken. All rights reserved.
#
from __future__ import absolute_import

import json
import yaml
from collections import defaultdict, Mapping
from functools import wraps, update_wrapper
from pyxdeco.advice import addClassAdvisor
from formencode import Schema, FancyValidator


MARKER = object()


class Document(Schema):
    """
    Represents a parseable document.
    """
    @classmethod
    def loadYAML(cls, raw):
        """
        Parse a document according to this schema.
        """
        inst = cls()
        loaded = yaml.load(raw)
        inst.results = inst.to_python(loaded)
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
        inst.results = inst.to_python(loaded)
        return inst

    def __getattr__(self, attr):
        try:
            result = getattr(self, 'fields', {})[attr]
            if isinstance(result, Property):
                result = getattr(self, 'results', {})[attr]
            return result
        except KeyError:
            raise AttributeError(attr)


class Property(FancyValidator):
    def __init__(self, func):
        self._func = func
        update_wrapper(self, func)
        addClassAdvisor(self._on_class)

    def _on_class(self, cls):
        method = self._func.__get__(cls(), cls)
        default = method()
        if isinstance(default, Schema):
            cls.fields[self.__name__] = default
        else:
            self.if_missing = default
        self.state = cls
        return cls

