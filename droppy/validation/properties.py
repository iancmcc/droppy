#
# Copyright (c) 2013 Ian McCracken. All rights reserved.
#
from __future__ import absolute_import

import json
import yaml
from collections import defaultdict, Mapping
from functools import wraps, update_wrapper
from pyxdeco import class_level_decorator


MARKER = object()


class Document(object):
    """
    Represents a parseable document.
    """
    _props = {}

    def __init__(self):
        self._values = defaultdict(lambda:MARKER)

    def _apply(self, values):
        """
        Apply parsed values to a document.
        """
        if isinstance(values, Mapping):
            for k, v in values.iteritems():
                prop = self._props.get(k)
                if prop is not None:
                    prop.__set__(self, v)

    @classmethod
    def loadYAML(cls, raw):
        """
        Parse a document according to this schema.
        """
        inst = cls()
        loaded = yaml.load(raw)
        inst._apply(loaded)
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
        inst._apply(loaded)
        return inst


@class_level_decorator
def Property(func, cls):
    prop = _Property(func)
    cls._props[func.__name__] = prop
    setattr(cls, func.__name__, prop)


class _Property(object):

    def __init__(self, func):
        update_wrapper(self, func)
        self._func = func
        self._name = func.__name__
        self._default = MARKER
        self._validators = []

    def _get_default(self, instance):
        if self._default is MARKER:
            self._default = self._func.__get__(instance, None)()
        return self._default

    def __get__(self, obj, objtype=None):
        val = obj._values[self._name]
        if val is MARKER:
            return self._get_default(obj)
        return val

    def __set__(self, obj, value):
        default = self._get_default(obj)
        if isinstance(default, Document):
            default._apply(value)
            value = default
        obj._values[self._name] = value

