#
# Copyright (c) 2013 Ian McCracken. All rights reserved.
#
from types import FunctionType
from functools import wraps
import inspect

from pyxdeco import class_level_decorator
from pyxdeco.advice import addClassAdvisor
import formencode.validators as fv

from formencode.validators import Validator
from formencode.compound import All

from .properties import Property


def autocall_decorator(func):

    def isFuncArg(*args, **kw):
        return len(args) == 1 and len(kw) == 0 and (
            inspect.isfunction(args[0]) or isinstance(args[0], type))

    if isinstance(func, type):
        def class_wrapper(*args, **kw):
            if isFuncArg(*args, **kw):
                return func()(*args, **kw) # create class before usage
            return func(*args, **kw)
        class_wrapper.__name__ = func.__name__
        class_wrapper.__module__ = func.__module__
        return class_wrapper

    @wraps(func)
    def func_wrapper(*args, **kw):
        if isFuncArg(*args, **kw):
            return func(*args, **kw)
        def functor(userFunc):
            return func(userFunc, *args, **kw)
        return functor
    return func_wrapper


def validator_decorator(base):
    @wraps(base)
    @autocall_decorator
    def decorator(prop, *args, **kwargs):
        if not isinstance(prop, Validator):
            prop = Property(prop, 2)
        validator = base(*args, **kwargs)
        compound = All(prop, validator)
        return compound
    return decorator


StringBool = validator_decorator(fv.StringBool)
Bool = validator_decorator(fv.Bool)
Int = validator_decorator(fv.Int)
Number = validator_decorator(fv.Number)
UnicodeString = validator_decorator(fv.UnicodeString)

NotEmpty = validator_decorator(fv.NotEmpty)
ConfirmType = validator_decorator(fv.ConfirmType)
Constant = validator_decorator(fv.Constant)
OneOf = validator_decorator(fv.OneOf)
DictConverter = validator_decorator(fv.DictConverter)
