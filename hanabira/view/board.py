# -*- coding: utf-8 -*-

from .base import *
from . import thread
from . import post

ThreadView = thread.ThreadView
PostView = post.PostView

import logging
log = logging.getLogger(__name__)

class BoardView(BaseView):
    board = None
    threads = None
    message_html = False
    message_raw = True    
    def __init__(self, board, threads=None):
        self.board = board
        self.threads = threads
        
    def make_dict(self):
        board = self.board
        r = dict(
            id=board.id,
            board=board.board,
            title=board.title,
            description=board.description,
            bump_limit=board.bump_limit,
            restrict_read=board.restrict_read,
            restrict_new_thread=board.restrict_new_thread,
            restrict_new_reply=board.restrict_new_reply,
            archive=board.archive,

            require_captcha=board.require_captcha,
            require_thread_file=board.require_thread_file,
            require_post_file=board.require_post_file,
            require_new_file=board.require_new_file,
            allow_files=board.allow_files,
            keep_filenames=board.keep_filenames,
            allowed_filetypes=board.allowed_filetypes,
            file_max_size=board.file_max_size,
            file_max_res=board.file_max_res,
            files_max_qty=board.files_max_qty,

            allow_names=board.allow_names,
            remember_name=board.remember_name,
            allow_delete_threads=board.allow_delete_threads,
            delete_thread_post_limit=board.delete_thread_post_limit,
            allow_OP_moderation=board.allow_OP_moderation,
            allow_custom_restricts=board.allow_custom_restricts,
            restrict_trip=board.restrict_trip,
            )
        r['__class__'] = board.__class__.__name__
        if self.threads:
            threads_dicts = []
            threads = list(self.threads)
            thread_view = ThreadView(threads.pop(0), board=board)
            thread_view.message_html = self.message_html
            thread_view.message_raw = self.message_raw            
            threads_dicts.append(thread_view.make_dict())
            while threads:
                thread_view.set_thread(threads.pop(0))
                threads_dicts.append(thread_view.make_dict())
            r['threads'] = threads_dicts
        return r

class BoardsView(BaseView):
    boards = None
    def __init__(self, boards):
        self.boards = boards
    
    def make_dict(self):
        boards = []
        for board, threads in self.boards.items():
            boards.append(BoardView(board, threads).make_dict())
        return boards

thread.BoardView = BoardView
post.BoardView = BoardView