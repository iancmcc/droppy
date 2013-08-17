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
from functools import wraps

import formencode.validators as fv
from formencode.compound import All

from .properties import ParsedProperty


def _validator_decorator(base, **extra_kwargs):
    defaults = {
        'strip': True
    }
    defaults.update(extra_kwargs)

    @wraps(base)
    def factory(*args, **kwargs):
        def the_decorator(prop):
            if not isinstance(prop, fv.Validator):
                prop = ParsedProperty(prop)
            defaults.update(kwargs)
            validator = base(*args, **defaults)
            compound = All(prop, validator)
            return compound

        return the_decorator

    return factory


StringBool = _validator_decorator(fv.StringBool)
Bool = _validator_decorator(fv.Bool)
Int = _validator_decorator(fv.Int)
Number = _validator_decorator(fv.Number)
UnicodeString = _validator_decorator(fv.UnicodeString)
Set = _validator_decorator(fv.Set)
String = _validator_decorator(fv.String)

NotEmpty = _validator_decorator(fv.NotEmpty)
ConfirmType = _validator_decorator(fv.ConfirmType)
Constant = _validator_decorator(fv.Constant)
OneOf = _validator_decorator(fv.OneOf)
StripField = _validator_decorator(fv.StripField, accept_iterator=True)
DictConverter = _validator_decorator(fv.DictConverter)
IndexListConverter = _validator_decorator(fv.IndexListConverter)

MaxLength = _validator_decorator(fv.MaxLength)
MinLength = _validator_decorator(fv.MinLength)
Regex = _validator_decorator(fv.Regex)
PlainText = _validator_decorator(fv.PlainText)

Email = _validator_decorator(fv.Email)
URL = _validator_decorator(fv.URL)
IPAddress = _validator_decorator(fv.IPAddress)
CIDR = _validator_decorator(fv.CIDR)
MACAddress = _validator_decorator(fv.MACAddress)


