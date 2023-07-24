# -*- coding: utf-8 -*-
"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
from routes import Mapper

def make_map(config):
    """Create, configure and return the routes Mapper"""
    map = Mapper(directory=config['pylons.paths']['controllers'],
                 always_scan=config['debug'])

    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    map.connect('post_error',     '/error/post/:post_id',             controller='view', action='post_error')
    map.connect(None, '/error/{action}/{id}', controller='error')
    map.connect(None, '/error/{action}', controller='error')

    with map.submapper(path_prefix="/admin", controller="auth") as m:
        make_auth_map(m)

    with map.submapper(path_prefix="/admin", controller="admin") as m:
        make_admin_map(m)

    map.connect('reload', '/control/reload', controller='control', action='reload')

    with map.submapper(path_prefix="/api", controller="api_data") as m:
        make_data_api(m)
    with map.submapper(path_prefix="/api", controller="api_actions") as m:
        make_actions_api(m)
    with map.submapper(path_prefix="/api/admin", controller="api_admin") as m:
        make_admin_api(m)
        
    with map.submapper(path_prefix="/search", controller="search") as m:
        make_search_map(m)    

    #Utils
    with map.submapper(path_prefix="/utils", controller="utils") as m:
        make_utils_map(m)

    # View controller top
    map.connect('settings',       '/settings',                        controller='view', action='settings')
    map.connect('bookmarks',      '/bookmarks',                       controller='view', action='bookmarks')
    map.connect('messages',       '/messages',                        controller='view', action='messages')
    map.connect('frameset',       '/',                                controller='view', action='frameset')
    map.connect(                  '/index{.format}',                  controller='view', action='frameset', format='xhtml', since='', key='', count='')
    map.connect('frame',          '/frame.xhtml',                     controller='view', action='frame')
    map.connect('main',           '/main.xhtml',                      controller='view', action='featured')
    map.connect('help',           '/help/:handle',                    controller='view', action='help')
    map.connect('help_index',     '/help',                            controller='view', action='help_index')
    
    with map.submapper(controller="actions") as m:
        make_actions_map(m)

    # View controller bottom
    map.connect('board_arch_last','/{board}/arch/last', controller='view', action='archive_last')
    map.connect('thread_arch',    '/{board}/arch/res/{thread_id:\d+}{.format}', controller='view', action='thread', format='xhtml', archive=True)
    map.connect('board_arch',     '/{board}/arch/{page}{.format}',          controller='view', action='board', page='index', format='xhtml', archive=True)
    map.connect('deleted_posts',  '/{board}/deleted/{thread_id:\d+}{.format}', controller='view', action='deleted_thread', format='xhtml')
    # WTF is this? Should be removed.
    map.connect(                  '/{board}/res/{post_id:\d+}',        controller='view', action='thread_post')
    map.connect('thread',         '/{board}/res/{thread_id:\d+}{.format}', controller='view', action='thread', format='xhtml', archive=False)
    map.connect('board',          '/{board}/{page}{.format}',          controller='view', action='board',  page='index', format='xhtml', archive=False)

    # Redirects for common bad urls
    map.redirect('/admin',         '/admin/',                   _redirect_code="301 Moved Permanently")
    map.redirect('/{board}/arch/', '/{board}/arch/index.xhtml', _redirect_code="301 Moved Permanently")
    map.redirect('/{board}/',      '/{board}/index.xhtml', _redirect_code="301 Moved Permanently")
    map.redirect('/{board}',       '/{board}/index.xhtml', _redirect_code="301 Moved Permanently")
    
    return map

############################
##        Submappers
############################
def make_admin_api(map):
    
    # Post
    map.connect('reset_name',    '/post/{post_id:\d+}/reset-name{.format}',  action='reset_name', format='json', new_format=True) 
    map.connect('delete_images', '/post/{post_id:\d+}/delete-images{.format}', action='delete_images', format='json', new_format=True)
    map.connect('api_hide_post', '/post/{post_id:\d+}/hide{.format}',        action='hide_post', format='json', new_format=True)
    map.connect('api_show_post', '/post/{post_id:\d+}/show{.format}',        action='show_post', format='json', new_format=True)
    map.connect('api_revive_post','/post/{post_id:\d+}/revive{.format}', action='revive_post', format='json', new_format=True)
    map.connect('api_delete_post','/post/{post_id:\d+}/delete{.format}', action='delete_post', format='json', new_format=True, conditions=dict(method=['POST']))
    
    # Thread
    map.connect('thread_set', '/thread/{thread_id:\d+}/set/{attr}/{value}{.format}', action='thread_set', format='json', new_format=True)
    
    # User
    map.connect('ban_user',      '/user/{post_id:\d+}/ban{.format}',   action='ban_user', format='json', new_format=True)
    map.connect('unban_user',    '/user/{post_id:\d+}/unban{.format}', action='unban_user', format='json', new_format=True)
    map.connect('warnban_user',  '/user/{post_id:\d+}/warnban{.format}',   action='warnban_user', format='json', new_format=True)

