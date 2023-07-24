# -*- coding: utf-8 -*-
from pylons import tmpl_context as c
from hanabira.model.gorm import *

from hanabira.model import threads
from hanabira.model.files import File
from hanabira.model.threads import Thread, DeletedThread
from hanabira.model.logs import AutoPostInvisible
from hanabira.model.restrictions import format_restrictions_reason
from hanabira.model.warnings import format_reasons_short, format_token_public
from hanabira.lib.utils import sanitized_unicode, ipToInt, add_error
from hanabira.lib.visible import VisiblePosts, ensure_visible
from hanabira.lib.decorators import getargspec, make_args_for_spec
from hanabira.view.error import *

import logging
log = logging.getLogger(__name__)

post_files_table = Table("post_files", meta.metadata,
                         Column("post_id", Integer, ForeignKey('posts.post_id'), index=True),
                         Column("file_id", Integer, ForeignKey('files.file_id'), index=True),
                         )

class PostReference(meta.Declarative):
    __tablename__ = 'post_references'
    reference_id = Column(Integer, primary_key=True)
    source_id = Column(Integer, index=True)
    target_id = Column(Integer, ForeignKey('posts.post_id'), index=True)

    def __init__(self, source_id, target_id):
        self.source_id = source_id
        self.target_id = target_id
        meta.Session.add(self)
        
class PostRevision(meta.Declarative):
    __tablename__ = "post_revisions"
    revision_id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.post_id'), index=True)
    date = Column(DateTime)
    name = Column(UnicodeText)
    subject = Column(UnicodeText)
    message_raw = Column(UnicodeText)
    message_html = Column(UnicodeText)
    reason = Column(UnicodeText)
    changed_by = Column(Enum(*['author', 'mod', 'anonymous']))
    admin_id = Column(Integer)
    
    index = None
    diff = None
    
    def __init__(self, post, date=None, 
                 changed_by="author", admin_id=None, reason=""):
        self.post_id = post.id
        self.name = post.name
        self.subject = post.subject
        self.message_raw = post.message_raw
        self.message_html = post.message
        self.date = date
        self.changed_by = changed_by
        self.admin_id = admin_id
        self.reason = reason
        meta.Session.add(self)
        
    def __repr__(self):
        return "<PostRevision({0.revision_id}, post_id={0.post_id})>".format(self)
    
        
