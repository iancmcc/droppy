#
# Copyright (c) 2013 Ian McCracken. All rights reserved.
#
from __future__ import absolute_import

import yaml
from collections import defaultdict
from functools import wraps, update_wrapper
from pyxdeco import class_level_decorator


MARKER = object()


class Document(object):
    """
    Represents a YAML document.
    """
    _props = {}

    def __init__(self):
        self._values = defaultdict(lambda:MARKER)

    def _apply(self, values):
        """
        Apply parsed values to a document.
        """
        try:
            for k, v in values.iteritems():
                prop = self._props.get(k)
                if prop is not None:
                    prop.__set__(self, v)
        except AttributeError:
            pass

    @classmethod
    def load(cls, raw):
        """
        Parse a document according to this schema.
        """
        inst = cls()
        loaded = yaml.load(raw)
        inst._apply(loaded)
        return inst

    @staticmethod
    @class_level_decorator
    def YAMLProperty(func, cls):
        prop = _YAMLProperty(func)
        cls._props[func.__name__] = prop
        setattr(cls, func.__name__, prop)


class _YAMLProperty(object):

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

