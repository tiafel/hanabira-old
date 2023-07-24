# -*- coding: utf-8 -*-

from .base import *

import logging
log = logging.getLogger(__name__)

__all__ = ['DataView']

class DataView(BaseView):
    def __init__(self, obj):
        self.obj = obj
    
    def make_xhtml(self):
        return repr(self.obj)
    
    def make_dict(self):
        return self.obj

result_true = DataView(True)
result_false = DataView(False)