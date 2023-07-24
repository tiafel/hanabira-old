# -*- coding: utf-8 -*-

from .base import *

import logging
log = logging.getLogger(__name__)

BoardView = None

class PostView(BaseView):
    post = None
    message_html = False
    message_raw = True
    post_html = False
    def __init__(self, post):
        self.post = post
        if post:
            self.set_thread(post.thread, g.boards.get(id=post.thread.board_id))
        
    def set_thread(self, thread, board):
        self.thread = thread
        self.board = board
        self.see_invisible = (session.admin and 
                              session.admin.has_permission('see_invisible', self.board.id))
        
    def set_post(self, post):
        self.post = post
        
    def make_xhtml(self):
        c.board = self.board
        c.get_reflink = True
        c.reply = True
        c.reputation_min = session.get('reputation_min', -5)
        self.board.set_context_permissions(c, c.admin)
        return render('/view/post.mako',
                      {'thread':self.thread, 'board':self.board, 'post':self.post, 'need_wrap':self.post_html})
    
    def make_dict(self):
        obj = self.post
        r = {
            '__class__': obj.__class__.__name__,
            'post_id': obj.post_id,
            'display_id': obj.display_id,
            'thread_id': obj.thread_id,
            'board_id': obj.board_id,
            'subject': obj.subject,
            'name': obj.name,
            'date': str(obj.date),
            'last_modified': obj.last_modified and str(obj.last_modified) or None,
            'op': obj.op,
            'files': list(map(lambda x:x.export_dict(), obj.files))
        }
        
        if self.message_raw:
            r['message'] = obj.message_raw
        if self.message_html:
            r['message_html'] = obj.message
            
        if self.see_invisible:
            r['invisible'] = obj.invisible
            r['inv_reason'] = obj.inv_reason
            r['sage'] = obj.sage
        return r 
    
class PostAPIView(BaseView):
    def __init__(self, post, thread, board):
        if 'thread' in request.GET:
            thread.posts = [post]
            self.view = BoardView(board, threads=[thread])
        else:
            self.view = PostView(post)
        if 'message_html' in request.GET:
            self.view.message_html = True
            self.view.message_raw = 'message_raw' in request.GET
    
    def make_dict(self):
        return self.view.make_dict()
    
    def make_xhtml(self):
        return self.view.make_xhtml()
