# -*- coding: utf-8 -*-

from .base import *
from . import post

PostView = post.PostView

import logging
log = logging.getLogger(__name__)

class ThreadView(BaseView):
    thread = None
    board = None
    message_html = False
    message_raw = True
    post_html = False
    def __init__(self, thread, board=None):
        self.set_board(board)
        self.set_thread(thread)
        
    def set_board(self, board):
        self.board = board
        self.see_invisible = (session.admin and 
                              session.admin.has_permission('see_invisible', self.board.id))
        
    def set_thread(self, thread):
        self.thread = thread
        
    def make_dict(self):
        thread = self.thread
        r = {
            '__class__': thread.__class__.__name__,
            'thread_id':thread.thread_id,
            'board_id': thread.board_id,
            'display_id':thread.display_id,
            'archived':thread.archived,
            'autosage':thread.autosage,
            'title':thread.title,
            'created':str(thread.created),
            'last_hit':str(thread.last_hit),
            'last_modified':str(thread.last_modified),
            'posts_count':thread.posts_count,
            'files_count':thread.files_count
        }
        
        if thread.posts:
            posts = []            
            post_view = PostView(None)
            post_view.set_thread(thread, self.board)
            post_view.message_html = self.message_html
            post_view.message_raw = self.message_raw
            post_view.post_html = self.post_html
            for post in thread.posts:
                post_view.set_post(post)
                if self.post_html:
                    posts.append(post_view.make_xhtml())
                else:
                    posts.append(post_view.make_dict())
            r['posts'] = posts
        if self.see_invisible:
            r['invisible'] = thread.invisible
        return r        
    
class ThreadAPIView(BaseView):    
    # '/api/posts_list.mako'    
    def __init__(self, thread, board, post_html=False):
        if 'board' in request.GET:
            self.view = BoardView(board=board, threads=[thread])
        else:
            self.view = ThreadView(thread, board=board)    
        if 'message_html' in request.GET:
            self.view.message_html = True
            self.view.message_raw = 'message_raw' in request.GET
        self.view.post_html = post_html
    
    def make_dict(self):
        return self.view.make_dict()
    
    def make_xhtml(self):
        return self.view.make_xhtml()
        
post.ThreadView = ThreadView