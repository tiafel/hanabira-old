# -*- coding: utf-8 -*-

from .base import *

import logging
log = logging.getLogger(__name__)

class MakoView(BaseView):
    def __init__(self, template):
        self.template = template
        
    def make_xhtml(self):
        return render(self.template)