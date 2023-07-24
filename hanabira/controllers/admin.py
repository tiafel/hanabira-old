# -*- coding: utf-8 -*-

from hashlib import md5

from hanabira.lib.base import *
from hanabira.lib.utils import *
from hanabira.lib.visible import VisiblePosts
from hanabira.lib.filters import FilterBase, Filter
from hanabira.lib.cluster import reload_nodes
from hanabira.lib.permissions import check_permissions

from hanabira.model.admins import Admin, AdminKey
from hanabira.model.invites import Invite
from hanabira.model.settings import BooleanSetting, IntegerSetting, StringSetting
from hanabira.model import Post, Thread, Featured, DeletedPost, DeletedThread
from hanabira.model.help import HelpArticle
from hanabira.model.boards import Section, Board
from hanabira.model.permissions import Permission
from hanabira.model.files import File, Filetype, Extension, ratings
from hanabira.model.restrictions import restriction_types, effects, Restriction
from hanabira.model.referers import Referer
from hanabira.model.logs import ModRestrictionActionLog, BaseEventLog, log_types, ModPostInvisibleLog, \
     ModSessionActionLog, ModViewPost, ModViewSession, ModEditFile, ModRevivePost, ModEditPost
from hanabira.model.warnings import WarningRecord

from hanabira.view import *
from hanabira.forms.admins import *
from hanabira.forms.boards import *
from hanabira.forms.help import HelpArticleForm

import logging
log = logging.getLogger(__name__)

