# -*- coding: utf-8 -*-
import datetime, time
import logging
import pickle

from sqlalchemy import *
from sqlalchemy.orm import eagerload, relation
from sqlalchemy.sql import and_, or_, not_, union
from sqlalchemy.dialects.mysql.base import BIGINT as MSBigInteger
from sqlalchemy.ext.declarative import synonym_for

from pylons.i18n import _, ungettext, N_
from pylons import app_globals as g, session, request, tmpl_context as c

from hanabira.lib.utils import *
from hanabira.lib.visible import ensure_visible
from hanabira.lib.decorators import getargspec, make_args_for_spec
from hanabira.view.error import *

from hanabira.model import meta
from hanabira.model.files import File
from hanabira.model.logs import UserPostDeleteLog, OPPostDeleteLog, UserThreadDeleteLog, ModPostDeleteLog, ModThreadDeleteLog

log = logging.getLogger(__name__)
Post = None
DeletedPost = None

def temp_file(filename):
    return str(g.settings.path.temp) + filename

def static_local(filename):
    return str("%s%s" % (g.settings.path.static, filename))

class Thread(meta.Declarative):
    __tablename__ = 'threads'
    omitted = 0
    deleted = False
    posts   = None
    
    thread_id     = Column(Integer, primary_key=True)
    board_id      = Column(Integer, ForeignKey('boards.board_id'), nullable=False, index=True)
    display_id    = Column(Integer, nullable=True, index=True)
    op_id         = Column(Integer, nullable=True)
    last_hit      = Column(DateTime, nullable=False, index=True)
    created       = Column(DateTime)
    last_modified = Column(DateTime, nullable=False, index=True)
    last_bumped   = Column(DateTime, nullable=False, index=True)
    posts_count   = Column(Integer, nullable=False, default=0)
    files_count   = Column(Integer, nullable=False, default=0)
    posts_index   = Column(Integer, nullable=False, default=0)
    archived      = Column(Boolean, default=False, index=True)
    autosage      = Column(Boolean, default=False)
    invisible     = Column(Boolean, default=False)
    locked        = Column(Boolean, default=False)
    sticky        = Column(Boolean, default=False)
    censor_lim    = Column(Boolean, default=False)
    censor_full   = Column(Boolean, default=False)
    op_moderation = Column(Boolean, default=False)
    op_deleted    = Column(Integer, default=0)
    total_deleted = Column(Integer, default=0)
    require_files = Column(Boolean, default=False)
    allow_files   = Column(Boolean, default=True)
    title         = Column(UnicodeText, nullable=False, default='')
 
    @synonym_for('thread_id')
    @property
    def id(self):
        return self.thread_id
    
    @classmethod
    def get(cls, thread_id, deleted=None):
        res = cls.query.filter(cls.id == thread_id).first()
        if not res and deleted:
            res = DeletedThread.query.filter(DeletedThread.id == thread_id).first()
        return res    

    def delete_posts(self, board, posts, password, admin, request, session):
        if self.display_id in posts:
            # Attempt to delete thread
            if board.allow_delete_threads and self.posts_count < board.delete_thread_post_limit:
                if password and self.op.password == password:
                    UserThreadDeleteLog(ipToInt(request.ip), session.id, self)
                    self.delete_self(deleter='author')
                    return True
            if admin and admin.has_permission('delete_threads', board.board_id):
                ModThreadDeleteLog(ipToInt(request.ip), session.id, admin, self, "")
                self.delete_self(deleter='mod')
                return True
            else:
                return False
        else:
            deleted = 0
            for post_id in posts:
                post = Post.query.filter(Post.thread_id == self.thread_id).filter(Post.display_id == post_id).first()
                if post:
                    if password and post.password == password:
                        UserPostDeleteLog(ipToInt(request.ip), session.id, post)
                        post.delete_self(deleter='author')
                        deleted += 1
                        self.total_deleted += 1
                    elif admin and admin.has_permission('delete_posts', board.board_id):
                        ModPostDeleteLog(ipToInt(request.ip), session.id, admin, post, "")
                        post.delete_self(deleter='mod')
                        deleted += 1
                        self.total_deleted += 1
                    elif self.op_moderation and password and self.op.password == password:
                        OPPostDeleteLog(ipToInt(request.ip), session.id, post)
                        post.delete_self(deleter='op')
                        self.op_deleted += 1
                        self.total_deleted += 1
                        deleted += 1
                    else:
                        log.debug("Delete post, '%s' eq '%s' = %s" % (password, post.password, post.password == password))
            if deleted:
                self.update_stats()
                self.last_hit = self.last_bump().date                
                meta.Session.commit()
                return True
            else:
                return False


    @classmethod
    def populate_threads(cls, threads, board, visible_posts=None, see_invisible=None, per_thread=10, ops_only=False):
        pq = []
        tbyid = {}
        vis_board = visible_posts and visible_posts.get_board(board.id)
        vis_threads = vis_board and (vis_board['threads'] + list(vis_board['posts'].keys()))
        op_ids = []
        for thread in threads:
            if not ops_only:
                if see_invisible:
                    where = "thread_id = {0} and display_id is not null".format(thread.id)
                elif not vis_threads:
                    where = "invisible=0 and thread_id = {0} and display_id is not null".format(thread.id)
                else:
                    vposts = [str(x) for x in list(vis_board['posts'].get(thread.id, {}).keys())]
                    if vposts:
                        where = "(post_id in ({1}) or invisible=0) and thread_id = {0} and display_id is not null".format(thread.id, ",".join(vposts))
                    else:
                        where = "invisible=0 and thread_id = {0} and display_id is not null".format(thread.id)
                pq.append("({0})".format(select([Post.post_id]).where(where).order_by(Post.display_id.desc()).limit(10)))
            tbyid[thread.id] = thread
            thread.posts = []
            op_ids.append(thread.op_id)
            if thread.posts_count >= (per_thread + 1):
                thread.omitted = thread.posts_count - (per_thread + 1)
            else:
                thread.omitted = None
            thread.omitted_files = thread.files_count
        if not ops_only:
            post_ids = [x[0] for x in list(meta.Session.execute(" UNION ".join(pq), {'param_1':10}))]
        if not ops_only:
            posts = Post.query.filter(or_(\
                Post.post_id.in_(post_ids),
                Post.post_id.in_(op_ids))).order_by(Post.display_id.asc()).all()
        else:
            posts = Post.query.filter(Post.post_id.in_(op_ids)).order_by(Post.display_id.asc()).all()
        for post in posts:
            thread = tbyid[post.thread_id]
            thread.posts.append(post)
            if post.op:
                thread.op = post
            if post.invisible:
                if not thread.omitted is None:
                    thread.omitted += 1
            if post.files_qty:
                thread.omitted_files -= post.files_qty
        return threads
    
    def last_bump(self):
        return Post.query.filter(Post.thread_id == self.id).filter(Post.sage == False).filter(Post.invisible == False).order_by(Post.id.desc()).first()
    
    def last_post(self, visible_posts=None, see_invisible=False):
        return Post.post_filters(Post.query, visible_posts=visible_posts, see_invisible=see_invisible, thread=self).order_by(Post.id.desc()).first()
        
    def count_posts(self, visible_posts=None, see_invisible=False):
        return Post.post_filters(Post.query, self, visible_posts=visible_posts, see_invisible=see_invisible).count()

    def new_posts(self, visible_posts=None, see_invisible=False, since_date=None):
        posts = Post.post_filters(Post.query, self, visible_posts=visible_posts, see_invisible=see_invisible)
        if since_date:
            posts = posts.filter(Post.date > since_date)
        return posts.all()
        
                        
    def delete_self(self, deleter='author'):
        posts = Post.query.filter(Post.thread_id == self.thread_id).all()
        posts_deleter = deleter == 'mod' and 'mod' or 'op'
        for post in posts:
            post.delete_self(deleter=posts_deleter)
        DeletedThread(self, deleter=deleter)
        self.deleted = 1
        
    def fetch_posts(self, admin=None, visible_posts=None, deleted=False, after=None, get_posts=True):
        if get_posts:
            view_deleted = admin and admin.has_permission('view_deleted', self.board_id)
            if deleted or self.deleted:
                pcls = DeletedPost
                if view_deleted:
                    dt = ['author', 'op', 'mod']
                else:
                    dt = ['op']                    
            else:
                pcls = Post
                dt = []
            if visible_posts:
                q = pcls.post_filters(thread=self, visible_posts=visible_posts.get_posts(self),
                                      see_invisible=(admin and admin.has_permission('see_invisible', self.board_id))
                                      )
            else:
                q = pcls.post_filters(thread=self)

            if dt:
                q = q.filter(pcls.deleter.in_(dt))
            if after:
                q = q.filter(pcls.display_id > after)
            posts = q.order_by(pcls.display_id.asc()).all()
            self.posts = posts
        op = Post.query.options(eagerload('files')).filter(Post.post_id == self.op_id).first()
        self.op = op        
        
    def collect_posts(self, op, posts, limit=1):
        if not op in posts:
            posts.append(op)
            self.omitted = self.posts_count - limit
            self.omitted_files = self.files_count
            for post in posts:
                if post.invisible: 
                    self.omitted += 1
                elif post.files_qty:
                    self.omitted_files -= 1
        self.posts = posts[::-1]

    def set_title(thread, op):
        if op.subject:
            thread.title = op.subject
        elif op.message_raw:
            ms = re.sub('[*_%`]', '', op.message_raw.split('\n', 1)[0])
            m = re.search(r'(\S+\s+){0,7}\S+', ms)
            if m:
                m = m.group(0)
                if m != ms: m += '…'
                thread.title = m
                
    def update_stats(thread, board=None, post=None, user=None, commit=False):
        if post and not (post.sage or post.invisible):
            thread.last_hit = request.now
        if post and not post.sage:
            thread.last_bumped = request.now
        thread.last_modified = request.now
        thread.posts_count = thread.count_posts()
        thread.files_count = Post.post_filters(Post.query.filter(Post.files_qty > 0), thread).count()
        if board and board.bump_limit and thread.posts_count >= board.bump_limit:
            thread.autosage = True
        if commit:
            meta.Session.commit()
                
    def update(thread, board=None):
        log.info("thread.update() is deprecated")
        thread.posts_count = thread.count_posts()
        thread.files_count = Post.post_filters(Post.query.filter(Post.files_qty > 0), thread).count()
        
        if board and board.bump_limit and thread.posts_count >= board.bump_limit:
            thread.autosage = True
            
    def clean_invisible(self):
        posts = Post.query.filter(Post.thread_id == self.id).filter(Post.invisible == True).all()
        for post in posts:
            post.delete_self()
    
    def bump(self):
        now = datetime.datetime.now()
        self.last_bumped = now
        self.last_hit = now
        self.last_modified = now        
            
    def archive(self, a=True):
        self.archived = a
        if a:
            self.bump()
            self.clean_invisible()
            
    def is_censored(self, user):
        if not self.censor_full and not self.censor_lim:
            return False
        if not request.country in ['RU', 'NA']:
            return False
        if user.admin:
            return False
        if self.censor_lim and user.posts_visible >= 1:
            return False
        return True
                  
    @property
    def board(self):
        return g.boards.board_ids[self.board_id]

    @classmethod
    def not_in(self, hidden):
        return not_(self.display_id.in_(hidden))

    # Exports
    def get_board(self):
        return g.boards.get(id=self.board_id)
    
    @classmethod
    def fetcher(cls, func):
        spec = getargspec(func)
        def _decorator(self, **kw):
            thread = board = None
            if 'thread_id' in kw:
                thread = cls.get(kw.get('thread_id'), deleted=True)
                if thread:
                    board = g.boards.get(id=thread.board_id)
            elif 'board' in kw:
                board = g.boards.get(kw.get('board'))
                if board:
                    if 'display_id' in kw:
                        thread = board.get_thread_simple(kw.get('display_id'))
            if not board or not thread:
                return error_element_not_found
            if not board.check_permissions('read', c.admin, c.channel):
                return error_board_read_not_allowed
            kw['board'] = board
            kw['thread'] = thread
            args = make_args_for_spec(spec, kw)
            return func(self, **args)    
        return _decorator
            
    
    def export_dict(self, admin=None):
        board = self.get_board()
        see_invisible = admin and admin.has_permission('see_invisible', board.board_id)
        r = {'thread_id':self.thread_id, 'display_id':self.display_id, 'archived':self.archived, 'autosage':self.autosage,
             'title':self.title, 'last_hit':str(self.last_hit), 'last_modified':str(self.last_modified),
             'posts_count':self.posts_count, 'files_count':self.files_count}
        
        if self.posts:
            posts = []
            for post in self.posts:
                posts.append(post.export_dict(see_invisible=see_invisible))
            r['posts'] = posts
        if see_invisible:
            r['invisible'] = self.invisible
        return r

