# -*- coding: utf-8 -*-
import logging
from pylons.i18n import _, ungettext, N_
from hanabira.model.files import File
#from hanabira.lib.sphinxapi import *
from hanabira.model.threads import Thread
from hanabira.model.posts import Post, post_files_table
from sqlalchemy.orm import eagerload
from hanabira.model import meta
import math
log = logging.getLogger(__name__)

class Search(object):
    id = None
    count = 0
    threads = None
    query = None
    files = 0
    per_page = 0
    pages = 0
    thread_ids = None
    def __init__(self, id, query, posts, files, per_page):
        self.id = id
        self.query = query
        self.count = 0
        self.pages = 0
        self.per_page = per_page
        self.threads = {}
        self.thread_ids = []
        if 'matches' in posts and posts['matches']:
            log.debug("Posts: %s" % posts['total_found'])
            for match in posts['matches']:
                post_id = match['id']
                thread_id = match['attrs']['thread_id']
                if not thread_id in self.threads:
                    self.threads[thread_id]=[]
                self.threads[thread_id].append(post_id)
                self.count += 1
        if 'matches' in files and files['matches']:
            log.debug("Files: %s" % files['total_found'])
            ids = map(lambda x: x['id'], files['matches'])
            self.files = len(ids)
            log.info("Query start.")
            file_posts = Post.query.join(post_files_table).\
                         filter(post_files_table.c.file_id.in_(ids)).\
                         filter(Post.display_id != None).all()
            log.info("Posts with these files: %s" % len(file_posts))
            for post in file_posts:
                if not post.thread_id in self.threads:
                    self.threads[post.thread_id]=[]
                if not post.id in self.threads[post.thread_id]:
                    self.threads[post.thread_id].append(post.id)
                    self.count += 1
        for thread in self.threads:
            self.threads[thread].sort()
        self.thread_ids = self.threads.keys()
        self.thread_ids.sort(reverse=True)
        #log.info(self.threads)
        self.pages = int(math.ceil(float(len(self.threads))/self.per_page))

    def get_threads(self, page=0, admin=None, visible_posts=None):
        offset = self.per_page * page
        thread_ids = self.thread_ids[offset:offset+self.per_page]
        log.info(thread_ids)
        threads_rows = meta.Session.query(Thread, Post).join((Post,Thread.op_id==Post.post_id)).filter(Thread.id.in_(thread_ids)).order_by(Thread.id.desc()).all()
        threads = []
        for thread, op in threads_rows:
            if thread.board.check_permissions('read', admin):
                posts = Post.query.options(eagerload('files')).filter(Post.id.in_(self.threads[thread.id])).order_by("posts_display_id DESC").all()
                thread.collect_posts(op, posts, limit=len(posts))
                threads.append(thread)
        return threads

    def valid(self):
        return True

    def __repr__(self):
        return "<Search('%s', %s/%s/%s, %s pages)>" % (self.query, self.count, len(self.threads), self.files, self.pages)

class Searches(object):
    settings = None
    searches = []
    client   = None
    def __init__(self, settings):
        self.settings = settings
        self.client = SphinxClient()
        self.client.SetServer(str(settings.sphinx.host), settings.sphinx.port)
        self.client.SetMatchMode(SPH_MATCH_EXTENDED2)
        self.client.SetLimits(0, settings.sphinx.maximum, settings.sphinx.maximum, settings.sphinx.maximum)
        
    def check(self, query):
        return False

    def get(self, search_id):
        if len(self.searches) > search_id and self.searches[search_id].valid():
            return self.searches[search_id]
        else:
            return None

    def new(self, query, board_id=None):
        if board_id:
            self.client.SetFilter('board_id', [board_id])
        posts = self.client.Query(query, str(self.settings.sphinx.index_posts))
        if board_id:
            self.client.ResetFilters()
        files = self.client.Query(query, str(self.settings.sphinx.index_files))
        if posts or files:
            sid = len(self.searches)
            self.searches.append(Search(sid, query, posts, files, self.settings.sphinx.per_page))
            return self.searches[sid]
        else:
            return None
    
