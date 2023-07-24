# -*- coding: utf-8 -*-

from hanabira.lib.base import *

from hanabira.lib.export import export, result, error
from hanabira.view import *

from hanabira.model import meta, Post
#from hanabira.model import Notification

import logging
log = logging.getLogger(__name__)

class ApiActionsController(BaseController):
    def __before__(self):
        BaseController.__before__(self) 
        if session.is_bot:
            return abort(403)
    
    @render_view
    def thread_hide(self, board, thread_id, format):
        if not board in session['hide']:
            session['hide'][board] = []
        session['hide'][board].append(int(thread_id))
        session.save()
        if format == 'redir':
            return redirect(url('board', board=board))
        else:
            return result_true

    def thread_sign(self, board, display_id):
        board = g.boards.get(board)
        thread = board.get_thread_simple(display_id)
        if thread:
            session['bookmarks'].add(thread.id)
            session.save()

    @render_view
    def thread_unhide(self, board, thread_id):
        session['hide'][board].remove(int(thread_id))
        if not session['hide'][board]:
            del session['hide'][board]
        session.save()
        return result_true

    def thread_unsign(self, board, display_id):
        board = g.boards.get(board)
        thread = board.get_thread_simple(display_id)
        if thread:        
            session['bookmarks'].remove(thread.id)
            session.save()
                        
    def hide_info(self, board, format):
        if board in session['hideinfo']:
            del session['hideinfo'][board]
        else:
            session['hideinfo'][board] = True
        session.save()
        if format == 'redir':
            return redirect(url('board', board=board))
        else:
            return self._result(True)
        
    @render_view
    def notice_delete(self, mid, format):
        session.delete_notice(mid)
        session.save()
        return DataView(True)    
    """
    def notification_mark_read(self, notification_id, format):
        n = Notification.query.get(notification_id)
        if not n:
            return error(40401)
        if not n.session_id == session.id:
            return error(40351)
        n.unread = False
        meta.Session.commit()
        return DataView(True)
    """
    
    def playlist_add(self, file_id, format):
        f = File.query.get(file_id)
        if f:
            if f.filetype.type == 'music':
                session['playlist'].add(f)
                session.save()
                return self._result(True)
            else:
                return self._result(False)
        else:
            return self._result(False)

    def playlist_remove(self, file_id, format):
        file_id = int(file_id)
        pl = session['playlist']
        if file_id in pl.index:
            pl.remove(file_id)
            session.save()
            return self._result(True)
        else:
            return self._result(False)
        
    # Save to DB and publish it
    def playlist_playing(self, file_id, format):
        return self._result(False)    
