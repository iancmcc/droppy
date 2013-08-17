#
# Copyright (c) 2013 Ian McCracken. All rights reserved.
#
from functools import wraps, update_wrapper
import inspect

from decorator import decorator
import formencode.validators as fv
from formencode.compound import All

from .properties import Property, Document

def validator_decorator(base, **extra_kwargs):
    defaults = {
        'strip': True
    }
    defaults.update(extra_kwargs)
    @wraps(base)
    def factory(*args, **kwargs):
        def the_decorator(prop):
            if not isinstance(prop, fv.Validator):
                prop = Property(prop)
            defaults.update(kwargs)
            validator = base(*args, **defaults)
            compound = All(prop, validator)
            return compound
        return the_decorator
    return factory

StringBool = validator_decorator(fv.StringBool)
Bool = validator_decorator(fv.Bool)
Int = validator_decorator(fv.Int)
Number = validator_decorator(fv.Number)
UnicodeString = validator_decorator(fv.UnicodeString)
Set = validator_decorator(fv.Set)
String = validator_decorator(fv.String)

NotEmpty = validator_decorator(fv.NotEmpty)
ConfirmType = validator_decorator(fv.ConfirmType)
Constant = validator_decorator(fv.Constant)
OneOf = validator_decorator(fv.OneOf)
StripField = validator_decorator(fv.StripField, accept_iterator=True)
DictConverter = validator_decorator(fv.DictConverter)
IndexListConverter = validator_decorator(fv.IndexListConverter)

MaxLength = validator_decorator(fv.MaxLength)
MinLength = validator_decorator(fv.MinLength)
Regex = validator_decorator(fv.Regex)
PlainText = validator_decorator(fv.PlainText)

Email = validator_decorator(fv.Email)
URL = validator_decorator(fv.URL)
IPAddress = validator_decorator(fv.IPAddress)
CIDR = validator_decorator(fv.CIDR)
MACAddress = validator_decorator(fv.MACAddress)


