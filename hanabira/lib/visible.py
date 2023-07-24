# -*- coding: utf-8 -*-
import logging
log = logging.getLogger(__name__)

class VisiblePosts(object):
    cont = None

    def __init__(self):
        self.cont = {}

    def get_board(self, board_id):
        return self.cont.get(board_id, {'threads':[], 'posts':{}})
    
    def get_threads(self, board_id):
        return self.get_board(board_id)['threads']

    def add_thread(self, thread):
        self.cont.setdefault(thread.board_id, {'threads':[], 'posts':{}})
        self.cont[thread.board_id]['threads'].append(thread.id)

    def remove_thread(self, thread):
        self.cont.setdefault(thread.board_id, {'threads':[], 'posts':{}})
        if thread.id in self.cont[thread.board_id]['threads']:
            self.cont[thread.board_id]['threads'].remove(thread.id)

    def get_posts(self, thread):
        return self.get_board(thread.board_id)['posts'].get(thread.thread_id, {}).keys()

    def add_post(self, post, thread):
        """
        Будем хранить в виде post_id:bump_date, где bump_date == date при sage==False, и == None при True
        """
        bump_date = not post.sage and post.date or None
        self.cont.setdefault(thread.board_id, {'threads':[], 'posts':{}})
        self.cont[thread.board_id]['posts'].setdefault(thread.thread_id, {})
        self.cont[thread.board_id]['posts'][thread.thread_id][post.post_id] = bump_date

    def has_post(self, post, board):
        posts = self.get_board(board.board_id)['posts']
        if post.thread_id in posts:
            if post.post_id in posts[post.thread_id]:
                return True
        return False
        
    def has_thread(self, thread):
        return thread.id in self.cont.get(thread.board_id, {'threads':[]})['threads']

    def remove_post(self, post, thread):
        posts = self.get_board(thread.board_id)['posts']
        if post.thread_id in posts:
            if post.post_id in posts[post.thread_id]:
                del posts[post.thread_id][post.post_id]

    def get_bumps(self, board_id):
        """
        Возвращаем номера постов, которые
        1) Имеют дату
        2) Были последние в треде из постов этого юзера
        """
        posts = self.get_board(board_id)['posts']
        bumps = {}
        for tid in posts:
            thread_posts = posts[tid]
            thread_bumps = sorted(filter(lambda x:thread_posts[x], thread_posts))
            if thread_bumps:
                bumps[tid] = thread_posts[thread_bumps[-1]]
                #            bumps[thread_bumps[-1]] = {'d':thread_posts[thread_bumps[-1]], 't':tid}

        return bumps

    def __repr__(self):
        return self.cont.__repr__()
        
def ensure_visible(sess):
    if not sess: return
    if not 'visible_posts' in sess or sess['visible_posts'].__class__ != VisiblePosts:
        sess['visible_posts'] = VisiblePosts()
    return sess['visible_posts']

