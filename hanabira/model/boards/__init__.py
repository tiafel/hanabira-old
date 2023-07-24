# -*- coding: utf-8 -*-
import datetime, math, cgi, os, random
import pickle
import logging

from sqlalchemy import *
from sqlalchemy.orm import eagerload, relation
from sqlalchemy.ext.declarative import synonym_for
from sqlalchemy.sql import and_, or_, not_, func

from threading import Lock

from pylons.i18n import _, ungettext, N_
from pylons import url, app_globals as g, session

from hanabira.model import meta
from hanabira.model.threads import Thread, DeletedThread
from hanabira.model.posts import Post, DeletedPost
from hanabira.model.files import FileSet
from hanabira.lib.utils import *
from hanabira.lib.contexts import locked
from hanabira.lib.trace import trace_time

log = logging.getLogger(__name__)

class Channel(meta.Declarative):
    __tablename__ = "chans"
    chan_id = Column(Integer, primary_key=True)
    name    = Column(UnicodeText, nullable=False)
    title      = Column(UnicodeText, nullable=False)
    host     = Column(UnicodeText, nullable=False)
    lower_banner = Column(UnicodeText)

    @synonym_for('chan_id')
    @property
    def id(self):
        return self.chan_id
    
    @property
    def upper_banner():
        img = random.choice(meta.upper_banners)
        return '<img href="%s" /><br />'%img
        
    def __repr__(self):
        return "<Channel %s @ %s>"%(self.title.encode('utf-8'), self.name.encode('utf-8'))

class Section(meta.Declarative):
    __tablename__ = "sections"
    section_id = Column(Integer, primary_key=True)
    title      = Column(UnicodeText, nullable=False)
    index      = Column(Integer)
    chan_id   = Column(Integer, ForeignKey("chans.chan_id"), nullable=False, index=True)
    chan       = relation(Channel)

    @synonym_for('section_id')
    @property
    def id(self):
        return self.section_id

    @property
    def channel(self):
        return g.boards.chan_ids[self.chan_id]
    
    def __repr__(self):
        return "<Section(%s)[%s][%s]>" % (str(self.title), self.section_id, self.chan_id)

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title

def default_allowed_ft():
    return ['image']