class Post(meta.Declarative):
    __tablename__ = "posts"
    deleted = False
    
    post_id       = Column(Integer, primary_key=True)
    thread_id     = Column(Integer, ForeignKey('threads.thread_id'), nullable=False, index=True)
    board_id      = Column(Integer, nullable=False, index=True)    
    display_id    = Column(Integer, nullable=True, index=True)
    message       = Column(UnicodeText, nullable=True)
    message_short = Column(UnicodeText, nullable=True)
    message_raw   = Column(UnicodeText, nullable=True)
    invisible     = Column(Boolean, default=False)
    sage          = Column(Boolean, nullable=True)
    op            = Column(Boolean, default=False)
    date          = Column(DateTime, nullable=False, index=True)
    last_modified = Column(DateTime, nullable=True)
    session_id    = Column(String(64), nullable=False)
    #session_id    = Column(BIGINT, ForeignKey('sessions.session_id'),
    #                       nullable=False, index=True)    
    password      = Column(Unicode(32), nullable=True)
    subject       = Column(UnicodeText, nullable=True) # Should be removed
    name          = Column(UnicodeText, nullable=True)
    tripcode      = Column(UnicodeText, nullable=True)
    error         = Column(PickleType(pickler=pickle), nullable=True) # Do not load by default
    reference_count = Column(Integer, default=0)    
    inv_reason    = Column(PickleType(pickler=pickle), nullable=True) # Should be removed (reasons go into modqueue)
    ip            = Column(BIGINT, ForeignKey('ips.ip'), nullable=True, index=True)
    geoip         = Column(String(2), nullable=False, default='NA')
    files_qty     = Column(Integer, nullable=False, default=0)
    files         = relation(File, secondary=post_files_table, backref='posts', lazy=False)
    thread        = relation(Thread)
    #session       = relation(UserSession, lazy=True)
    
    _thread_cached = None
    
    @synonym_for('post_id')
    @property
    def id(self):
        return self.post_id

    @classmethod
    def get(cls, post_id=None, deleted=None):
        if post_id:
            res = cls.query.options(eagerload('thread')).filter(cls.id == post_id).first()
            if not res and deleted:
                res = DeletedPost.query.options(eagerload('thread')).filter(DeletedPost.id == post_id).first()
            return res
        
    @classmethod
    def get_unfinished(cls, post_id):
        post = Post.query.options(eagerload('files')).options((eagerload('thread'))).filter(Post.post_id == post_id).filter(Post.display_id == None).first()
        return post
    
    def get_revisions(self):
        return PostRevision.query.filter(PostRevision.post_id == self.id).\
               order_by(PostRevision.date.asc()).all()
    
    @classmethod    
    def post_filters(cls, query=None, thread=None, hidden=None, visible_posts=None, see_invisible=False):
        if not query:
            query = cls.query.options(eagerload('files'))
        query = query.filter(cls.display_id != None)
        if thread:
            query = query.filter(cls.thread_id == thread.id)
        if hidden:
            query = query.filter(not_(cls.post_id.in_(hidden)))
        if not see_invisible:
            if visible_posts:
                query = query.filter(or_(cls.post_id.in_(visible_posts), cls.invisible == False))
            else:
                query = query.filter(cls.invisible == False)
        return query

    def delete_self(self, deleter='author'):
        """
        
        .. todo: Update sessions handling once sessions are implemented via DB
          
        """
        try:
            if session._object_stack():
                # Increase deleted counter in the session:
                if self.session_id == session.id:
                    post_session = session
                else:
                    post_session = g.sessions.load_by_id(self.session_id)
                post_session.update_post_count(self, self.thread, 'delete')
        except Exception as e:
            pass
        
        # Don't touch files for now, should be fixed later
        return DeletedPost(self, deleter=deleter)
        #dp = DeletedPost(self)
        #meta.Session.add(dp)
        #meta.Session.delete(self)
    
    def fix_board_id(self):
        self.board_id = self.thread.board_id
        
    def set_data(self, name_str, subject, message_raw):
        if not self.board_id:
            self.fix_board_id()
            
        board = g.boards.get(id=self.board_id)
        name_str = sanitized_unicode(name_str).replace(u'#', u'!').strip()

        if not name_str or not board.allow_names:
            name_str = board.default_name
            
        name_arr = name_str.split('!')
        
        name = name_arr[0]
        if len(name) > 32:
            name = name[0:32]
        self.name = name
        
        tripcode = u'!'.join(name_arr[1:])
        if tripcode:
            tripcode = u'!' + tripcode
        self.tripcode = tripcode

        self.message_raw = sanitized_unicode(message_raw)
        parsed_message = g.parser.parse(self, self.thread, board)
        self.message = parsed_message.message
        self.message_short = parsed_message.message_short
        self.references = parsed_message.reflinks        
        
        ## XXX:
        # Disable title? 

        self.subject = sanitized_unicode(subject)
        if len(self.subject) > 64:
            self.subject = self.subject[0:64]
        if self.op:                
            self.thread.set_title(self)
        
    def add_revision(self, name, subject, message_raw, reason, admin, commit=True):
        revisions = self.get_revisions()
        if not revisions:
            PostRevision(self, changed_by="author", date=self.date)
        self.set_data(name_str=name, subject=subject, message_raw=message_raw)
        self.last_modified = request.now
        self.thread.last_modified = request.now
        PostRevision(self, date=request.now,
                     changed_by="mod", admin_id=admin.id, reason=reason)
        if commit:
            meta.Session.commit()

    def __repr__(self):
        return "<Post(%s, %s)>" % (self.display_id, self.files)
        
    def session(self, session):
        return g.sessions.load_by_id(self.session_id)
    
    def showable(self, session, board):
        if self.deleted:
            if (session.get_token('view_deleted', board_id=board.id) or
                self.session_id == session.id):
                return True
            else:
                return False
        elif self.invisible:
            see_invisible = session.get_token('see_invisible', board_id=board.id)
            return see_invisible or ensure_visible(session).has_post(self, board)
        else:
            return True

    def export_dict(self, see_invisible=False):
        r = {'post_id':self.post_id, 'display_id':self.display_id, 'subject':self.subject, 'name':self.name,\
             'message':self.message_raw, 'date':str(self.date),\
             'op':self.op, 'files':list(map(lambda x:x.export_dict(), self.files))}
        if see_invisible:
            r['invisible'] = self.invisible
            r['inv_reason'] = self.inv_reason
            r['sage'] = self.sage
        return r

    # XXX: Do something with Thread/DeletedThread dichotomy!
    def get_thread(self):
        thread = self.thread
        if not thread:
            thread = Thread.query.get(self.thread_id)
        if not thread:
            thread = DeletedThread.query.get(self.thread_id)
        return thread
    
    @property
    def _thread(self):
        if not self._thread_cached:
            self._thread_cached = self.get_thread()
        return self._thread_cached
            
    def hide(post, sess=None, reason=['API']):
        changed = False
        thread = post.thread
        visible_posts = ensure_visible(sess)
        post.inv_reason = reason
        if post.op:
            if not thread.invisible:
                changed = True
                thread.invisible = True
                if sess:
                    visible_posts.add_thread(thread)
        else: 
            if not post.invisible:
                changed = True
                post.invisible = True
                if sess:
                    visible_posts.add_post(post, thread)
        if changed and sess: 
            thread.update_stats()
            if 'API' in reason and (post.op or not thread.invisible):
                sess.posts_visible -= 1
            sess.save()
        return changed
            
    def show(post, sess=None, bump=False):
        changed = False
        thread = post.thread
        visible_posts = ensure_visible(sess)
        post.inv_reason = None
        now = datetime.datetime.now()
        if post.op:
            if thread.invisible:
                changed = True
                thread.invisible = False
                if sess:
                    visible_posts.remove_thread(thread)
        else: 
            if post.invisible:
                changed = True 
                post.invisible = False
                if bump:
                    brd = g.boards.get(id=thread.board_id)
                    post.date = now
                    # Causes DB sync
                    brd.set_display_id(thread, post)
                if not post.sage and post.date > thread.last_hit:
                    thread.last_hit = post.date
                    if bump:
                        thread.last_modified = now
                        thread.last_bumped = now
                if sess:
                    visible_posts.remove_post(post, thread)
        if changed and sess: 
            if post.op or not thread.invisible:
                sess.posts_visible += 1
            thread.update_stats()
            sess.save()
        return changed
    
    @classmethod
    def fetcher(cls, func):
        spec = getargspec(func)
        def _decorator(self, **kw):
            post = thread = board = None
            if 'post_id' in kw:
                post = cls.get(kw.get('post_id'), deleted=True)
                if post:
                    thread = post.get_thread()
                    board = g.boards.get(id=thread.board_id)
            elif 'board' in kw:
                board = g.boards.get(kw.get('board'))
                if board:
                    if 'display_id' in kw:
                        post = board.get_post(kw.get('display_id'), try_deleted=True)
                        if post:
                            thread = post.thread
            if post and post.deleted and not (session.get_token('view_deleted') or post.session_id == session.id):
                return error_element_not_found                
            if not post or not board or not thread:
                return error_element_not_found
            if not board.check_permissions('read', session.admin, c.channel):
                return error_board_read_not_allowed
            kw['board'] = board
            kw['post'] = post
            kw['thread'] = thread
            args = make_args_for_spec(spec, kw)
            return func(self, **args)    
        return _decorator

   
    def add_references(self, references):
        # Get list of existing references
        current_refs = PostReference.query.\
                       filter(PostReference.source_id == self.id).all()
        current_refs = set(map(lambda x: x.target_id, current_refs))

        for ref_post in references:
            if not ref_post.id in current_refs:
                PostReference(self.id, ref_post.id)
                ref_post.reference_count += 1

    def load_references(self):
        """
        Load references along with thread and board info
        """
        q = (Post.query.
             join((PostReference, PostReference.source_id == Post.post_id)).
             filter(PostReference.target_id==self.id).
             options(eagerload(Post.thread))
             #.options(lazyload(Post.files))
             )
        return q.all()

    
    def handle_restrictions(self, board, errors):
        # If 'readonly' - forbid to post
        # Handle warns and invisibles by adding to queue

        effects = g.restrictions.check_post(self)
        
        if 'readonly' in effects:
            add_error(errors, 'message', _('You are not allowed'
                                           'to post in this thread'))
            return None
        
        thread = self.thread
        reason = []
        invisible = False
        
        forbid_post = session.get_token('forbid_post', thread=thread, board=board)
        if forbid_post:
            add_error(errors, 'message', format_token_public(forbid_post))
            return None

        for p in self.references.values():
            if p and (p.invisible or (p.thread.invisible and (p.thread.id != thread.id))):
                invisible = True
                reason.append('References to %s'%(p.invisible and 'post' or 'thread'))
                
        if 'premod' in effects:
            invisible = True
            reason.extend(format_restrictions_reason(effects['premod']))
        
        premod_tokens = session.get_token('premod', thread=thread, board=board)
        if premod_tokens:
            invisible = True
            reason.extend([format_reasons_short(tokens=premod_tokens)])
            
        if not invisible and self.op and session.posts_visible < 1:
            invisible = True
            reason.extend(['Thread with no visible posts'])
        
        if (invisible and
            not session.get_token(['no_restrictions', 'bypass_premod'], 
                                  board=board, thread=thread)
            ):
            self.hide(session, reason)
            AutoPostInvisible(ipToInt(request.ip), session.id, self, 0, u", ".join(reason))

