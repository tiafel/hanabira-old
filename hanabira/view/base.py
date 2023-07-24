# -*- coding: utf-8 -*-

from pylons import tmpl_context as c, request, response, session, app_globals as g
from pylons.i18n import _, ungettext, N_, get_lang, set_lang
from hanabira.lib.trace import render
import json

import logging
log = logging.getLogger(__name__)

class BaseView(object):
    is_error = False
    def render(self, format):
        if format == 'xhtml':
            return self.make_xhtml()
        elif format in ['js', 'json']:
            json = self.make_json()
            response.headers['Content-Type'] = 'application/json'            
            return json
        
    def make_xhtml(self):
        return "Not Implemented"
    
    def make_dict(self):
        raise NotImplementedError("Should be subclassed")
    
    def make_json(self):
        if (not 'new_format' in request.GET and
            not 'new_format' in request.environ['pylons.routes_dict']):
            return self.make_json_old()
        if self.is_error:
            d = {'error':self.make_dict()}
        else:
            d = {'result':self.make_dict()}
        json = JSONEncoder().encode(d)
        return json
    
    def make_json_old(self):
        return JSONEncoder().encode(self.make_dict())
    
    
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        return o.make_dict()