class AdminController(BaseController):
    def __before__(self):
        BaseController.__before__(self)
        c.pageinfo.title = _("Management")
        admin = session.get('admin', None)
        if admin and admin.valid() and admin.enabled:
            admin.reload_permissions()
            c.can_see_invisible = admin.has_permission('see_invisible')
            c.can_view_ip = admin.has_permission('view_ip')
            c.can_view_files = admin.has_permission('files')
            c.can_edit_posts = admin.has_permission('edit_posts')
            c.admin = session.admin = admin
            c.rating_strict = False
        else:
            return redirect(url('login'))

    def check_scope(self, scopes, scope):
        if 0 in scopes:
            return True
        if scope in scopes:
            return True
        raise PermissionException("Scope {0} is missing in {1}".format(scope, scopes))

    def log_admin_action(self, event, **kw):
        event(ip=ipToInt(request.ip), session_id=session.id, admin=c.admin, **kw)

    def index(self):
        if c.admin.has_permission('view_admins'):
            return redirect(url('admins'))
        else:
            return redirect(url('profile'))

    @render_view
    @check_permissions('view_admins')
    def admins(self):
        c.pageinfo.subtitle = _('Admins')
        c.admins = Admin.query.all()
        return MakoView('/admin/admins.mako')

    @render_view
    @check_permissions('manage_admins')
    def admins_edit(self, admin_id):
        c.pageinfo.subtitle = _('Admins')
        admin = Admin.query.options(eagerload('permissions')).filter(Admin.admin_id == admin_id).first()
        form  = AdminEditForm(admin)
        c.target_admin = admin
        c.permissions = Permission.query.order_by('type').all()
        c.boards = Board.query.all()
        if request.POST:
            form.rebind(admin, data=request.POST)
            if form.validate():
                form.sync()
                meta.Session.add(admin)
                meta.Session.commit()
                if form.passwd1.value:
                    form.model.set_password(form.passwd1.value)                
        c.form = form
        return MakoView('/admin/admins.edit.mako')

    @check_permissions('manage_admins')
    def admins_permission_add(self, admin_id):
        c.pageinfo.subtitle = _('Admins')
        admin = Admin.query.options(eagerload('permissions')).filter(Admin.admin_id == admin_id).first()
        admin.add_permission(request.POST.get('permission'), request.POST.get('scope'))
        return redirect(url('admins_edit', admin_id=admin_id))

    @check_permissions('manage_admins')
    def admins_permission_del(self, admin_id, permission_id):
        c.pageinfo.subtitle = _('Admins')
        admin = Admin.query.options(eagerload('permissions')).filter(Admin.admin_id == admin_id).first()
        admin.delete_permission(permission_id)
        return redirect(url('admins_edit', admin_id=admin_id))

    @check_permissions('manage_admins')
    def admins_key_add(self, admin_id):
        admin = Admin.query.options(eagerload('permissions')).filter(Admin.admin_id == admin_id).first()
        key = admin.add_key()
        return json.dumps({'key_id':key.id, 'key':key.key})

    @check_permissions('manage_admins')
    def admins_key_del(self, key_id):
        key = AdminKey.query.filter(AdminKey.key_id == key_id).first()
        if key:
            meta.Session.delete(key)
            meta.Session.commit()
        return 'Done'

    @render_view
    @check_permissions('boards')
    def boards(self):
        c.pageinfo.subtitle = _('Boards')
        g.boards.load()
        return MakoView('/admin/boards.mako')

    @render_view
    @check_permissions('settings')
    def settings(self):
        c.pageinfo.subtitle = _('Settings')
        f = [BooleanSetting, IntegerSetting, StringSetting]
        c.settings = {}
        for x in g.settings._all:
            if g.settings._all[x].__class__ in f:
                c.settings[x] = g.settings._all[x]
        if request.POST:
            for x in c.settings:
                value = request.POST.get(x, None)
                c.settings[x].set(value)
                meta.Session.merge(c.settings[x])
            meta.Session.commit()
            reload_nodes()
        return MakoView('/admin/settings.mako')

    @render_view
    @check_permissions('help')
    def help(self):
        c.pageinfo.subtitle = _('Help')
        c.articles = HelpArticle.query.all()
        return MakoView('/admin/help.mako')

    @render_view
    @check_permissions('help')
    def help_new(self):
        c.pageinfo.subtitle = _('Help')
        form = HelpArticleForm(HelpArticle)
        if request.POST:
            form.rebind(HelpArticle, data=request.POST)
            if form.validate():
                form.sync()
                meta.Session.add(form.model)
                form.model.parse()
                meta.Session.commit()
                return redirect(url('help_list'))
        c.form = form
        return MakoView('/admin/help.edit.mako')

    @check_permissions('help')
    def help_edit(self, help_id):
        c.pageinfo.subtitle = _('Help')
        article = HelpArticle.query.filter(HelpArticle.help_id == help_id).first()
        if not article:
            return abort(404)
        c.article = article
        form = HelpArticleForm(article)
        if request.POST:
            form.rebind(article, data=request.POST)
            if form.validate():
                form.sync()
                form.model.parse()
                meta.Session.commit()
                return redirect(url('help_list'))            
        c.form = form
        return render('/admin/help.edit.mako')
        
    @check_permissions('boards')
    def boards_new(self):
        c.pageinfo.subtitle = _('Boards')
        form = BoardForm(Board, filetypes=g.extensions.types.keys())
        if request.POST:
            form.rebind(Board, data=request.POST)
            if form.validate():
                form.sync()
                meta.Session.add(form.model)
                meta.Session.commit()
                g.boards.load()
                reload_nodes()
                return redirect(url('boards'))
        c.form = form
        return render('/admin/boards.edit.mako')

    @check_permissions('boards')
    def boards_edit(self, board_id):
        c.pageinfo.subtitle = _('Boards')
        c.board = board = Board.query.filter(Board.board_id == board_id).first()
        form = BoardForm(board, filetypes=g.extensions.types.keys())
        if not self.admin.has_permission('boards', board_id):
            return self.permission_error('boards')
        if request.POST:
            form.rebind(board, data=request.POST)
            if form.validate():
                form.sync()
                meta.Session.add(board)
                meta.Session.commit()
                g.boards.load()
                reload_nodes()
                return redirect(url('boards'))
        c.form = form
        return render('/admin/boards.edit.mako')

    @check_permissions('sections')
    def sections_edit(self, section_id):
        c.pageinfo.subtitle = _('Sections')
        c.section = section = Section.query.filter(Section.section_id == section_id).first()
        form = SectionForm(section)
        if request.POST:
            form.rebind(section, data=request.POST)
            if form.validate():
                form.sync()
                meta.Session.update(section)
                meta.Session.commit()
                g.boards.load()
                reload_nodes()
                return redirect(url('boards'))
        c.form = form
        return render('/admin/sections.mako')
        

    @check_permissions('sections')
    def sections_new(self):
        c.pageinfo.subtitle = _('Sections')
        form = SectionForm()
        if request.POST:
            form.rebind(Section, data=request.POST)
            if form.validate():
                form.sync()
                meta.Session.add(form.model)
                meta.Session.commit()
                g.boards.load()
                reload_nodes()
                return redirect(url('boards'))
        c.form = form
        return render('/admin/sections.mako')

    @check_permissions('invites')
    def invites_new(self):
        c.pageinfo.subtitle = _('Invites')
        c.invite = None
        reason = request.POST.get('reason', False)
        if reason and len(reason) > 1:
            #reason = filterText(reason)
            c.invite = Invite()
        return render('/admin/invites.mako')

    def profile(self):
        c.pageinfo.subtitle = _('Profile')
        form = ProfileForm(self.admin)
        if request.POST:
            form.rebind(self.admin, data=request.POST)
            if form.validate():
                form.sync()
                meta.Session.update(self.admin)
                meta.Session.commit()
                if form.passwd1.value:
                    form.model.set_password(form.passwd1.value)
                session['admin'] = self.admin
                session.save()
        c.form = form
        return render('/admin/profile.mako')

    @check_permissions('files', False)
    def files(self, filter_id, page, scopes=None):
        c.pageinfo.subtitle = _('Files')
        page = page and int(page) or 0
        filters = {'type':(Filetype, 'list', g.extensions.types.keys()), 'rating':(File, 'list',['unrated', 'sfw', 'r-15', 'r-18', 'r-18g', 'illegal'])}
        sort    = {'file_id':None, 'type':Filetype, 'rating':None, 'date_added':None}
        base    = FilterBase(model=File, filters=filters, sort=sort, query='get_query_with_ft',\
                             default_per_page=100, default_sort=[('file_id', 'desc')])
        c.filter = g.filters.handle(base, request.POST, filter_id)
        if request.POST:
            return redirect(url('files_list', filter_id=c.filter.id, page=0))
        c.files = c.filter.get(page=page)
        return render('/admin/files.mako')

    @check_permissions('files', False)
    def files_by_id(self, file_id, scopes=None):
        f = File.query.filter(File.file_id == file_id).count()
        if f > 0:
            filters = {'file_id':(File, 'list', [file_id])}
            base    = FilterBase(model=File, filters=filters, sort={}, query='get_query_with_ft',\
                                 default_per_page=1)
            filter_id = g.filters.save(Filter(base=base, filters=[('file_id', file_id)]))
            return redirect(url('files_list', filter_id=filter_id, page=0))
        else:
            return abort(404)

    @check_permissions('files', False)
    def file_ajax(self, file_id, scopes=None):
        c.files = File.query.join(Filetype).filter(File.file_id.in_(file_id.split('_'))).all()
        if len(c.files):
            return render('/admin/files_ajax.mako')
        else:
            return "No files found. WTF!?+"

    @check_permissions('files')
    def files_edit(self):
        if request.POST:
            f = File.query.filter(File.file_id == request.POST.get('file_id', None)).first()
            if not f:
                return abort(404)
            r = request.POST.get('rating', None)
            if not r in ratings:
                return abort(404)
            log.info("AdminController.files_edit(%s, %s)" % (f.file_id, r))
            f.rating = r
            self.log_admin_action(ModEditFile, file_id=f.id)
            meta.Session.commit()
            return "Done"
        return "WTF?"
    
    @check_permissions('referers')
    def referers(self, filter_id, page):
        c.pageinfo.subtitle = _('Referers')
        page = page and int(page) or 0
        filters = {'session_new':(Referer, 'list', ['0', '1'])}
        sort    = {'date':None, 'referer_id':None, 'domain':None}
        base    = FilterBase(model=Referer, filters=filters, sort=sort,\
                             default_per_page=100, default_sort=[('referer_id', 'desc')])
        c.filter = g.filters.handle(base, request.POST, filter_id)
        if request.POST:
            return redirect(url('referers', filter_id=c.filter.id, page=0))
        c.referers = c.filter.get(page=page)
        return render('/admin/referers.mako')
    
    @check_permissions('restrictions')
    def restrictions(self, filter_id, page):
        c.pageinfo.subtitle = _('Restrictions')
        page = page and int(page) or 0
        filters = {'type':(Restriction, 'list', restriction_types), 'effect':(Restriction, 'list', effects), 'expired':(Restriction, 'list', ['0', '1'])}
        sort    = {'restriction_id':None, 'type':None, 'date_added':None, 'value':None, 'effect':None, 'expired':None}
        base    = FilterBase(model=Restriction, filters=filters, sort=sort,\
                             default_per_page=100, default_sort=[('effect', 'asc'), ('type', 'asc'), ('expired', 'asc'), ('value', 'asc')],
                             default_filters=[('expired', False)])
        c.filter = g.filters.handle(base, request.POST, filter_id)
        if request.POST:
            return redirect(url('restrictions', filter_id=c.filter.id, page=0))
        c.restrictions = c.filter.get(page=page)
        c.restriction_types = restriction_types
        c.effects = effects
        return render('/admin/restrictions.mako')

    @check_permissions('restrictions')
    def restrictions_new(self):
        req = request.POST
        if req:
            type = req.get('type', None)
            value = req.get('value', None)
            effect = req.get('effect', None)
            comment = req.get('comment', u"")
            if type in g.restrictions.classes and value and effect:
                cls = g.restrictions.classes[type]
                r = cls(value=value, effect=effect, expired=False, scope=0, date_added=datetime.now(), duration=0, comment=comment)
                if r.validate():
                    meta.Session.add(r)
                    meta.Session.commit()
                    self.log_admin_action(ModRestrictionActionLog, restriction=r, action=_("added"))
                    meta.Session.commit()
                    g.restrictions.load()
                    reload_nodes()
        return redirect(url('restrictions'))

    @check_permissions('restrictions')
    def restrictions_expire(self, restriction_id):
        r = Restriction.query.filter(Restriction.restriction_id == restriction_id).first()
        if not r:
            return abort(404)
        r.expired = not r.expired
        self.log_admin_action(ModRestrictionActionLog, restriction=r, action=(r.expired and _("disabled") or _("enabled")))
        meta.Session.commit()
        g.restrictions.load()
        reload_nodes()
        return redirect(url('restrictions'))

    @check_permissions('restrictions')
    def restrictions_edit(self, restriction_id):
        pass
        

    @check_permissions('featured')
    def featured(self):
        if request.POST:
            post_display_id = request.POST['post_display_id']
            thread_display_id = request.POST['thread_display_id']
            boardname  = request.POST['boardname']
            board = g.boards.boards[boardname]
            thread = Thread.query.filter(Thread.board_id == board.id).filter(Thread.display_id == thread_display_id).one()
            post = Post.query.filter(Post.display_id == post_display_id).filter(Post.thread_id == thread.thread_id).one()
            return redirect(url('featured_add', post_id=post.id))
        else:
            return render('/admin/featured.mako')

    @check_permissions('featured')
    def featured_add(self, post_id):
        c.post = post = Post.query.filter(Post.id == post_id).one()
        if request.POST:
            description = request.POST['description']
            show_file   = request.POST.get('show_file', False)
            show_text   = request.POST.get('show_text', False)
            f = Featured.new(post_id=post.id, file_id=(show_file and post.files[0].id), description=description, show_file=show_file, show_text=show_text) 
            return redirect(url('featured'))
        return render('/admin/featured_add.mako')

    @render_view
    @check_permissions('sessions')
    def get_post(self, post_id):
        c.post = post = Post.get(post_id, 1)
        if not post:
            return DataView(_("This post doesn't exist."))

        c.reply = False
        c.thread = thread = c.post.thread or Thread.query.filter(Thread.id == post.thread_id).first()
        c.session = g.sessions.load_by_id(post.session_id)
        c.events  = BaseEventLog.query.filter(BaseEventLog.post_id == post_id).order_by(BaseEventLog.date.desc()).all()
        self.log_admin_action(ModViewPost, post=post, commit=True)
        if not thread:
            c.thread = thread = DeletedThread.query.filter(DeletedThread.id == post.thread_id).first()
            c.pageinfo.description = _("This post's thread is deleted.")
        elif post.deleted:
            c.pageinfo.description = _("This post is deleted.")
        if not thread:
            return DataView(_("Thread id {0} does not exist.").format(post.thread_id))
        if post.op:
            thread.collect_posts(post, [])
        c.board = thread.board
        c.post.thread = thread
        return AdminPostsListView([c.post], extended=True)
    #render('/admin/post_inspect.mako')


    @render_view
    @check_permissions('edit_posts')
    def post_edit(self, post_id, format=None, scopes=None):
        c.post = post = Post.get(post_id=post_id)
        c.message = None
        if not post:
            return abort(404)
        if request.POST:
            post.add_revision(
                name=request.POST.get('name'),
                subject=request.POST.get('subject'),
                message_raw=request.POST.get('message'),
                reason=request.POST.get('reason'),
                admin=c.admin,
            )
            self.log_admin_action(ModEditPost, post=post, commit=True)
            c.message = _("New post revision saved.")
        return MakoView('/admin/post_edit.mako')

    @render_view
    @check_permissions('manage_threads')
    def get_thread(self, thread_id):
        thread, op = meta.Session.query(Thread, Post).join((Post,Thread.op_id==Post.post_id)).filter(Thread.id == thread_id).first() or (None, None)
        if not thread:
            thread, op = meta.Session.query(DeletedThread, DeletedPost).join((DeletedPost, DeletedThread.op_id==DeletedPost.post_id)).filter(DeletedThread.id == thread_id).first() or (None, None)
            c.pageinfo.description = _("This thread is deleted.")
        if thread:
            c.board = board = thread.board
            thread.collect_posts(op, [])
            c.post = op
            c.reply = False
            c.thread = thread
            self.log_admin_action(ModViewPost, post=op, commit=True)
            c.session = g.sessions.load_by_id(op.session_id)
            c.events  = BaseEventLog.query.filter(BaseEventLog.post_id == op.post_id).order_by(BaseEventLog.date.desc()).all()
        else:
            c.pageinfo.description = _("This thread doesn't exist.")
        return AdminPostsListView([c.post], extended=True)
    #MakoView('/admin/thread_inspect.mako')

    @check_permissions('sessions')
    def session(self, session_id):
        c.session_id = session_id
        c.session = g.sessions.load_by_id(session_id)
        if not c.session:
            return abort(404)
        if request.POST:
            if 'premod_reason' in request.POST:                
                # Global premod            
                reason = request.POST['premod_reason']
                wr = WarningRecord('premod', session_id, c.session.last_ip, reason=reason)
                c.session.add_token('premod', ('global', None), -1, admin=session.admin, reason_text=reason)
                c.session.save()
                self.log_admin_action(ModSessionActionLog, target_session_id=session_id, action="added global premod", commit=True)
            elif 'token_data' in request.POST:
                # Remove specified tokens
                token, scope1, scope2 = request.POST['token_data'].split(":")
                if scope1 == 'global':
                    scope2 = None
                elif scope1 == 'thread':
                    scope2 = int(scope2)
                c.session.remove_token(token, (scope1, scope2))
                c.session.save()
                self.log_admin_action(ModSessionActionLog, target_session_id=session_id, action="removed "+request.POST['token_data'], commit=True)
        else:
            self.log_admin_action(ModViewSession, target_session_id=session_id, commit=True)
        c.events  = BaseEventLog.query.filter(BaseEventLog.target_session_id == session_id).order_by(BaseEventLog.date.desc()).limit(20).all()
        c.referers = Referer.query.filter(Referer.session_id == session_id).order_by(Referer.date.desc()).limit(20).all()
        c.warnings = WarningRecord.get_for_session(c.session)
        return render('/admin/session.mako')
    
    @check_permissions('sessions')
    def session_recount(self, session_id):
        sess = g.sessions.load_by_id(session_id)
        if not sess:
            return abort(404)
        
        posts = Post.query.filter(Post.session_id == session_id).count()
        deleted_posts = DeletedPost.query.filter(DeletedPost.session_id == session_id).count()
        inv_posts = Post.query.filter(Post.session_id == session_id).filter(Post.invisible == True).count()
        sess.posts_count = posts + deleted_posts
        sess.posts_invisible = inv_posts
        sess.posts_deleted = deleted_posts
        
        threads = Post.query.filter(Post.session_id == session_id).filter(Post.op == True).count()
        deleted_threads = DeletedPost.query.filter(DeletedPost.session_id == session_id).filter(DeletedPost.op == True).count()
        sess.threads_count = threads + deleted_threads
        sess.threads_deleted = deleted_threads
        
        # Recount chars len too!
        
        sess.save()
        return redirect(h.url('session', session_id=session_id))
        
    
    @check_permissions('view_ip')
    def get_whois(self, ip):
        return whois(int(ip), html=1)
            
    @check_permissions('manage_threads')
    def thread_clean(self, id):
        thread = Thread.find(id)
        thread.clean_invisible()
            
    @check_permissions('manage_threads')
    def thread_merge(self, subj, dest):
        if dest.find('_') > -1:
            board, display = dest.split('_')
            board = g.boards.boards.get(board)
            if board:
                dest_thread = Thread.query.filter(Thread.display_id == display).filter(Thread.board_id == board.id).first()
                if dest_thread: dest = dest_thread.id
                else: return "alert('Here is no thread with display_id %s.')"%(display)
            else: return abort(404)
        else:
            dest_thread = Thread.query.filter(Thread.id == dest).first()
        subj_thread = Thread.query.filter(Thread.id == subj).first()
        if subj_thread.op_id < dest_thread.op_id:
            subj_thread, dest_thread, subj, dest = dest_thread, subj_thread, dest, subj
        posts = Post.post_filters(Post.query.filter(Post.thread_id == subj)).all()
        for post in posts:
            post.thread_id = dest
            post.op = False
        meta.Session.commit()
        dest_thread.bump()
        dest_thread.board.update_thread(dest_thread)
        subj_thread.delete_self()
        
    @check_permissions('manage_threads')
    def thread_transport(self, thread_id, board, dest_board):
        board = g.boards.get(board)
        if not board:
            return u"alert('%s')"%_("Boardname is incorrect.")
        thread = board.export_thread(thread_id, dest_board)
        if not thread:
            return "alert('Can't transport thread')"
        return "location.replace('%s')"%thread.location
    
    @check_permissions('manage_threads')
    def move_posts(self):
        if not request.POST:
            return "No POST data."
        log.info(request.POST)

    @render_view
    @check_permissions('view_ip')
    def get_file_post(self, file_id):
        f = File.query.get(file_id)
        if not f:
            return abort(404)
        c.posts = f.posts
        c.pageinfo.description = u'Posts with file {0.filename} ({0.file_id})'.format(f)
        return AdminPostsListView(c.posts)
    
    @render_view
    @check_permissions('sessions')
    def userposts(self):
        req = request.POST
        do = req['do']
        if do == 'delete':
            thread_ids, post_ids, report = g.post_queries[req['query']]
            try:
                l = 'Deleting threads: '
                for thread in Thread.query.filter(Thread.id.in_(thread_ids)).all():
                    l = '%s, %s'%(l, str(thread.id))
                    thread.delete_self()
                l = '%s.\nDeleting posts: '%l
                for post in Post.query.filter(Post.id.in_(post_ids)).all():
                    l = '%s, %s'%(l, str(post.id))
                    post.delete_self()
            except Exception as e:
                traceback.print_exc()
                log.info("Error: %s in post delete"%e)
                res = "%s<br>Error: %s in post delete"%(l, e)
            else:
                res = "%s<br>has been disembodied."%report
            log.info(l)
            return HTMLView(res)
        
        if do == 'cancel':
            del g.post_queries[req['query']]
            return HTMLView("<html><center>Forgotten.<center></html>")
        
        if do == 'delform':
            threads = {}
            log.info(req)
            for field in req:
                post_id = safe_int(field)
                thread_id = safe_int(req[field])
                if post_id and thread_id:
                    if not thread_id in threads:
                        threads[thread_id] = []
                    if not post_id in threads[thread_id]:
                        threads[thread_id].append(post_id)
            for tid in threads:
                thread = Thread.query.filter(Thread.id == tid).first()
                thread.delete_posts(thread.board, threads[tid], None, c.admin, request, session)
            meta.Session.commit()
            return HTMLView('<html><script>javascript:history.go(-1)</script></html>')
        
        target_ip = None
        if 'post_id' in req:
            post = Post.get(req['post_id'], 1)
            target_session_id = post.session_id
            target_ip = post.ip
        elif 'session_id' in req:
            target_session_id = req['session_id']
        
        if 'deleted' in req and int(req['deleted']):
            post_cls = DeletedPost
        else:
            post_cls = Post
            
        q = post_cls.query.options(eagerload('thread')).join(Thread).filter(post_cls.display_id != None)
        board = g.boards.boards[req['board']]
        by = req['by']
        ops = req['ops']
        loc = req['loc']
        max = safe_int(req.get('max'))
        if by == 'sn':
            range = req['range'].split(' - ')
        q = {
          "ss":lambda: q.filter(post_cls.session_id == target_session_id),
          #"pw":lambda: q.filter(Post.password == post.password),
          #"pi":lambda: q.filter(or_(Post.ip == post.ip, Post.password == post.password)),
          #"rl":lambda: q.filter(Post.session_id.in_(post.session.get('related sessions'))),
          "ip":lambda: q.filter(post_cls.ip == target_ip),
          #"sn":lambda: q.filter(Post.ip.between(ipToInt(range[0]), ipToInt(range[1]))),
          #"ad":lambda: q.filter(or_(Post.session_id == post.session_id, Post.password == post.password, Post.ip == post.ip))
        }[by]()
        q = {
          "ev":lambda: q,
          "ds":lambda: q.filter(post_cls.date > datetime.now()-timedelta(hours=float(req['qty'])*24)),
          "hr":lambda: q.filter(post_cls.date > datetime.now()-timedelta(hours=float(req['qty']))),
          "ps":lambda: q.filter(post_cls.display_id > board.post_index-int(req['qty']))
        }[req['limit']]()
        q = {
          "oa":lambda: q,
          "tt":lambda: q.filter(post_cls.thread_id == post.thread_id),
          "tb":lambda: q.filter(Thread.board_id == board.id).filter(Thread.archived == False),
          "ba":lambda: q.filter(Tread.board_id == board.id),
        }[loc]()
        
        if 'is_op' in req and int(req['is_op']):
            q = q.filter(post_cls.op == True)
        elif 'invisible' in req and int(req['invisible']):
            q = q.filter(post_cls.invisible == True)
        
        q = q.order_by(post_cls.id.desc())
        
        if do == 'stat':
            thread_ids = []
            post_ids = []
            from_own_threads = threads_to_delete = 0
            if ops == 'ex':
                posts = q.filter(Post.op == False).all()
                post_count = posts_to_delete = len(posts)
            else:
                posts = q.filter(Post.op == True).all()
                threads_to_delete = len(posts)
                for p in posts:
                    t = p.thread
                    from_own_threads += t.posts_count
                    thread_ids.append(t.id)
                if ops == 'in':
                    posts = q.filter(Post.op == False).filter(not_(Thread.id.in_(thread_ids))).all()
                    post_count = q.filter(Post.op == False).count() + threads_to_delete
                    posts_to_delete = len(posts)
                    post_ids = map(lambda x: x.id, posts)
            if threads_to_delete and loc != 'tt':
                report = '%s posts: %s threads (totally %s posts) and %s in other threads'%(post_count,threads_to_delete,from_own_threads,posts_to_delete)
            elif loc == 'tt':
                report = '%s posts in this thread'%posts_to_delete
            else:
                report = '%s posts'%posts_to_delete
            if loc in ['tb','ba']:
                report = '%s on this board'%report
            query = (post_ids, thread_ids, report)
            c.report = report
            c.query_id = id = md5(query.__repr__()).hexdigest()
            g.post_queries[id] = query
            return render("/admin/posts_stat.mako")
                
        if do == 'list':
            if ops != 'in':
                q = q.filter(Post.op == (ops == 'is'))
            if max and max > 0:
                q = q.limit(max)
            c.posts = q.all()
            c.check_boxes = True
            return AdminPostsListView(c.posts, has_lookup=False)
        
    @check_permissions('see_invisible')        
    def lastposts(self):
        c.pageinfo.subtitle = _('Last posts')
        return render('/admin/lastposts.mako')
        
    @render_view
    @check_permissions('see_invisible')
    def list_lastposts(self):
        req = request.POST
        q = Post.query.options(eagerload('thread')).join(Thread).filter(Post.display_id != None).filter(Post.date > datetime.now()-timedelta(hours=float(req['time'])))
        if req.get('files'): q = q.filter(Post.files_qty > 0)
        if req.get('sage'): q = q.filter(Post.sage == True)
        if req.get('op'): q = q.filter(Post.op == True)
        if not c.admin.has_permission('see_invisible'): q = q.filter(Post.invisible == False)
        elif req.get('inv'):
            q = q.filter(or_(Post.invisible == True, Post.op == True))
        c.posts = q.order_by(Post.id.desc()).all()
        board = int(req.get('board', '0'))
        if board > 0:
            posts = []
            for post in c.posts:
                if post.thread.board_id == board:
                    posts.append(post)
            c.posts = posts
            
        exclude_api = req.get('exclude_api')
        
        if req.get('inv'):
            posts = []
            for post in c.posts:
                if post.invisible == True or \
                   (post.op == True and post.thread.invisible == True):
                    if not exclude_api or not 'API' in post.inv_reason:
                        posts.append(post)
            c.posts = posts
            
        c.pageinfo.description = 'Posts for last %s hours'%req['time']
        c.last_posts_req = request.POST
        return AdminPostsListView(c.posts)
        
    @check_permissions('sessions')
    def userexec(self):
        req = request.POST
    #    if req['act'] == ban:
            
    #    else:
            
        post = Post.get(req['post_id'], 1)
            
        if req['act'] in ['ban', 'unban']:
            range = req['range'].split(' - ')
        if req['target'] == 'sn':
            target = "%s/%s"%(range[0], implicitMask(range))
        else: 
            target = post.ip
        # У нас оно не от рута запущено. И доступ к iptables оттуда давать ну ОЧЕНЬ не хочется
        #popen("iptables -%s INPUT -s %s -j DROP"%(req['act']=='ban' and 'A' or 'D', target))
        # и вообще сделать с этим что-нибудь
        
    ##
    ## Stubs here
    ##

    @check_permissions('view_log', False)
    def logs_view(self, filter_id, page, scopes=None):
        c.pageinfo.subtitle = _('Referers')
        page = page and int(page) or 0
        filters = {'type':(BaseEventLog, 'list', log_types)}
        sort    = {'log_id':None}
        base    = FilterBase(model=BaseEventLog, filters=filters, sort=sort,\
                             default_per_page=100, default_sort=[('log_id', 'desc')])
        c.filter = g.filters.handle(base, request.POST, filter_id)
        if request.POST:
            return redirect(url('logs', filter_id=c.filter.id, page=0))
        c.logs = c.filter.get(page=page)
        #c.logs = BaseEventLog.query.all()
        return render("/admin/logs.mako")

    @check_permissions('statistics', False)
    def statistics(self, scopes=None):
        return render("/admin/stub.mako")    

    @check_permissions('permissions')
    def permissions(self):
        c.pageinfo.subtitle = _('Permissions')
        return render("/admin/stub.mako")
        c.permissions = CompoundPermission.query.all()