class Board(meta.Declarative):
    __tablename__ = "boards"
    board_id                 = Column(Integer, primary_key=True)
    section_id               = Column(Integer, ForeignKey("sections.section_id"), nullable=False, index=True)
    section_index            = Column(Integer, nullable=False, index=True)
    post_index               = Column(Integer, nullable=False, default=0)
    thread_index             = Column(Integer, nullable=False, default=0)
    indexing_type            = Column(Unicode(16), nullable=False, default='board-board')
    board                    = Column(Unicode(8), nullable=False, index=True)
    title                    = Column(UnicodeText, nullable=True)
    long_title               = Column(UnicodeText, nullable=True)
    description              = Column(UnicodeText, nullable=True)
    meta_description         = Column(UnicodeText, nullable=True)
    keywords                 = Column(UnicodeText, nullable=True)
    posts                    = Column(Integer, nullable=False, default='0')
    threads                  = Column(Integer, nullable=False, default='0')
    # Permissions
    restrict_read            = Column(Boolean, nullable=False, default=False)
    restrict_new_thread      = Column(Boolean, nullable=False, default=False)
    restrict_new_reply       = Column(Boolean, nullable=False, default=False)
    # Archive
    archive                  = Column(Boolean, nullable=False, default=False)
    archive_days_min         = Column(Integer, nullable=False, default=1)
    archive_days_max         = Column(Integer, nullable=False, default=10)
    archive_pages            = Column(Integer, nullable=False, default=10)
    # Files
    require_thread_file      = Column(Boolean, nullable=False, default=True)
    require_post_file        = Column(Boolean, nullable=False, default=False)
    require_new_file         = Column(Boolean, nullable=False, default=False)
    allow_files              = Column(Boolean, nullable=False, default=True)
    keep_filenames           = Column(Boolean, nullable=False, default=True)
    file_max_size            = Column(Integer, nullable=False, default=2*1024*1024)
    file_min_size            = Column(Integer, nullable=False, default=0)
    file_max_res             = Column(Integer, nullable=False, default=4*1000*1000)
    file_min_res             = Column(Integer, nullable=False, default=0)
    files_max_qty            = Column(Integer, nullable=False, default=5)
    thumbnail_resolution     = Column(Integer, nullable=False, default=200)
    allowed_filetypes        = Column(PickleType(pickler=pickle), nullable=False, default=default_allowed_ft)
    allowed_new_files        = Column(PickleType(pickler=pickle), nullable=True, default=None)
    # Captcha limits
    require_captcha          = Column(Boolean, default=True)    
    threads_per_hour         = Column(Integer, default=2)
    replies_per_hour         = Column(Integer, default=2)
    confirm_bump_age         = Column(Integer, default=7)
    # Options
    default_name             = Column(UnicodeText, nullable=True, default="Анонимус")
    allow_names              = Column(Boolean, default=True)
    remember_name            = Column(Boolean, default=True)
    threads_per_page         = Column(Integer, nullable=False, default=10)
    posts_per_thread         = Column(Integer, nullable=False, default=10)
    bump_limit               = Column(Integer, nullable=False, default=500)
    allow_delete_threads     = Column(Boolean, default=True)
    delete_thread_post_limit = Column(Integer, default=100)
    allow_OP_moderation      = Column(Boolean, nullable=False, default=False)
    allow_custom_restricts   = Column(Boolean, nullable=False, default=False)
    show_geo                 = Column(Boolean, default=False)
    show_city                = Column(Boolean, default=False)
    show_hash                = Column(Boolean, default=False)
    posting_interval         = Column(Integer, nullable=False, default=0)
    threads_interval         = Column(Integer, nullable=False, default=0)
    restrict_trip            = Column(Boolean, nullable=False, default=False)
    ignore_filters           = Column(Boolean, nullable=False, default=False)
    # Relations
    section                  = relation(Section)
    # Mappings
    __mapper_args__ = {'polymorphic_on': indexing_type, 'polymorphic_identity': 'board-board'}
    
    @synonym_for('board_id')
    @property
    def id(self):
        return self.board_id

    def check_permissions(self, type, admin, chan=None):
        restrict_type = 'restrict_'+type
        if self.__getattribute__(restrict_type):
            return admin and admin.has_permission(type, self.board_id)
        else:
            return not chan or self.chan.id == chan.id or (admin and admin.has_permission('boards'))
        
    def check_require_captcha(self):
        if not self.require_captcha:
            return False
        if session.get('admin', None) and session['admin'].has_permission('no_captcha', self.id):
            return False
        if session['captcha'].get_complexity(self.board) > g.settings.captcha.optional_complexity:
            return True
        if not session['enforced_captcha_complexity'] and g.settings.captcha.post_threshold != -1 and g.settings.captcha.post_threshold <= (session.posts_visible):
            return False
        else:
            return True
        
    
    def check_posting_limits(self, post, _post_limits):
        # Non-token restrictions: age/consequtive posting
        if not self.require_captcha:
            return False
        if session.get('admin', None) and session['admin'].has_permission('no_captcha', self.id):
            return False
        
        now = datetime.datetime.now()
        hour_ago = now - datetime.timedelta(hours=1)
        ecc = session['enforced_captcha_complexity']
        if post.op == False and not post.sage and not post.thread.sticky:
            if (now - post.thread.last_hit).days >= self.confirm_bump_age:
                complexity = ecc + g.settings.captcha.bump_penalty
                _post_limits.append([('captcha', _('This thread is too old, please confirm that you are human.')), complexity])
                return True
        if post.op == True:
            qty = Post.query.filter(Post.op == True).filter(Post.session_id == session.id).filter(Post.date >= hour_ago).filter(Post.display_id != None).count()
            if qty >= self.threads_per_hour:
                complexity = ecc + (g.settings.captcha.new_thread_penalty * (qty - self.threads_per_hour + 1))
                _post_limits.append([('captcha', _('You reached new threads limit, please confirm that you are human.')), complexity])
                return True
        if post.op == False:
            posts = Post.query.filter(Post.thread_id == post.thread_id).filter(Post.display_id != None).filter(Post.date >= hour_ago).order_by(Post.display_id.desc()).all()
            consecutive = 0
            while posts:
                ppost = posts.pop(0)
                if ppost.session_id == session.id:
                    consecutive += 1
                else:
                    break
            if consecutive >= self.replies_per_hour:
                complexity = ecc + (g.settings.captcha.reply_penalty * (consecutive - self.replies_per_hour + 1))
                _post_limits.append([('captcha', _('You reached consecutive replies limit, please confirm that you are human.')), complexity])
                return True

    def thread_filters(self, query=None, archive=False, hidden=None, visible_posts=None, see_invisible=False, sticky=None):
        if not query:
            query = Thread.query
        query = query.filter(Thread.board_id == self.id).filter(Thread.display_id != None)
        if not archive is None:
            query = query.filter(Thread.archived == archive)
        if not sticky is None:
            query = query.filter(Thread.sticky == sticky)
        if hidden:
            query = query.filter(Thread.not_in(hidden))
        if not see_invisible:
            if visible_posts:
                visible_threads = visible_posts.get_threads(self.id)
                if visible_threads:
                    query = query.filter(or_(Thread.thread_id.in_(visible_threads), Thread.invisible == False))
                else:
                    query = query.filter(Thread.invisible == False)
            else:
                query = query.filter(Thread.invisible == False)
        return query

    def get_thread_count(self, hidden=None, archive=False, visible_posts=None, see_invisible=False, sticky=None):
        if archive:
            f = self.thread_filters(archive=True, see_invisible=False, sticky=False)
        else:
            f = self.thread_filters(archive=archive, hidden=hidden, visible_posts=visible_posts, see_invisible=see_invisible, sticky=sticky)
        c = f.count()
        return c
    
    def get_pages(self, admin, hidden=None, archive=False, visible_posts=None):
        if self.check_permissions('read', admin):
            see_invisible = (admin and admin.has_permission('see_invisible', self.board_id))
            q = self.get_thread_count(hidden=hidden, archive=archive, visible_posts=visible_posts, see_invisible=see_invisible, sticky=None)
            return int(math.ceil(float(q)/self.threads_per_page))
        else:
            return 0

    def get_thread(self, thread_id, fetch=True, admin=None, visible_posts=None, deleted=False, after=None, get_posts=True):
        if self.check_permissions('read', admin):
            thread = Thread.query.filter(Thread.board_id == self.id).filter(Thread.display_id == thread_id).first()
            view_deleted = admin and admin.has_permission('view_deleted', self.id)
            if not thread and (deleted or view_deleted):
                thread = DeletedThread.query.filter(DeletedThread.board_id == self.id).filter(DeletedThread.display_id == thread_id).first()
            if thread:
                if fetch:
                    thread.fetch_posts(admin, visible_posts, deleted, after, get_posts)
                return thread
            else:
                return None

    def get_thread_simple(self, display_id):
        thread = Thread.query.filter(Thread.board_id == self.id).filter(Thread.display_id == display_id).first()
        return thread
    
    def get_thread_by_id(self, thread_id, admin):
        if self.check_permissions('read', admin):
            thread = Thread.query.filter(Thread.board_id == self.id).filter(Thread.thread_id == thread_id).first()
            if thread:
                thread.op = Post.post_filters(Post.query.filter(Post.post_id == thread.op_id)).first()
                return thread

    def get_post(self, post_id, try_deleted=False):
        post = Post.query.options(eagerload('thread')).join(Thread).filter(Post.display_id == post_id).filter(Thread.board_id == self.board_id).first()
        if not post and try_deleted:
            post = DeletedPost.query.options(eagerload('thread')).join(Thread).filter(DeletedPost.display_id == post_id).filter(Thread.board_id == self.board_id).first()
        return post
        
    def last_bump(self, thread_id=None, display_id=None):
        if display_id: q = Post.query.options(eagerload('thread')).filter(Thread.id == display_id).filter(Thread.board_id == self.id)
        elif thread_id: q = Post.query.filter(Post.thread_id == thread_id)
        else: q = None
        if q: return q.filter(Post.sage == False).filter(Post.invisible == False).order_by(Post.id.desc()).first()

    def get_visible_threads(self, page=0, archive=False, hidden=None):
        offset = self.threads_per_page * page
        threads_query = self.thread_filters(archive=archive, hidden=hidden, sticky=False).order_by(Thread.last_hit.desc())
        threads = threads_query.offset(offset).limit(self.threads_per_page).all()
        return threads

    def get_invisible_threads(self, page=0, archive=False, hidden=None, visible_posts=None):
        offset = self.threads_per_page * page
        see_invisible = False
        threads_query = self.thread_filters(archive=archive, hidden=hidden, visible_posts=visible_posts, sticky=False).order_by(Thread.last_hit.desc())
        threads = threads_query.offset(offset).limit(self.threads_per_page).all()
        invisible_bumps = visible_posts.get_bumps(self.board_id)
        min_date = None
        max_date = None
        for thread in threads:
            thread.last_hit_actual = thread.last_hit
            if not max_date or thread.last_hit > max_date:
                max_date = thread.last_hit
            if not min_date or thread.last_hit < min_date:
                min_date = thread.last_hit
        # User had bumped some threads with invisible posts
        if invisible_bumps and min_date and max_date:
            # We select only bumps which fall into max_date > bump_date > min_date, except if its 1st page
            bumps = {}
            for tid in invisible_bumps:
                d = invisible_bumps[tid]
                if d > min_date and (not page or d < max_date):
                    bumps[tid] = d
            bumped_threads = self.thread_filters(archive=archive, hidden=hidden, visible_posts=visible_posts, see_invisible=see_invisible).\
                                                 filter(Thread.thread_id.in_(list(bumps.keys()))).filter(Thread.last_hit < max_date).\
                                                 order_by(Thread.last_hit.desc()).all()
            for thread in bumped_threads:
                # Invisible bump was last bump
                if bumps[thread.id] >= thread.last_hit:
                    # We do not have this thread in listing already
                    if not thread in threads:
                        thread.last_hit_actual = bumps[thread.id]
                        threads.append(thread)
                    else:
                        thread.last_hit_actual = bumps[thread.id]
            if bumped_threads:
                threads.sort(key=lambda x:x.last_hit_actual, reverse=True)
            if len(threads) > self.threads_per_page:
                    threads = threads[:self.threads_per_page]
        return threads


    def get_all_threads(self, page=0, archive=False, hidden=None):
        offset = self.threads_per_page * page
        threads_query = self.thread_filters(archive=archive, see_invisible=True, hidden=hidden, sticky=False).order_by(Thread.last_bumped.desc())
        threads = threads_query.offset(offset).limit(self.threads_per_page).all()
        return threads
    
    def get_archive_threads(self, page=0):
        offset = self.threads_per_page * page
        threads_query = self.thread_filters(archive=True, see_invisible=False, sticky=False).order_by(Thread.last_bumped.asc())
        threads = threads_query.offset(offset).limit(self.threads_per_page).all()
        if not threads:
            return []
        threads = Thread.populate_threads(threads, self, see_invisible=False,
                                          per_thread=self.posts_per_thread)
        return threads
    
    def get_threads(self, admin, page=0, archive=False, hidden=None, visible_posts=None, see_invisible=False, ignore_sticky=False, get_posts=True, get_ops=True):
        """
        For sake of simplicity, we should divide it into 3 cases:
        1. User is unaffected by premod, and see no invisible posts
        2. User has see_invisible permission
        3. User has some threads affected
        """
        if self.check_permissions('read', admin):
            offset = self.threads_per_page * page
            if not see_invisible is None:
                see_invisible = (admin and admin.has_permission('see_invisible', self.board_id))
            vis_threads = visible_posts and (visible_posts.get_threads(self.board_id) + list(visible_posts.get_board(self.id)['posts'].keys())) 
            if (see_invisible is None and visible_posts is None) or (not see_invisible and not vis_threads):
                threads = self.get_visible_threads(page=page, archive=archive, hidden=hidden)
            elif see_invisible:
                threads = self.get_all_threads(page=page, archive=archive, hidden=hidden)
            else:
                threads = self.get_invisible_threads(page=page, archive=archive, hidden=hidden, visible_posts=visible_posts)

            if not ignore_sticky and not archive and page == 0:
                sticky = self.thread_filters(archive=None, hidden=hidden, sticky=True, see_invisible=True).order_by(Thread.last_hit.desc()).all()
                threads = sticky + threads

            if not threads:
                return []

            if get_posts:
                threads = Thread.populate_threads(threads, self, visible_posts=visible_posts,\
                                                  see_invisible=see_invisible, per_thread=self.posts_per_thread)
            elif get_ops:
                threads = Thread.populate_threads(threads, self, visible_posts=visible_posts,\
                                                  see_invisible=see_invisible, per_thread=self.posts_per_thread, ops_only=True)
            return threads            
        else:
            return []

    def empty_post(self, thread_id=None, fileset=None, password=None, admin=None, ip=None, geoip=None, session_id=None):
        if not password is None and ip and session_id:
            if thread_id:
                thread = Thread.query.filter(Thread.board_id == self.board_id).filter(Thread.display_id == thread_id).first()
            else:
                thread = Thread()
            now = datetime.datetime.now()
            errors = {}
            post = Post()
            critical_errors = []
            if thread:
                if thread.id:
                    if not self.check_permissions('new_reply', admin):
                        log.info('new_reply permission check failed')
                        critical_errors.append(_('%s permission check failed')%'new_reply')
                    if thread.archived:
                        log.info('thread is archived')
                        critical_errors.append(_('Thread %s is archived')%thread_id)
                    if thread.locked and not admin:
                        log.info('thread is locked')
                        critical_errors.append(_('Thread %s is locked')%thread_id)
                    if critical_errors:
                        return critical_errors
                    post.op = False
                else:
                    if not self.check_permissions('new_thread', admin):
                        log.info('new_thread permission check failed')
                        return [_('%s permission check failed')%'new_thread']
                    thread.board_id = self.board_id
                    thread.op_moderation = self.allow_OP_moderation
                    thread.last_hit = now
                    thread.created = now
                    thread.last_modified = now
                    thread.last_bumped = now
                    meta.Session.add(thread)
                    meta.Session.commit()
                    post.op = True
                post.thread_id = thread.id
                post.board_id = self.id
                post.date = now
                post.ip = ipToInt(ip)
                post.geoip = geoip
                post.password = password
                post.session_id = session_id
                if fileset:
                    post.files = fileset.fileset
                    if fileset.errors:
                        errors['file'] = fileset.errors
                post.error = pickle.dumps(errors)
                meta.Session.add(post)
                meta.Session.commit()
                if post.op:
                    thread.op_id = post.id
                    meta.Session.commit()
                post.thread = thread
                return post
            else:
                log.info('Thread %s does not exist' % thread_id)
                return [_("Thread %s does not exist")%thread_id]
        else:
            log.info('empty_post(): not %s is None and %s and %s == False' % (password, ip, session_id))
            return None

    def new_post(self, post_id, session, req, hold=False):
        params = req.POST
        admin = session.get('admin', None)
        password = sanitized_unicode(params.get('password', ''))
        session_id = session.id
        if post_id:
            post = self.get_unfinished_post(post_id)
            if not post:
                log.info('Post %s does not exist' % post_id)
                return None
        else:
            thread_id = int(params.get('thread_id', '0'))
            post = self.empty_post(thread_id=thread_id, password=password, admin=admin, ip=req.ip, geoip=req.country, session_id=session_id)
            if not post:
                log.info("self.empty_post() returned None")
                return None
            if type(post) == list:
                return post

        thread = post.thread
        now = datetime.datetime.now()
        
        # XXX: make errors separate class, with .add_error() method
        errors = {}
        invisible = False
        reason = None
        
        if len(params.get('message', '')) > 60000:
            add_error(errors, 'message', _('Message should not exceed 60000 chars (your is {0} chars)').format(len(params.get('message', ''))))
            message_raw = params.get('message', '')[0:60000]
        else:
            message_raw = params.get('message', '')
        
        trace_time('post.set_data')
        post.set_data(
            name_str=(not session.get_token('forbid_name', board=self, thread=thread) and params.get('name', '') or ''), 
            subject=(not session.get_token('forbid_subj', board=self, thread=thread) and params.get('subject', '') or ''),
            message_raw=message_raw,
            )
        trace_time('post.set_data')        
        
        post.password = password
        session['redirect'] = params.get('goto', 'board')
        if post.password:
            session['password'] = post.password
        post.date = now
        post.sage = thread.autosage or (not post.op and params.get('sage', False))
        if post.sage:
            post.sage = True
        post.ip = ipToInt(req.ip)
        post.geoip = req.country
        post.session_id = session.id
        
        if self.allow_files and not session.get_token('forbid_files', thread=thread, board=self):
            trace_time('post.files')
            fileset = FileSet(post.files, self)
            fileset.add_from_post(params)
            if fileset.errors:
                errors['file'] = fileset.errors
            post.files = fileset.fileset
            post.files_qty = len(fileset.fileset)
            trace_time('post.files')
            
        if not (post.message_raw or post.files):
            add_error(errors, 'message', _('You should either write message or add file'))

        if post.op and self.require_thread_file and not post.files:
            add_error(errors, 'file', _('You have to add at least one file for new thread'))
        if post.op and not (post.message_raw or post.subject):
            add_error(errors, 'subject', _('You should either write subject or message'))
        if not post.op and self.require_post_file and not post.files:
            add_error(errors, 'file', _('You have to add at least one file'))

        #if self.posting_interval and not (admin and admin.has_permission('no_delay', self.id)):
        #    prevpost = Post.query.filter(Post.display_id != None).filter(Post.ip == post.ip).join(Thread).filter(Thread.board_id == self.id).order_by(Post.display_id.desc()).first()
        #    if prevpost:
        #        now = datetime.datetime.now()
        #        td  = now - prevpost.date
        #        if td.seconds < self.posting_interval:
        #            add_error(errors, 'message', _('You have to wait %s more seconds before posting again') % (self.posting_interval - td.seconds))
                  
          
        _post_limits = []
        if self.check_posting_limits(post, _post_limits):
            _post_limit = _post_limits.pop()
            if session['captcha'].check_complexity(self, _post_limit[1]):
                if not session['captcha'].check(self, params, admin):
                    add_error(errors, 'captcha', _('Incorrect captcha'))
                    session['captcha'].new(self.board, complexity=_post_limit[1])
            else:
                add_error(errors, *_post_limit[0])
        elif self.check_require_captcha():
            if not session['captcha'].check(self, params, admin):
                add_error(errors, 'captcha', _('Incorrect captcha'))
        else:
            session['captcha'].new(self.board, complexity=g.settings.captcha.optional_complexity)
        
        trace_time('post.restrictions') 
        post.handle_restrictions(self, errors)
        trace_time('post.restrictions') 
        if not errors:
            session.update_post_count(post, thread)
            
            # XXX: Should be handled by Thread?
            if not (post.sage or post.invisible):
                thread.last_hit = now
            if not post.sage:
                thread.last_bumped = now
            thread.last_modified = now
            trace_time('post.commit')
            self.set_display_id(thread, post)
            self.update_thread(thread)
            trace_time('post.commit')
            if post.post_id in session['posts']:
                del session['posts'][post.post_id]
        else:
            post.error = errors
            meta.Session.commit()
            session['posts'][post.post_id] = self.board
        session.save()
        return post

    def get_unfinished_post(self, post_id):
        post = Post.query.options(eagerload('files')).options((eagerload('thread'))).filter(Post.post_id == post_id).filter(Post.display_id == None).filter(Thread.board_id == self.board_id).first()
        return post

    def update_thread(self, thread):
        thread.update_stats(board=self)
        self.update_self()

    def update_self(self):
        q = list(Thread.query.filter(Thread.board_id == self.board_id).values(func.sum(Thread.posts_count)))
        self.posts = q[0][0]
        meta.Session.merge(self)
        meta.Session.commit()
        
    def set_display_id(self, thread, post):
        with locked(self.index_lock):
            thread_idx, post_idx = list(Board.query.
                                        filter(Board.board_id == self.id).
                                        values(Board.thread_index,
                                               Board.post_index)
                                        )[0]
            
            index = thread_idx + 1
            if not thread.display_id:
                thread.display_id = index
            post.display_id = index
            
            Board.query.filter(Board.board_id == self.id).update(
                dict(thread_index=index, post_index=index),
                synchronize_session=False
            )
            meta.Session.commit()
            self.thread_index = index
            self.post_index = index
        
    def import_thread(self, thread):
        return None

        new_thread = Thread()
        new_thread.import_data(thread, False)
        new_thread.board_id = self.id
        new_thread.display_id = None
        new_thread.imported_from = {'thread_id':thread.display_id, 'board':thread.board.board}
        new_thread.exported_to = None
        meta.Session.add(new_thread)
        meta.Session.commit()
        
        ids = {}
        bname = thread.board.board
        def rewrite_ref(m):
            num = int(m.group(1))
            if num in ids:
                return '>>%s'%ids[num]
            else:
                return '>>%s/%s'%(bname, num)
            
        for post in thread.posts:
            new_post = Post()
            new_post.import_data(post, False)
            for f in post.files:
                new_post.files.append(f)
            new_post.thread_id = new_thread.id
            message = re.sub(r'>>(\d+)', rewrite_ref, post.message_raw)
            if message != post.message_raw:
                new_post.message_raw = message
                parsed_message = g.parser.parse(new_post, new_thread, self)
                new_post.message = parsed_message.message
                new_post.message_short = parsed_message.message_short
            meta.Session.add(new_post)
            self.set_display_id(new_thread, new_post)
            if new_post.op:
                new_thread.op_id = new_post.id
            ids[post.display_id] = new_post.display_id
            
        self.update_thread(new_thread)
        return new_thread
    
    def export_thread(self, thread_id, board):
        return None
        
        thread = Thread.find(thread_id)
        new_board = g.boards.get(board)
        if not thread or not new_board or thread.board_id != self.id or new_board.id == self.id:
            return
        thread.posts = Post.post_filters(thread=thread, see_invisible=True).order_by(Post.display_id.asc()).all()
        new_thread = new_board.import_thread(thread)
        thread.exported_to = {'thread_id':new_thread.display_id, 'board':board}
        thread.imported_from = None
        thread.location = url('thread', **thread.exported_to)
        thread.locked = True
        meta.Session.commit()
        return thread

    def delete_posts(self, threads, password, admin, request=None, session=None):
        deleted = 0
        for thread_id in threads:
            thread = self.get_thread_by_id(thread_id, admin)
            if thread:
                log.debug("Delete from thread %s:%s %s" % (thread.thread_id, thread.display_id, threads[thread_id]))
                if thread.archived and not (admin and admin.has_permission('manage_archive')):
                    return _("Can't delete posts from archive.")
                res = thread.delete_posts(board=self, posts=threads[thread_id], password=password, admin=admin, request=request, session=session)
                if res == True: # deleted something
                    deleted += 1
        if not deleted:
            return _("Wrong delete password.")
        else:
            self.update_self()

    def stats_posts(self):
        idx = meta.Session.query(Board.post_index).filter(Board.board_id == self.id).first()[0]
        return idx

    def stats_posts_diff(self, stats):
        return self.post_index - stats

    def archive_threads(self):
        removed = 0
        if not self.archive:
            return removed

        threads_max = self.archive_pages * self.threads_per_page
        count = self.get_thread_count(archive=False)
        if count <= threads_max:
            return removed

        to_remove = count - threads_max
        log.info("Should archive %s threads" % (to_remove))
        now = datetime.datetime.now()
        date_min = now - datetime.timedelta(days=self.archive_days_min)
        threads = self.thread_filters(see_invisible=True).filter(Thread.last_hit < date_min).filter(Thread.invisible==True).all()
        log.info('Found %s invisible threads updated before %s'%(len(threads), date_min))
        inv_del = 0
        inv_arch = 0
        for thread in threads:
            if thread.posts_count > 20:
                thread.archive(True)
                inv_arch += 1
            else:
                thread.delete_self()
                inv_del += 1
            removed += 1
            to_remove -= 1
        log.info("Deleted {0} and archived {1} invisible threads, need to remove {2} more.".format(inv_del, inv_arch, to_remove))
        
        threads = self.thread_filters().filter(Thread.last_hit < date_min).filter(Thread.sticky == False).order_by(Thread.last_hit).all()
        log.info("Found %s threads updated before %s" % (len(threads), date_min))
        while to_remove and len(threads):
            thread = threads.pop(0)
            days = (now - thread.last_hit).days
            log.info("Thread %s, posts %s, last_hit %s (%s days)" % (thread.display_id, thread.posts_count, thread.last_hit, days))
            min_days = self.calculate_archive_min_days(thread)
            log.info("Minimum days before archive: %s" % min_days)
            if days >= min_days:
                log.info("Archived")
                thread.archive(True)
                removed += 1
                to_remove -= 1
        if removed:
            meta.Session.commit()
        return removed

    def calculate_archive_min_days(self, thread):
        return int(round(math.log(thread.posts_count, self.bump_limit)
                         * (self.archive_days_max - self.archive_days_min)
                         + self.archive_days_min))

    # Exports
    def set_context_permissions(self, context, admin):
        if admin:
            context.can_view_ip = admin.has_permission('view_ip', self.id)
            context.can_view_files = admin.has_permission('files', self.id)
            context.can_see_invisible = admin.has_permission('see_invisible', self.id)
            context.can_delete_posts = admin.has_permission('delete_posts', self.id)
            context.can_edit_posts = admin.has_permission('edit_posts', self.id)
        else:
            context.can_view_ip = False
            context.can_view_files = False
            context.can_see_invisible = False
            context.can_delete_posts = False
            context.can_edit_posts = False

    def get_capabilities(self):
        return {}
        
    def __repr__(self):
        return "<Board(/%s/, %s, %s)>" % (self.board, self.indexing_type, self.post_index)

