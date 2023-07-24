# -*- coding: utf-8 -*-
import simplejson
import logging
from datetime import datetime

from pylons import app_globals as g

from hanabira.model import meta
from hanabira.model.threads import Thread

log = logging.getLogger(__name__)

class Bookmarks(object):
    threads = None
    boards  = None
    visits  = None
    def __init__(self, _old=None):
        self.threads = {}
        self.boards  = {}
        self.visits  = {}
        if _old:
            for b in _old:
                board = g.boards.get(b)
                self.boards[b] = []
                threads = board.thread_filters(archive=None).filter(Thread.display_id.in_(_old[b])).all()
                for thread in threads:
                    self.boards[b].append(thread.id)
                    self.visits[thread.id] = thread.last_hit
                    self.threads[thread.id] = board.board

    def is_faved(self, thread_id):
        return thread_id in self.threads

    def add(self, thread_id):
        if not thread_id in self.threads:
            thread = Thread.query.get(thread_id)
            if thread:
                board = thread.board
                if not board.board in self.boards:
                    self.boards[board.board] = []
                self.boards[board.board].append(thread.id)
                self.visits[thread.id] = datetime.now()
                self.threads[thread.id] = board.board

    def remove(self, thread_id):
        if thread_id in self.threads:
            board = self.threads[thread_id]
            del self.visits[thread_id]
            self.boards[board].remove(thread_id)
            del self.threads[thread_id]

    def get_threads(self):
        """
        Return dict {id:thread}
        """
        threads = Thread.query.filter(Thread.display_id != None).filter(Thread.thread_id.in_(self.threads.keys())).all()
        result  = {}
        for thread in threads:
            result[thread.id] = thread
        return result

    def get_boards(self, admin, channel):
        """
        Return [(board, board threads)]
        """
        threads = self.get_threads()
        result = []
        for bname in self.boards:
            board = g.boards.get(bname)
            if board and board.check_permissions('read', admin, channel):
                bthreads = []
                for tid in self.boards[bname]:
                    thread = threads.get(tid, None)
                    if thread:
                        bthreads.append(thread)
                if bthreads:
                    result.append((board, bthreads))
        return result

    def get_visit(self, thread_id):
        if thread_id in self.visits:
            return self.visits[thread_id]
        else:
            return None

    def visited(self, thread_id, date=None):
        if not date:
            date = datetime.now()
        if thread_id in self.threads:
            self.visits[thread_id] = date
                
