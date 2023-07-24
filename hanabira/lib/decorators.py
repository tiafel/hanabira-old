# -*- coding: utf-8 -*-

from inspect import getargspec
from decorator import decorator

import logging
log = logging.getLogger(__name__)

def make_args_for_spec(spec, kw, has_self=True):
    if spec.keywords:
        return kw
    args = {}
    argnames = spec[0][has_self and 1 or 0:]
    for name in argnames:
        if name in kw:
            args[name] = kw[name]
    return args
