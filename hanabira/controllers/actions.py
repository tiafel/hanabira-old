# -*- coding: utf-8 -*-
from hanabira.lib.utils import *
from hanabira.lib.base import *
from hanabira.model import Post
import time

import logging
log = logging.getLogger(__name__)


class ActionsController(BaseController):

    def captcha(self, board, rand=None):
        #print("captcha()")
        data = session['captcha'].draw(board)
        session.save()
        #print("captcha data len=", len(data))
        response.headers['Content-Length'] = len(data)
        response.headers['Content-Type'] = 'image/png'
        return data

    def post(self, board, format, post_id):
        if not board in g.boards.boards:
            return abort(403)
        log.debug("ActionsController.post('{0}', {1}): {2.ip}, {3} bytes".format(board, post_id, request, len(request.POST.get('message', ''))))
        redir = None
        board = g.boards.boards[board]
        if post_id and post_id != u'new':
            post_id = int(post_id)
        else:
            post_id = 0
        new_file = 'new_file' in request.POST
        post = board.new_post(post_id, session, request, hold=new_file)
        if post is None:
            return abort(403)
        if type(post) == list:
            c.error_message = u'<br />'.join(post)
            return render('/error/post.mako')
        sc = False
        if post.display_id:
            if session['bookmarks'].is_faved(post.thread.id):
                session['bookmarks'].visited(post.thread.id)
                sc = True
            if post.thread.invisible and not session['visible_posts'].has_thread(post.thread):
                session['visible_posts'].add_thread(post.thread)
                sc = True
            if session['redirect'] == 'board':
                redir = url('board', board=board.board)
            elif session['redirect'] == 'thread':
                if c.scroll_threads:
                    session['scroll_to'] = request.POST.get('scroll_to')
                    sc = True
                redir = url('thread', board=board.board, thread_id=post.thread.display_id)
            else:
                redir = url('board', board=board.board, page=session['redirect'])
            if sc:
                session.save()
        else:
            if new_file:
                redir = url('util_file_new', post_id=post.post_id, filetype=request.POST.get('new_file_type', 'image'))
            else:
                redir = url('post_error', post_id=post.post_id)
        if 'X-Progress-ID' in request.environ['QUERY_STRING']:
            return """<html><script>parent.location.replace('%s');</script></html>""" % redir
        else:
            return redirect(redir)

    def delete(self, board):
        if not board in g.boards.boards:
            return redirect(url('board', board=board.board))

        board = g.boards.boards[board]
        admin = session.get('admin', None)
        if admin and (not admin.valid() or not admin.enabled):
            admin = None

        threads = {}
        if request.POST:
            password = request.POST.get('password', None)
            for field in request.POST:
                post_id = safe_int(field)
                thread_id = safe_int(request.POST[field])
                if post_id and thread_id:
                    if not thread_id in threads:
                        threads[thread_id] = []
                    if not post_id in threads[thread_id]:
                        threads[thread_id].append(post_id)
            if threads:
                res = board.delete_posts(threads=threads, password=password, admin=admin, request=request, session=session)
                if res:
                    c.error_message = res
                    return render('/error/post.mako')

        if c.referer:
            m = parse_url(c.referer)
            if m.get('thread'):
                return redirect(url('thread', board=board.board, thread_id=m['thread']))
            elif m.get('page'):
                return redirect(url('board', board=board.board, page=m['page']))
        return redirect(url('board', board=board.board))
