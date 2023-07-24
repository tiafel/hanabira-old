import logging

from hanabira.lib.utils import *
from hanabira.lib.base import *
from hanabira.model.files import *
from hanabira.model import meta, Post, Thread
from hanabira.view import *
import time, cgi, os
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
import subprocess

log = logging.getLogger(__name__)

class UtilsController(BaseController):
    def file_new(self, filetype, post_id):
        post_id = int(post_id)
        c.post = post = Post.get(post_id = post_id)
        return render('/utils/image.new.mako')
    
    def image_new(self, post_id):
        post_id = int(post_id)
        c.post = post = Post.get(post_id = post_id)
        if not post:
            return abort(404)
        c.board = board = g.boards.board_ids[post.thread.board_id]
        if not board:
            return abort(404)
        if request.POST:
            if request.POST.get('upload', False):
                f = request.POST.get('file', None)
                rating = request.POST.get('rating', 'sfw').lower().strip()
                if not rating in ['sfw', 'r-15', 'r-18', 'r-18g']:
                    rating = 'sfw'
                if isinstance(f, cgi.FieldStorage):
                    fs = FileSet(board=board, fileset=post.files)
                    f2 = fs.add_from_fobj(f, rating)
                    if f2:
                        post.files.append(f2)
                        post.error = []
                        meta.Session.commit()
                        return redirect(url('util_image_edit_new', post_id=post.id, file_id=f2.id))
                return render('/utils/image.new.mako')
            else:
                filename = request.POST.get('shi_filename', '').strip()
                if not filename:
                    filename = str(long(time.time() * 10**3))
                width = int(request.POST.get('shi_width', '600'))
                height = int(request.POST.get('shi_height', '600'))
                tool = request.POST.get('tool', 'shi_pro')
                shi_type = None
                if tool == 'shi_pro':
                    shi_type = 'pro'
                else:
                    shi_type = 'normal'
                newfile = g.newfiles.new(post_id, filename, 'image')
                newfile.width = width
                newfile.height = height
                newfile.tool = tool
                newfile.shi_type = shi_type
                newfile.source = None
                newfile.animation = bool(request.POST.get('shi_animation', False))                
                return redirect(url('util_shi_new', file_id=newfile.id, file_key=newfile.key))
        return render('/utils/image.new.mako')

    def image_edit(self, file_id, post_id, new):
        log.info("utils.image_edit(%s, %s, %s) %s @ %s" % (file_id, post_id, new, request.method, request.ip))
        c.post = post = Post.get(post_id = post_id)
        if post:
            c.board = board = g.boards.board_ids[post.thread.board_id]
            c.file = f = File.get(file_id = file_id)
            c.fonts = g.fonts.fonts
            if f and f.filetype.type == 'image':
                if request.POST:
                    if not request.POST.get('tool', None) or not request.POST.get('w', None):
                        # Spam-bot with wrong POST form
                        return abort(403)
                    if not new:
                        fs = FileSet(board=board)
                        newpost = board.empty_post(thread_id=post.thread.display_id, fileset=fs,\
                                                   password=session['password'], admin=session.get('admin', None), ip=request.ip, session_id=session.id)
                        session['posts'][newpost.post_id] = board.board
                        session.save()                        
                        post = newpost
                    else:
                        fs = FileSet(board=board, fileset=post.files)
                    if post.display_id:
                        return abort(403)
                    f2 = None
                    wd = int(request.POST.get('w', '0') or '0')
                    hg = int(request.POST.get('h', '0') or '0')
                    x = int(request.POST.get('x', '0') or '0')
                    y = int(request.POST.get('y', '0') or '0')
                    tool = request.POST.get('tool')
                    if tool in ['macro']:
                        # XXX: rewrite macro/demotivator tools with Pillow
                        raise Exception("Temporarily disabled")
                    elif tool in ['shi_normal', 'shi_pro']:
                        filename = request.POST.get('shi_filename', '').strip()
                        if not filename:
                            filename = str(long(time.time() * 10**3))
                        width = int(request.POST.get('shi_width', '600'))
                        height = int(request.POST.get('shi_height', '600'))
                        shi_type = None
                        if tool == 'shi_pro':
                            shi_type = 'pro'
                        else:
                            shi_type = 'normal'
                        newfile = g.newfiles.new(post.id, filename, 'image')
                        newfile.width = width
                        newfile.height = height
                        newfile.tool = tool
                        newfile.shi_type = shi_type
                        newfile.source = g.fs.web(f.path)
                        newfile.animation = bool(request.POST.get('shi_animation', False))
                        return redirect(url('util_shi_new', file_id=newfile.id, file_key=newfile.key))
                    if f2:
                        post.files.append(f2)
                        post.error = []
                        meta.Session.commit()
                        return redirect(url('post_error', post_id=post.post_id))
                return render('/utils/image.edit.mako')
            else:
                return abort(403)
                

    def image_shi(self, file_id, file_key):
        file_id = int(file_id)
        newfile = g.newfiles.get(file_id, file_key)
        if not newfile:
            return abort(403)
        c.width = newfile.width
        c.height = newfile.height
        c.post_id = newfile.post_id
        c.file_id = newfile.id
        c.file_key = newfile.key
        c.shi_type = newfile.shi_type
        c.source  = newfile.source
        c.animation = newfile.animation
        return render('/utils/shi.mako')

    def image_shi_save(self, environ, start_response, file_id, file_key):
        file_id = int(file_id)
        newfile = g.newfiles.get(file_id, file_key)
        if not newfile:
            return abort(403)
        post  = Post.get(post_id = newfile.post_id)
        board = g.boards.board_ids[post.thread.board_id]
        start_response('200 OK', [('Content-Type', 'text/plain'), ('Content-Length', '2')])
        cl = int(request.environ['CONTENT_LENGTH'])
        id = request.environ['wsgi.input'].read(1)
        if id == 'S':
            headerLength = int(request.environ['wsgi.input'].read(8))
            header = request.environ['wsgi.input'].read(headerLength)

            bodyLength = int(request.environ['wsgi.input'].read(8))
            request.environ['wsgi.input'].read(2)
            body = request.environ['wsgi.input'].read(bodyLength)

            headers = header.split('&')
            ext = headers[0].split('=')[1]
            time = headers[1].split('=')[1]
            filename = "%s.%s" % (newfile.filename, ext)
            fs = FileSet(board=board, fileset=post.files)
            f = fs.add_from_data(data=body, filename=filename, binary=True)
            post.files.append(f)
            post.error = []
            meta.Session.commit()
        return ['ok']
            
        
    def text(self, file_id, post_id, edit=False):
        c.post = post = Post.get(post_id = post_id)
        if post:
            c.file = f = File.get(file_id = file_id)
            if f:
                c.pageinfo.title = f.filename
                fp = g.fs.local(f.path)
                meta = f.get_metadata()
                lexer = get_lexer_by_name(meta['type'].lower())
                c.type = meta['type'].lower()
                c.edit = edit
                formatter = HtmlFormatter(linenos='table', encoding="", outencoding="")
                c.text = text = open(fp, 'r').read()
                c.text_html = highlight(text.decode('utf8'), lexer, formatter)
                return render('/utils/text.mako')

    def text_save(self, file_id, post_id):
        c.post = post = Post.get(post_id = post_id)
        if post:
            if post.thread.board_id in g.boards.board_ids:
                c.board = board = g.boards.board_ids[post.thread.board_id]
                c.file = f = File.get(file_id = file_id)
                if f:
                    fs = FileSet(board=board)
                    f2 = fs.add_from_data(data=request.POST.get('code', None), filename=f.filename)
                    if f2 and f2.id:
                        # Generate unified diff
                        sp = subprocess.Popen("diff -u %s %s" % (h.static_local(f.path), h.static_local(f2.path)), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        r = sp.stdout.read()
                        e = sp.stderr.read()
                        if not e and r:
                            r = unicode(r, 'utf-8')
                            diff_lines = r.split('\n')
                            diff = "\n".join(['diff -urN %s %s' % (f.path, f2.path), '--- %s' % f.path, '+++ %s' % f2.path] + diff_lines[2:])
                            diff_filename = "%s%s%sr.patch" % (f.filename, f.get_suffix(), f2.get_suffix())
                            diff_file = fs.add_from_data(data=diff, filename=diff_filename)
                        # Save result
                        ip = request.headers.get("X-Real-IP", request.environ["REMOTE_ADDR"])
                        admin = session.get('admin', None)
                        password = request.POST.get('password', u'')
                        session_id = session.id
                        post = board.empty_post(thread_id=post.thread.display_id, fileset=fs, password=password, admin=admin, ip=ip, session_id=session_id)
                        if post:
                            if not session.get('posts', False):
                                session['posts'] = {}
                            session['posts'][post.post_id] = board.board
                            session.save()                          
                            return redirect(url('post_error', post_id=post.post_id))

    def archive(self, file_id, post_id):
        c.post = post = Post.get(post_id = post_id)
        if post:
            if post.thread.board_id in g.boards.board_ids:
                c.board = board = g.boards.board_ids[post.thread.board_id]
                c.file = f = File.get(file_id = file_id)
                if f:
                    c.pageinfo.title = f.filename
                    fp = g.fs.local(f.path)
                    c.meta = meta = f.get_metadata()
                    c.type = meta['type'].lower()
                    c.files = files = meta['files']
                    return render('/utils/archive.mako')

    @render_view
    @Post.fetcher    
    def post_history(self, post, board):
        if (not (c.admin and c.admin.has_permission('edit_posts', board.id)) and
            not (post.session_id == session.id)):
            return error_temporary_restricted_to_author
        revisions = post.get_revisions()
        if not revisions:
            return error_element_not_found
        return PostRevisionsView(post, revisions)
