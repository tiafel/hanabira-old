# -*- coding: utf-8 -*-

from pylons.i18n import _, ungettext, N_, set_lang
from hanabira.model.gorm import *

from .filetype import Filetype

import logging
log = logging.getLogger(__name__)

class FlashFile(Filetype):
    __mapper_args__ = {'polymorphic_identity': u'flash'}
      
    def get_superscription(self):
        return _("Click the image to open file")
