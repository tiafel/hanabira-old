%if 'notices' in c.viewer_session:
<div style="position:fixed; top:0; left:0;background-color: rgb(240, 224, 214); width:100%;">
%for mid, (message, level) in c.viewer_session['notices'].items():
<div id="notice_${mid}" class="notice_${level}" style="border-bottom: 3px solid; padding: 10px;">
${message |n}
<br/>
<a onclick="delete_notice(${mid});">Удалить уведомление</a>
</div>
%endfor
</div>
%endif
<div class="adminbar">
%for section in app_globals.sections:
  %if c.channel.id == section.chan_id:
     <!-- ${section.title} -->
     [
     %for board in section.boards:
     %if board.check_permissions('read', c.admin, c.channel):
        %if c.mini:
            <a href="${h.url('board', board=board.board)}">/${board.board}/</a>
        %else:
            <a href="${h.url('board', board=board.board)}" title="${board.title}">/${board.board}/</a>
        %endif
     %endif
     %endfor
     ]
  %endif
%endfor
%if c.admin:
    [ <a href="${h.url('admin')}">${_('Admin Panel')}</a> | 
      <a href="${h.url('logout')}">${_('Logout')}</a> ]
%endif
    %if c.mini:
    [  <a href="${h.url('settings')}">${_('Settings')}</a> |
      <a href="${h.url('bookmarks')}">${_('Bookmarks')}</a> ]
    %else:
    [ <a href="${h.url('frameset')}">${_('Main')}</a> | 
      <a href="${h.url('settings')}">${_('Settings')}</a> |
      <a href="${h.url('bookmarks')}">${_('Bookmarks')}</a> |
      <a onclick='toggle_music_player();'>${_('Music Player')}</a> ]
    %endif
</div>
<div class="stylebar">
    <select onchange="set_stylesheet_all($('#stylebar').val())" id="stylebar">
    %for style_name, style_css in app_globals.styles:
     <option>${style_name}</option>
    %endfor
    </select>
</div>
