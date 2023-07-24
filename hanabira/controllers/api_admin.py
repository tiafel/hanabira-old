# -*- coding: utf-8 -*-

from hanabira.lib.base import *

from hanabira.model import Post, Thread
from hanabira.model.files import File
from hanabira.model.admins import AdminKey
from hanabira.model.logs import *
from hanabira.model.warnings import WarningRecord, generate_post_warn_message

from hanabira.lib.visible import VisiblePosts, ensure_visible
from hanabira.lib.export import export, result, error
from hanabira.lib.permissions import check_permissions
from hanabira.view import *

import logging
log = logging.getLogger(__name__)

class ApiAdminController(BaseController):
    
    def log_admin_action(self, event, **kw):
        event(ip=ipToInt(request.ip), session_id=session.id, admin=c.admin, **kw)
        
    @render_view
    @check_permissions('edit_posts', allow_key=True)
    @Post.fetcher
    def reset_name(self, post, board):
        if post.name != board.default_name or post.tripcode:
            post.name = board.default_name
            post.tripcode = ''
            post.thread.update_stats()
            meta.Session.commit()
            return result_true
        else:
            return result_false
    
    @render_view
    @check_permissions('edit_posts')
    @Post.fetcher
    def delete_images(self, post):
        if not post.files:
            return result_false
        post.files = []
        post.thread.update_stats()
        meta.Session.commit()
        return result_true
            
    @render_view
    @check_permissions('restrictions', allow_key=True)
    @Post.fetcher
    def hide_post(self, post):
        changed = post.hide(post.session(session))
        if changed:
            ModPostInvisibleLog(ipToInt(request.ip), session.id, session.admin, post=post, action=u"invisible")
            meta.Session.commit()
        return DataView(changed)
    
    @render_view
    @check_permissions('restrictions', allow_key=True)
    @Post.fetcher
    def show_post(self, post):
        bump = False
        if 'bump' in request.params:
            if int(request.params['bump']):
                bump = True
        changed = post.show(post.session(session), bump=bump)
        if changed:
            ModPostInvisibleLog(ipToInt(request.ip), session.id, session.admin, post=post, action=u"visible")
            meta.Session.commit()
        return DataView(changed)
    
    @render_view
    @check_permissions('revive_post', allow_key=True)
    @Post.fetcher
    def revive_post(self, post, thread):
        if thread.deleted and not post.op:
            return result_false

        if thread.deleted and post.op:
            thread.revive()
        else:
            post.revive()
        self.log_admin_action(ModRevivePost, post=post, commit=True)
        return result_true
    
    @render_view
    @check_permissions('delete_threads')
    @Post.fetcher
    def delete_post(self, post, thread, board):
        if post.deleted:
            return result_false
        if post.op:
            thread.delete_self(deleter='mod')
            self.log_admin_action(ModThreadDeleteLog, thread=thread, commit=True, reason="")
        else:
            post.delete_self(deleter='mod')
            self.log_admin_action(ModPostDeleteLog, post=post, commit=True, reason="")
        return result_true
    
    #
    # Threads
    #
    
    @render_view
    @check_permissions('manage_threads')
    @Thread.fetcher
    def thread_set(self, thread, attr, value):
        value = bool(int(value))
        if attr == 'archived':
            thread.archive(value)
            meta.Session.commit()
        elif attr in ['autosage', 'sticky', 'locked', 'op_moderation', 'censor_lim', 'censor_full']:
            now = datetime.now()
            thread.last_modified = now            
            thread.__setattr__(attr, value)
            meta.Session.commit()
        else:
            return error_api_bad_parameter
        return DataView(int(getattr(thread, attr)))
    
    @render_view
    @check_permissions('restrictions', allow_key=True)
    @Post.fetcher
    def ban_user(self, post):
        """
        sess = g.sessions.load_by_id(post.session_id)
        #if not sess['invisible']:
        #    sess['invisible'] = True
            sess['inv_reason'] = ["Mod-chan'ed"]
            ModSessionActionLog(ipToInt(request.ip), session.id, session.admin, sess.id, action=u"invisible")
            meta.Session.commit()
            sess.save()
            return result_true
        else:
            return result_false
        """

    @render_view
    @check_permissions('restrictions', allow_key=True)
    @Post.fetcher
    def unban_user(self, post):
        """
        sess = g.sessions.load_by_id(post.session_id)
        #if sess['invisible']:
        #    sess['invisible'] = False
            ModSessionActionLog(ipToInt(request.ip), session.id, session.admin, sess.id, action=u"visible")
            meta.Session.commit()
            sess.save()
            return result_true
        else:
            return result_false
        """

    @render_view
    @check_permissions('restrictions', allow_key=True)
    @Post.fetcher
    def warnban_user(self, post, thread, board):
        sess = g.sessions.load_by_id(post.session_id)
        #print request.POST
        
        reasons        = request.POST.getall('admin_user_warn_reason[]')
        token_type     = request.POST['admin_user_token_type']
        token_scope    = request.POST['admin_user_token_scope']
        token_duration = int(request.POST['admin_user_token_duration'])
        
        add_action = request.POST['additional_action']
        send_warning = 'admin_user_warn_send' in request.POST
        
        if not (reasons and send_warning) and token_type == "none":
            print("Nothing to do")
            raise Exception("No warning to send, no restriction to add")
        
        if token_type != 'none':
            if not token_type in ['forbid_post', 'premod', 'bypass_premod', 'forbid_name', 'forbid_name_subj', 'forbid_files']:
                raise Exception("Unknown token type")
            if token_scope == 'thread':
                token_scope = (token_scope, thread.id)
            elif token_scope == 'board':
                token_scope = (token_scope, board.board)
            else:
                token_scope = ('global', None)
            if token_type == 'forbid_name_subj':
                sess.add_token('forbid_name', token_scope, token_duration, reason_post_id=post.id, reasons=reasons, admin=session.admin)
                sess.add_token('forbid_subj', token_scope, token_duration, reason_post_id=post.id, reasons=reasons, admin=session.admin)
            else:
                sess.add_token(token_type, token_scope, token_duration, reason_post_id=post.id, reasons=reasons, admin=session.admin)
            self.log_admin_action(ModSessionActionLog, target_session_id=post.session_id, action="added {0}:{1[0]}:{1[1]}".format(token_type, token_scope))
        
        # Send warning
        if reasons and send_warning:
            msg = generate_post_warn_message(reasons, post, thread, board, deleted=(add_action == 'del'), token=(token_type, token_scope, token_duration))
            sess.add_notice(msg, 'warn')
            
        # Delete/Make visible
        if add_action == 'del':
            if post.op:
                thread.delete_self(deleter='mod')
                self.log_admin_action(ModThreadDeleteLog, thread=thread, commit=True, reason="")
            else:
                post.delete_self(deleter='mod')
                self.log_admin_action(ModPostDeleteLog, post=post, commit=True, reason="")
        elif add_action == 'vis':
            post.show(post.session(session), bump=False)
            ModPostInvisibleLog(ipToInt(request.ip), session.id, session.admin, post=post, action=u"visible")

        # Add to warnings/bans database
        wr = WarningRecord(token_type, post.session_id, post.ip, post_id=post.id, reason=reasons)
        
        meta.Session.commit()
        sess.save()
        return result_true
