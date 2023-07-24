# -*- coding: utf-8 -*-
import logging
from hanabira.lib.base import *
from hanabira.lib.utils import *
from datetime import datetime, timedelta
import simplejson
from hashlib import md5
log = logging.getLogger(__name__)

class ControlController(BaseController):
    def __before__(self):
        BaseController.init_request(self)
        if request.ip != "127.0.0.1":
            return abort(403)

    def reload(self):
        log.info("[!] Reloading all globals")
        log.info("[!] Reloading settings")
        g.settings.load()
        log.info("[!] Reloading boards")
        g.boards.load()
        log.info("[!] Reloading restrictions")
        g.restrictions.load()
        return api_ok()
