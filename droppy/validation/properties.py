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

    def to_python(self, *args, **kwargs):
        results = super(Document, self).to_python(*args, **kwargs)
        for k, v in results.iteritems():
            field = self.fields.get(k)
            if isinstance(field, Document):
                v = field
            setattr(self, k, v)
        return results


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
            print "Setting default of", self.__name__, "to", default
            self.if_missing = default
        return cls

