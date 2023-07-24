# -*- coding: utf-8 -*-

from .base import *

import logging
log = logging.getLogger(__name__)

class UserSessionView(BaseView):
    def __init__(self, sess):
        self.session = sess
        
    def make_dict(self):
        sess = self.session
        r = {
            '__class__':'UserSession',
            'id': sess.id,
            #admin_id=self.admin_id,
            'password': sess['password'],
            'language': sess['language'],
            'notifications': [],
            'tokens': sess.get_tokens(),
            }
        if 'threads' in request.GET:
            levels = request.GET.get('thread-level', 
                                     'bookmarked,replied,op,hidden').split(',')
            r['threads'] = sess.get_threads(levels=levels)
        return r