def make_data_api(map):
    map.connect(               '/thread/{thread_id:\d+}{.format}', action='thread_info')
    map.connect('thread_info', '/thread/{board}/{display_id:\d+}{.format}', action='thread_info')
    map.connect(               '/thread/{thread_id:\d+}/all{.format}', action='thread_all')
    map.connect('thread_all',  '/thread/{board}/{display_id:\d+}/all{.format}', action='thread_all')
    map.connect(               '/thread/{thread_id:\d+}/new{.format}', action='thread_new')    
    map.connect('thread_new',  '/thread/{board}/{display_id:\d+}/new{.format}', action='thread_new')    
    map.connect(               '/thread/{thread_id:\d+}/last{.format}', action='thread_last')
    map.connect('thread_last', '/thread/{board}/{display_id:\d+}/last{.format}', action='thread_last')
    map.connect('threads_api', '/threads{.format}', action="threads", new_format=True, format='json')
    
    
    map.connect('post_info',       '/post/{post_id:\d+}{.format}', action='post_info')
    map.connect(                   '/post/{board}/{display_id:\d+}{.format}', action='post_info')
    map.connect('post_info_did',   '/post/{board}/{thread_id:\d+}/{display_id:\d+}{.format}', action='post_info')
    
    map.connect('post_references', '/post/{post_id:\d+}/references{.format}', action='post_references')
    
    map.connect('stats_diff',   '/chan/stats/diff{.format}', action='chan_stats_diff', format='json')
    map.connect('banners_list', '/chan/banners{.format}', action='chan_banners_list', format='json')
    
    map.connect('user_info', '/user{.format}', action='user_info', format='json')
    
    map.connect('/playlist', action='playlist', format='json')
    
    # Deprecated
    map.connect('expand', '/thread/expand/{board}/{thread_id}{.format}', action='thread_expand', format='xhtml')
    map.connect('/thread/update/:board/:thread_id/:last_post/:reply/:format', action='thread_expand', format='html')
    map.connect('/thread/info/{board}/{display_id}.{format}', action='thread_info')
    map.connect('/thread/new/{board}/{display_id}.{format}', action='thread_new')
    map.connect('/thread/last/{board}/{display_id}.{format}', action='thread_last')    
    map.connect('reffered', '/post/ref/{board}/{thread_id}/{display_id}{.format}', action='post_info', format='xhtml')

def make_actions_api(map):
    map.connect('notice_delete', '/notice/delete/{mid}{.format}', action='notice_delete', format='json')
    
    map.connect('hide_thread', '/thread/{board}/{thread_id}/hide{.format}', action='thread_hide', format='xhtml')
    map.connect('unhide_thread', '/thread/{board}/{thread_id}/unhide{.format}', action='thread_unhide')
    map.connect('sign_thread', '/thread/{board}/{display_id}/sign{.format}', action='thread_sign')
    map.connect('unsign_thread', '/thread/{board}/{display_id}/unsign{.format}', action='thread_unsign')
    map.connect('hide_info', '/board/hide/{board}{.format}', action='hide_info', format='xhtml')
    map.connect('/playlist/add/:file_id',     action='playlist_add', format='json')
    map.connect('/playlist/remove/:file_id',  action='playlist_remove', format='json')
    map.connect('/playlist/playing/:file_id', action='playlist_playing', format='json')    

def make_auth_map(map):
    map.connect('login',    '/login',          action='login')
    map.connect('register', '/register/:code', action='register')
    map.connect('logout',   '/logout',         action='logout')    