class DeletedThread(Thread):
    __tablename__ = "deleted_threads"
    __mapper_args__ = {'concrete':True}
    
    deleted = True
    posts   = None
    
    thread_id     = Column(Integer, primary_key=True)
    board_id      = Column(Integer, ForeignKey('boards.board_id'), nullable=False, index=True)
    display_id    = Column(Integer, nullable=True, index=True)
    op_id         = Column(Integer, nullable=True)
    last_hit      = Column(DateTime, nullable=False, index=True)
    created       = Column(DateTime)
    last_modified = Column(DateTime, nullable=False, index=True)
    last_bumped   = Column(DateTime, nullable=False, index=True)
    posts_count   = Column(Integer, nullable=False, default=0)
    files_count   = Column(Integer, nullable=False, default=0)
    posts_index   = Column(Integer, nullable=False, default=0)
    archived      = Column(Boolean, default=False, index=True)
    autosage      = Column(Boolean, default=False)
    invisible     = Column(Boolean, default=False)
    locked        = Column(Boolean, default=False)
    sticky        = Column(Boolean, default=False)
    op_moderation = Column(Boolean, default=False)
    censor_lim    = Column(Boolean, default=False)
    censor_full   = Column(Boolean, default=False)
    op_deleted    = Column(Integer, default=0)
    total_deleted = Column(Integer, default=0)
    require_files = Column(Boolean, default=False)
    allow_files   = Column(Boolean, default=True)
    title           = Column(UnicodeText, nullable=False, default='') 

    deleter       = Column(Enum('author', 'mod'), default='author')
    deletion_time = Column(DateTime, default=datetime.datetime.now)

    @synonym_for('thread_id')
    @property
    def id(self):
        return self.thread_id
    
    def __init__(self, thread, deleter):
        self.import_data(thread)

        self.deleter = deleter
            
        meta.Session.delete(thread)
        meta.Session.add(self)
        meta.Session.commit()

    def revive(self):
        thread = Thread()
        thread.import_data(self)
        posts = DeletedPost.query.filter(DeletedPost.thread_id == self.id).all()
        meta.Session.delete(self)
        meta.Session.add(thread)
        meta.Session.commit() 
        for post in posts:
            post.revive()
        return thread
