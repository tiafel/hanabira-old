# -*- coding: utf-8 -*-

from hanabira.lib.base import *
from hanabira.lib.export import export, result, error, Export, export_result

from hanabira.model import meta, Post, Thread
from hanabira.view import *
from hanabira.lib.visible import ensure_visible

import logging
log = logging.getLogger(__name__)

class ApiDataController(BaseController):
    #
    # Global exports
    #

    @render_view
    def chan_banners_list(self):
        return DataView(g.boards.banners)  
    
    def chan_stats_diff(self, format):
        if format == 'json':
            diff = {}
            if not 'stats' in session:
                session['stats'] = {}
            for b in g.boards.boards:
                board = g.boards.boards[b]
                if board.check_permissions('read', c.admin, c.channel):
                    if not b in session['stats']: 
                        session['stats'][b] = board.stats_posts()
                    diff[b] = board.stats_posts_diff(session['stats'][b])
            session.save()
            return json.dumps(diff)
        else: 
            indexes = {}
            for b in g.boards.boards:
                board = g.boards.boards[b]
                if board.check_permissions('read', c.admin, c.channel):
                    indexes[b] = board.post_index
            return json.dumps(indexes)  
    
    #
    # Board exports
    #
    
    
    #
    # User exports
    #
    
    @render_view
    def user_info(self):
        return UserSessionView(session)

    def user_playlist(self, format):
        return session['playlist'].export()
    
    #
    # Thread exports
    #
    
    @render_view
    @Thread.fetcher
    def thread_info(self, thread, board):
        handle_etag(thread.last_modified)
        return ThreadAPIView(thread, board)
    
    @render_view
    @Thread.fetcher
    def thread_all(self, thread, board):
        handle_etag(thread.last_modified)
        q = Post.post_filters(
            thread=thread, 
            visible_posts=session['visible_posts'].get_posts(thread),
            see_invisible=session.get_token('see_invisible', board_id=board.id)
        ).order_by(Post.display_id.asc())
        thread.posts = q.all()
        return ThreadAPIView(thread, board)
    
    @render_view
    @Thread.fetcher
    def thread_new(self, thread, board):
        handle_etag(thread.last_modified)
        if not 'last_post' in request.GET:
            return error_api_missing_parameter(parameter='last_post')
        last_post = int(request.GET['last_post'])
        if last_post < thread.display_id:
            return error_api_bad_parameter(parameter='last_post')
        q = Post.post_filters(
            thread=thread,
            visible_posts=session['visible_posts'].get_posts(thread),
            see_invisible=session.get_token('see_invisible', board_id=board.id)
        ).filter(Post.display_id > last_post).order_by(Post.display_id.asc())
        thread.posts = q.all()
        post_html = 'post_html' in request.GET
        return ThreadAPIView(thread, board, post_html=post_html)
                
    @render_view
    @Thread.fetcher
    def thread_last(self, thread, board):
        if thread.id == 168789:
            return None
        handle_etag(thread.last_modified)
        last_post = int(request.GET.get('last_post', '0'))
        count = int(request.GET.get('count', '100'))
        q = Post.post_filters(thread=thread, visible_posts=session['visible_posts'].get_posts(thread),
                              see_invisible=(c.admin and c.admin.has_permission('see_invisible', board.board_id))
                              )
        if last_post:
            q = q.filter(Post.display_id < last_post)
        thread.posts = q.order_by(Post.display_id.desc()).limit(count).all()
        thread.posts.reverse()
        return ThreadAPIView(thread, board)

    def thread_expand(self, board, thread_id, format, last_post=None, reply=True):
        c.board = board = g.boards.get(board)
        if board and c.board.check_permissions('read', c.admin, c.channel):
            thread = board.get_thread(thread_id, admin=c.admin, visible_posts=ensure_visible(session), after=last_post)
            if thread:
                c.reply = int(reply)
                c.expanded = not last_post
                board.set_context_permissions(c, c.admin)
                return render('/view/thread_expansion.mako', {'thread':thread, 'board':board})
            else:
                return _("This thread does not exist anymore.")
        else:
            return _("Boardname is incorrect.")   
        
    @render_view
    def threads(self):
        since = None
        if 'since' in request.GET:
            try:
                since = datetime.strptime(request.GET['since'],
                                          '%Y-%m-%d %H:%M:%S')
            except:
                return error_api_bad_parameter(param='since',
                                               descr="Should be in %Y-%m-%d %H:%M:%S format")
            if not (0 <= (datetime.now() - since).days <= 2):
                return error_api_bad_parameter(param='since', 
                                               descr="Should be within 2 days")
        if not since:
            since = datetime.now() - timedelta(hours=24)     
        threads = Thread.query.filter(Thread.created >= since).\
                filter(Thread.display_id != None).all()
        boards = {}
        for thread in threads:
            board = g.boards.get(id=thread.board_id)
            if not board.check_permissions('read', c.admin, c.channel):
                continue
            if not board in boards:
                boards[board] = []
            boards[board].append(thread)
        return BoardsView(boards)
        
            
                
    #        
    # Post exports
    #
    
    @render_view
    @Post.fetcher
    def post_info(self, board, thread, post, format):
        etag = post.date
        if post.last_modified and post.last_modified > etag:
            etag = post.last_modified
        handle_etag(etag)
        if post.showable(session, board):
            return PostAPIView(post, thread, board)
        else:
            if thread.deleted:
                return error_thread_deleted
            else:
                return error_post_deleted
        
    @render_view
    @Post.fetcher
    def post_references(self, post):
        references = post.load_references()
        # Invert into thread.posts -> post
        threads = {}
        for post in references:
            if not post.thread_id in threads:
                threads[post.thread_id] = post.thread
                threads[post.thread_id].posts = []
            threads[post.thread_id].posts.append(post)
        # Okay, wtf it should return?
        return DataView(threads.values())