class KarehaBoard(Board):
    __mapper_args__ = {'polymorphic_identity': 'time-thread'}

class Boards(object):
    """
    Collection of Board and associated Section objects
    """
    sections = []
    boards = {}
    board_ids = {}
    chans = {}
    chan_ids = {}
    banners = None
    settings = None
    fs = None
    def __init__(self, settings, fs):
        self.settings = settings
        self.fs = fs
        self.load()
        
    def load(self):
        while self.sections:
            self.sections.pop()
        self.boards = {}
        self.board_ids = {}
        self.banners = {}
        self.chan_banners = {}
        sections = Section.query.order_by(Section.index.asc()).all()
        for chan in Channel.query.all():
            self.chans[chan.name] = self.chan_ids[chan.id] = chan
            chan.sections = Section.query.filter(Section.chan_id == chan.id).order_by(Section.index.asc()).all()
            chan.boards = {}
            chan.board_ids = {}
            for section in chan.sections:
                section.boards = Board.query.options(eagerload('section')).filter(Board.section_id == section.section_id).order_by(Board.section_index.asc()).all()
                for board in section.boards:
                    chan.boards[board.board] = chan.board_ids[board.id] = self.boards[board.board] = self.board_ids[board.id] = board
                    board.chan = chan
                    board.allowed_filetypes.append('video')
                    board.allowed_filetypes = list(set(board.allowed_filetypes))
                    board.index_lock = Lock()
                    bp = 'images/banners/{0.board}'.format(board)
                    if os.path.exists(self.fs.local(bp)):
                        banners = [self.fs.web(os.path.join(bp, x)) for x in os.listdir(self.fs.local(bp))]
                        self.banners[board.board] = banners
                        self.chan_banners.setdefault(chan.id, {})
                        self.chan_banners[chan.id][board.board] = banners
                self.sections.append(section)
                
    def get(self, board=None, host=None, id=None):
        if id:
            res = self.board_ids.get(id)
        elif host:
            chan = None
            for name in self.chans:
                if host in name or name in host:
                    chan = self.chans.get(name)
            res = chan or self.chan_ids[1]
            if board:
                res = res.boards.get(board)
        elif board:
            res = self.boards.get(board)
        return res

    def get_banner(self, board, session):
        bs = session.get('banners', None)
        if bs == 'different':
            if board.chan.id in self.chan_banners:
                bname = random.choice(list(self.chan_banners[board.chan.id].keys()))
                burl  = random.choice(self.chan_banners[board.chan.id][bname])
                return (bname, burl)
            else:
                return None
        elif bs == 'same':
            if board.board in self.banners:
                bname = board.board
                burl  = random.choice(self.banners[bname])
                return (bname, burl)
            else:
                return None
        else:
            return None
