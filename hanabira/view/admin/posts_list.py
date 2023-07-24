# -*- coding: utf-8 -*-

from ..base import *
from hanabira.model.warnings import reasons_list_short

import logging
log = logging.getLogger(__name__)

"""
/admin/posts_list.mako
/admin/post_inspect.mako
/admin/thread_inspect.mako
"""

class AdminPostsListView(BaseView):
    def __init__(self, posts, extended=False, has_lookup=True):
        self.posts = posts
        self.extended = extended
        self.has_lookup = has_lookup
        
        if extended and posts[0].op:
            self.is_thread = True
        else:
            self.is_thread = False
        
        
    def make_xhtml(self):
        c.view = self
        c.posts = self.posts
        self.admin = session.admin
        self.can_view_ip = session.get_token('view_ip')
        self.warn_reasons_list = reasons_list_short
        return render('/admin/posts_list.mako')
    
    @property
    def style_top_tab(self):
        if len(self.posts) > 1:
            return "border: 2px solid; margin-top: 2px"
        else:
            return ""
        
    @property
    def style_panel_thread(self):
        if self.is_thread:
            return ""
        else:
            return "display:none"
        
    @property
    def style_panel_lookup(self):
        if self.extended and self.has_lookup:
            return ""
        else:
            return "display:none"
    
    @property
    def style_panel_user(self):
        return "display:none"