deleted_post_files_table = Table("deleted_post_files", meta.metadata,
                                 Column("post_id", Integer, ForeignKey('deleted_posts.post_id'), index=True),
                                 Column("file_id", Integer, ForeignKey('files.file_id'), index=True),
                                 )

class DeletedPost(Post):
    __tablename__ = "deleted_posts"
    __mapper_args__ = {'concrete':True}
    
    post_id       = Column(Integer, primary_key=True)
    thread_id     = Column(Integer, ForeignKey('threads.thread_id'), nullable=False, index=True)
    board_id      = Column(Integer, nullable=False, index=True)    
    display_id    = Column(Integer, nullable=True, index=True)
    message       = Column(UnicodeText, nullable=True)
    message_short = Column(UnicodeText, nullable=True)
    #message_tree  = Column(UnicodeText, nullable=True) # Should be removed
    message_raw   = Column(UnicodeText, nullable=True)
    invisible     = Column(Boolean, default=False)
    sage          = Column(Boolean, nullable=True)
    op            = Column(Boolean, default=False)
    date          = Column(DateTime, nullable=False, index=True)
    last_modified = Column(DateTime, nullable=True)    
    #spoiler       = Column(Boolean, nullable=True) # WTF is this?
    session_id    = Column(String(64), nullable=False)
    #session_id    = Column(BIGINT, ForeignKey('sessions.session_id'),
    #                       nullable=False, index=True)    
    password      = Column(Unicode(32), nullable=True)
    subject       = Column(UnicodeText, nullable=True) # Should be removed
    name          = Column(UnicodeText, nullable=True)
    #email         = Column(UnicodeText, nullable=True)
    tripcode      = Column(UnicodeText, nullable=True)
    error         = Column(PickleType(pickler=pickle), nullable=True) # Do not load by default
    reference_count = Column(Integer, default=0)    
    #references    = Column(PickleType(pickler=pickle), nullable=True) # Should be removed
    inv_reason    = Column(PickleType(pickler=pickle), nullable=True) # Should be removed (reasons go into modqueue)
    ip            = Column(BIGINT, ForeignKey('ips.ip'), nullable=True, index=True)
    geoip         = Column(String(2), nullable=False, default='NA')
    files_qty     = Column(Integer, nullable=False, default=0)
    thread        = relation(Thread)
    
    deleted = True    
    deleter       = Column(Enum('author', 'op', 'mod'), default='author')
    files         = relation(File, secondary=deleted_post_files_table, lazy=False)        
    deletion_time = Column(DateTime, default=datetime.datetime.now)    
    
    @synonym_for('post_id')
    @property
    def id(self):
        return self.post_id

    def __init__(self, post, deleter):
        self.import_data(post)

        self.deleter = deleter
        files_list = post.files
        meta.Session.delete(post)
        meta.Session.commit()
        for f in files_list:
            self.files.append(f)
        meta.Session.add(self)
        meta.Session.commit()

    def __repr__(self):
        return "<DeletedPost(%s, %s)>" % (self.display_id, self.files)

    def revive(self):
        post = Post()
        post.import_data(self)
        files_list = self.files
        meta.Session.delete(self)
        meta.Session.commit()
        for f in files_list:
            post.files.append(f)
        meta.Session.add(post)
        meta.Session.commit()
        return post
    
threads.Post = Post
threads.DeletedPost = DeletedPost
