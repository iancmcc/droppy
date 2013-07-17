from types import FunctionType
from functools import wraps
import inspect

from pyxdeco import class_level_decorator
import formencode.validators as fv

#from .properties import ensure_property


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


class Validator(object):

    def __init__(self, base):
        self._base = base

    def apply(self, *args, **kwargs):
        return self._base.to_python(*args, **kwargs)


def validator_factory(base):
    @wraps(base)
    @autocall_decorator
    def decorator(prop, *args, **kwargs):
        prop = ensure_property(prop, depth=5)
        validator = Validator(base(*args, **kwargs))
        prop.add_validator(validator)
        return prop
    return decorator


NotEmpty = validator_factory(fv.NotEmpty)
