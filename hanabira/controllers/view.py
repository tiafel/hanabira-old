# -*- coding: utf-8 -*-
import logging
from sqlalchemy.orm import eagerload
from hanabira.lib.base import *
from hanabira.lib.utils import *
from hanabira.lib.export import ExportJSON, ExportAtom, ExportRSS, Export
from hanabira.model import meta
from hanabira.model import Thread, Post, Featured
from hanabira.model.logs import BaseEventLog
from sqlalchemy.sql import union
from hanabira.model.files import File
from hanabira.model.help import HelpArticle
from sqlalchemy.sql import and_, or_, not_, union
from hanabira.lib.visible import VisiblePosts
from datetime import datetime
import string, time, random
log = logging.getLogger(__name__)

class ViewController(BaseController):
    def main(self):
        return 'This is view.main()'
    
    def frameset(self, format='xhtml', since=None, key=None, count=None, **kw):
        #log.info('ViewController.frameset({0}, {1}) for {2.ip}'.format(ext, since, c))
        if format == 'xhtml':
            return render('/view/frameset.mako')
        else:
            if not since:
                since = request.GET.get('since', None)
            if not count:
                count = request.GET.get('count', 100)
            count = int(count)
            if not key:
                key  = request.GET.get('key', None)
            admin = self._get_admin(key, c)
            pq = Post.query.options(eagerload('files')).options((eagerload('thread'))).filter(Post.display_id != None)
            if not admin or not admin.has_permission('see_invisible'):
                pq = pq.filter(Post.invisible == False)
            if since:
                since = datetime.strptime(since, '%Y-%m-%d %H:%M:%S')
                pq = pq.filter(Post.date >= since)
            posts = pq.order_by(Post.post_id.desc()).limit(count).all()
            threads = {}
            for post in posts:
                if not post.thread_id in threads:
                    thread = post.thread
                    thread.posts = []
                    threads[thread.id] = thread
                    threads[post.thread_id].posts.append(post)
            events = []
            if since and admin and admin.has_permission('view_log'):
                events = BaseEventLog.query.filter(BaseEventLog.date > since).\
                         filter(or_(BaseEventLog.admin_id != admin.id, BaseEventLog.admin_id == None)).\
                         filter(not_(BaseEventLog.type.in_(['auto_session_ban', 'auto_post_invisible', 'mod_login', 'mod_view_post', 'mod_view_session']))).all()
        return Export(format=format, threads=list(threads.values()), events=events, admin=admin, response=response)
        
    def thread_post(self, board, post_id):        
        b = g.boards.get(board)
        if b and b.check_permissions('read', c.admin, c.channel):
            post = b.get_post(post_id)
            if post and post.showable(session, b):
                url = post.thread.location
                if post.op:
                    return redirect(url)
                else:
                    return redirect(str('%s#i%s'%(url, post_id)))
            else:
                return abort(404)
        else:
            return abort(404)

    # XXX: Wrap in @Thread.fetcher
    # XXX: WTF is archive keyword?
    def thread(self, board, thread_id, format='xhtml', archive=False):
        if format == 'html':
            return render('/view/bots.mako')
        ref = request.headers.get('Referer', '')
        if format != 'xhtml' and 'xhtml' in ref:
            return "This interface is not allowed to be used repeatedly."
        
        archive = archive == 'True'
        thread_id = safe_int(thread_id)
        if not thread_id:
            return abort(403)
        c.board = board = g.boards.get(board)
        if board and board.check_permissions('read', c.admin, c.channel):
            thread = board.get_thread(thread_id, fetch=False)
            if not thread:
                return abort(404)

            handle_etag(thread.last_modified)
            
            if thread.is_censored(session):
                c.thread = thread
                return render('/view/censored.mako')
            
            trace_time('fetch_posts')
            thread.fetch_posts(admin=c.admin, visible_posts=session['visible_posts'])
            trace_time('fetch_posts')
            c.pageinfo.set(board, thread)
            c.threads = [thread]
            c.banner = g.boards.get_banner(board, session)
            c.reply = True
            c.thread = c.threads[0]
            c.archive = thread.archived
            c.bookmarks = session['bookmarks']
            c.scroll_to = session.get('scroll_to')
            sc = False
            if c.scroll_to:
                session['scroll_to'] = None
                sc = True
            board.set_context_permissions(context=c, admin=c.admin)
            if thread.invisible and not session['visible_posts'].has_thread(thread):
                session['visible_posts'].add_thread(thread)
                sc = True
            if c.bookmarks.is_faved(thread.id):
                c.bookmarks.visited(thread.id)
                sc = True
            if sc:
                session.save()
            
            # Hack for now, should implement some smarter solution later
            if format in ['html', 'xhtml']:
                return render('/view/posts.mako')
            else:
                return Export(threads=c.threads, admin=c.admin, board=board, format=format, response=response)
                
        else:
            return abort(404)
    
    def board(self, board, page, format, archive):
        if format == 'html':
            return render('/view/bots.mako')
        c.board = board = g.boards.get(board)
        if board and board.check_permissions('read', c.admin, c.channel):
            archive = archive == 'True'
            if page == 'index' or page == 'wakaba':
                page = '0'
            c.pageinfo.set(board, page=page)
            c.banner = g.boards.get_banner(board, session)
            page = c.pageinfo.page
            if page is None:
                return abort(404)
            hidden = session['hide'].get(board.board, [])
            if page < 0:
                return abort(403)
            trace_time('board.get_threads')
            if archive:
                c.threads = board.get_archive_threads(page=page)
            else:
                c.threads = board.get_threads(admin=c.admin, page=page, archive=archive, hidden=hidden, visible_posts=session['visible_posts'])
            trace_time('board.get_threads')
            if not c.threads and page > 0:
                return abort(404)
                
            if c.threads:
                handle_etag([str(x.thread_id) for x in c.threads],
                    max(c.threads, key=lambda x:x.last_modified).
                                     last_modified)
                                                                                        
            c.bookmarks = session['bookmarks']
            session['stats'][board.board] = board.stats_posts()
            session.save()
            trace_time('board.pages')
            c.pages = board.get_pages(admin=c.admin, archive=archive, hidden=hidden, visible_posts=session['visible_posts'])
            trace_time('board.pages')
            board.set_context_permissions(context=c, admin=c.admin)
            c.archive = archive
            if format in ['html', 'xhtml']:
                return render('/view/posts.mako')
            else:
                return Export(threads=c.threads, admin=c.admin, board=board, format=format, page=page, pages=c.pages, response=response)
        else:
            return abort(404)

    # XXX: Move this to just thread()
    def deleted_thread(self, board, thread_id, format='xhtml'):
        c.board = board = g.boards.get(board)
        if board and board.check_permissions('read', c.admin, c.channel):
            c.thread = thread = board.get_thread(thread_id, admin=c.admin, visible_posts=session['visible_posts'], deleted=True)
            if not thread:
                return abort(404)
            if not thread.posts:
                return abort(404)
            c.threads = [thread]
            c.pageinfo.set(board, thread)
            c.reply = True
            c.deleted = True
            board.set_context_permissions(context=c, admin=c.admin)
            if format in ['html', 'xhtml']:
                return render('/view/posts.mako')   
            
    def archive_last(self, board):
        c.board = board = g.boards.get(board)
        if board and board.check_permissions('read', c.admin, c.channel):
            hidden = session['hide'].get(board.board, [])
            pages = board.get_pages(admin=c.admin, archive=True, 
                                    hidden=hidden,
                                    visible_posts=session['visible_posts'])
            return redirect(url('board_arch', board=board.board, page=(pages-1)))
        raise abort(404)
            
            
    def post_error(self, post_id):
        post_id = int(post_id)
        if session.get('posts', None) and post_id in session['posts']:
            board = session['posts'][post_id]
            c.board = board = g.boards.boards[board]
            c.pageinfo.title = board.title
            c.pageinfo.description = board.description
            c.post = post = board.get_unfinished_post(post_id)
            c.thread = post.thread
            c.reply  = not post.op
            c.errors = post.error
            c.hideinfo = []
        else: 
            c.error_message = _('You should enable cookies.')
        return render('/error/post.mako')

    def frame(self, **kw):
        c.onload = "update_board_stats();"
        return render('/view/frame.mako')
    
    def featured(self, page=0, **kw):
        c.featured_files = Featured.query.filter(Featured.show_file==True).order_by(Featured.date.desc()).limit(10).all()
        for img in c.featured_files:
            img.thread = img.post.thread
            img.board = g.boards.board_ids[img.thread.board_id]
        threads = []
        featured_posts = Featured.query.filter(Featured.show_text==True).order_by(Featured.date.desc()).limit(3).all()
        for img in featured_posts:
            img.thread = img.post.thread
            img.board = g.boards.board_ids[img.thread.board_id]
            thread = img.board.get_thread(img.thread.display_id, get_posts=False)
            thread.op = img.post
            threads.append(thread)
        news = []
        if g.settings.featured.news:
            c.board = board = g.boards.boards[str(g.settings.featured.news)]
            news = board.get_threads(admin=c.admin, page=page, see_invisible=None, get_posts=False, get_ops=True, ignore_sticky=True)
        c.news = sorted(news + threads, key=lambda x:x.op.date, reverse=True)
        return render('/view/featured.mako')

    def settings(self):
        if request.POST:
            session['rating_strict'] = not bool(request.POST.get('rating_strict', False))
            r = request.POST.get('rating', g.settings.censorship.default).lower()
            if r in ['sfw', 'r-15', 'r-18', 'r-18g']:
                session['rating'] = r
            session['reply_button'] = int(request.POST.get('reply_button', 1))
            session['scroll_threads'] = int(request.POST.get('scroll_threads', 1))
            session['mini'] = int(bool(request.POST.get('mini')))
            session['nopostform'] = int(bool(request.POST.get('nopostform')))
            session['banners'] = request.POST.get('banners')
            lang = request.POST.get('language', g.settings.chan.language).lower()
            if lang in ['ru', 'en', 'ru_ua', 'ja']:
                session['language'] = lang
                session['captcha'].set(lang=lang)
            session.save()
        else:
            c.pageinfo.title = _("Settings")
            c.rating = session['rating']
            c.rating_strict = not session['rating_strict']
            c.hidden = {}
            for b in session['hide']:
                board = g.boards.get(b)
                if board and board.check_permissions('read', c.admin, c.channel):
                    hidden = session['hide'][b]
                    if len(hidden) > 4:
                        c.hidden[b] = {0:hidden[:-4:-1], 1:hidden[-4::-1]}
                    else:
                        c.hidden[b] = {0:hidden[::-1], 1:[]}
            return render('/view/settings.mako')
            
    def bookmarks(self):
        c.pageinfo.title = _("Subscription")
        c.bookmarks = bookmarks = session['bookmarks']

        threads = Thread.query.filter(Thread.thread_id.in_(list(bookmarks.visits.keys()))).order_by(Thread.board_id.asc(), Thread.last_modified.desc()).limit(100).all()
        data = []
        board = [None, []]
        for thread in threads:
            if board[0] != g.boards.get(id=thread.board_id):
                if board[0]:
                    data.append(board)
                board = [g.boards.get(id=thread.board_id), []]
            board[1].append((thread, bookmarks.visits[thread.id]))
        if board[0] and board[1]:
            data.append(board)
        # data = [(board, [(thread, visited),..]),...]
        c.bookmarks_data = data
        return render('/view/bookmarks.mako')
        

    def help(self, handle):
        article = HelpArticle.query.filter(HelpArticle.handle == handle).filter(HelpArticle.language == session['language']).first()
        if not article:
            article = HelpArticle.query.filter(HelpArticle.handle == handle).first()
            if not article:
                return abort(404)
        c.pageinfo.title = _("Help")
        c.pageinfo.subtitle = article.title
        c.article = article
        return render('/view/help.mako')

    def help_index(self):
        articles = HelpArticle.query.filter(HelpArticle.language == session['language']).order_by(HelpArticle.index.asc()).all()
        if not articles:
            articles = HelpArticle.query.filter(HelpArticle.language == 'en').order_by(HelpArticle.index.asc()).all()
        c.pageinfo.title = _("Help")
        c.articles = articles
        return render('/view/help.index.mako')