def make_admin_map(map):
    # Admin controller
    map.connect('admin', '/', action='index')

    # Admins
    map.connect('admins',                '/admins',                          action='admins')
    map.connect('admins_edit',           '/admins/edit/:admin_id',           action='admins_edit')
    map.connect('admins_permission_add', '/admins/permission/add/:admin_id', action='admins_permission_add')
    map.connect('admins_key_add',        '/admins/key/add/:admin_id',        action='admins_key_add')
    map.connect('admins_key_del',        '/admins/key/del/:key_id',          action='admins_key_del')
    map.connect('admins_permission_del', '/admins/permission/del/:admin_id/:permission_id', action='admins_permission_del')

    # Boards and sections
    map.connect('boards',        '/boards',                    action='boards')
    map.connect('boards_edit',   '/boards/edit/{board_id}',    action='boards_edit')
    map.connect('boards_new',    '/boards/new',                action='boards_new'),
    map.connect('sections_edit', '/sections/edit/:section_id', action='sections_edit'),
    map.connect('sections_new',  '/sections/new',              action='sections_new'),

    # Files
    map.connect('files_edit', '/file/edit',             action='files_edit')
    map.connect('files_id',   '/file/id/:file_id',      action='files_by_id')
    map.connect('file_ajax',  '/file/ajax/:file_id',    action='file_ajax')
    map.connect('files_list', '/file/:filter_id/:page', action='files', filter_id='0', page='0')

    # Restrictions
    map.connect('restrictions_new',    '/restrictions/new',                    action='restrictions_new')
    map.connect('restrictions_edit',   '/restrictions/edit/:restriction_id',   action='restrictions_edit')
    map.connect('restrictions_expire', '/restrictions/expire/:restriction_id', action='restrictions_expire')
    map.connect('restrictions',        '/restrictions/:filter_id/:page',       action='restrictions', filter_id='0', page='0')

    # Help
    map.connect('help_list', '/help',               action='help')
    map.connect('help_edit', '/help/edit/:help_id', action='help_edit')
    map.connect('help_new',  '/help/new',           action='help_new')

    # Threads
    map.connect('thread_admin',       '/thread/{thread_id}{.format}',    action='get_thread', format="xhtml")
    map.connect('thread_clean',     '/thread/{thread_id}/clean',         action='thread_clean')
    map.connect('thread_merge',     '/thread/merge/:subj/:dest', action='thread_merge')
    map.connect('thread_transport', '/thread/transport/:thread_id/:board/:dest_board', action='thread_transport')
    
    # Posts
    map.connect('post_admin', '/post/{post_id:\d+}{.format}', action='get_post', format="xhtml")
    map.connect('get_post',   '/get_post/{post_id}', action='get_post')
    map.connect('post_edit', '/post/{post_id}/edit{.format}', action='post_edit')
    map.connect('get_posts_by_file', '/post/file/{file_id}', action='get_file_post')
    map.connect('post_move', '/post/move', action='move_posts')

    # Generic stuff
    map.connect('logs',           '/logs/:filter_id/:page',     action='logs_view', filter_id='0', page='0')
    map.connect('invites_new',    '/invites/new',               action='invites_new')
    map.connect('statistics',     '/statistics',                action='statistics')
    map.connect('referers',       '/referers/:filter_id/:page', action='referers', filter_id='0', page='0')
    map.connect('permissions',    '/permissions',               action='permissions')
    map.connect('admin_settings', '/settings',                  action='settings')
    map.connect('profile',        '/profile',                   action='profile')
    map.connect('featured',       '/featured',                  action='featured')
    map.connect('featured_add',   '/featured/add/:post_id',     action='featured_add')
    
    # Admin user control
    map.connect('session',   '/session/{session_id}', action='session')
    map.connect('session_recount', '/session/{session_id}/recount', action='session_recount')
    map.connect('send_notification', '/session/{session_id}/notify{.format}', action='send_notification')
    map.connect('whois',   '/whois/:ip', action='get_whois')
    map.connect('list_lastposts', '/exec/lastposts', action='list_lastposts')
    map.connect('lastposts', '/lastposts', action='lastposts')
    map.connect('userposts', '/exec/userposts', action='userposts')
    map.connect('userexec',  '/exec/user', action='userexec')

def make_search_map(map):
    map.connect('search_new',  '/index.:ext',            action='search_new', conditions=dict(method=['POST']))
    map.connect('search_form', '/index.:ext',            action='search_form')
    map.connect('search',      '/:search_id/:page.:ext', action='search', page='index', requirements=dict(search_id="\d+", page="index|\d+"))

def make_actions_map(map):
    map.connect('delete',     '/{board}/delete{.format}',            action='delete')
    map.connect('captcha',    '/captcha/{board}/{rand}.png',         action='captcha', rand=0)
    map.connect('post',       '/{board}/post/{post_id}{.format}',    action='post', post_id='new', format='xhtml')
    map.connect('reputation', '/action/reputation/{vote}/{post_id}{.format}', action='reputation')
    
def make_utils_map(map):
    map.connect('post_history', '/post/{post_id}/history{.format}', action="post_history", format="xhtml")
    map.connect('util_image_new',  '/file/new/image/:post_id',             action='image_new')
    map.connect('util_file_new',  '/file/new/:filetype/:post_id',          action='file_new')
    map.connect('util_shi_new',   '/image/shi/:file_id/:file_key',         action='image_shi')
    map.connect('util_shi_save',  '/image/shi/save/:file_id/:file_key',    action='image_shi_save')
    map.connect('util_image_edit', '/image/edit/:file_id/:post_id',        action='image_edit', new='')
    map.connect('util_image_edit_new', '/image/editnew/:file_id/:post_id', action='image_edit', new='1')
    map.connect('util_text_save', '/text/save/:file_id/:post_id',          action='text_save')
    map.connect('util_text_view', '/text/:file_id/:post_id',               action='text', edit='')
    map.connect('util_text_edit', '/text/:file_id/:post_id/edit',          action='text', edit=True)
    map.connect('util_archive_view', '/archive/:file_id/:post_id',         action='archive', )    
