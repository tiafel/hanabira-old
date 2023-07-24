# -*- coding: utf-8 -*-
<%inherit file="admin.mako" />
<script>files_max_qty=5</script>
<%include file="privacy.mako" />
%if c.thread:
<table class="hlTable">
<%include file="user_actions.mako" />
<tr><td class="postblock logo" style="font-size:1em;" colspan="6">thread</td></tr>
<tr><td colspan="6">
    [<a onclick="$.get('/admin/thread/clean/${c.thread.id}')">Clean invisible posts</a>]
    [<a onclick="prepare_merge(event, ${c.thread.id}, '${c.board.board}')">Merge</a>]
    [<a onclick="prepare_transport(event, ${c.thread.id}, '${c.board.board}')">Transport</a>]
    [<a onclick="$.get('/admin/thread/autosage/${c.thread.id}')">Autosage</a>]
    %if not c.thread.sticky:
    [<a onclick="$.get('/admin/thread/archived/${c.thread.id}')">Archive</a>]
    %endif
    %if not c.thread.archived:
    [<a onclick="$.get('/admin/thread/sticky/${c.thread.id}')">Stick</a>]
    %endif
    [<a onclick="$.get('/admin/thread/locked/${c.thread.id}')">Lock</a>]
    [<a onclick="$.post('${h.url('restrictions_new')}', {type:'thread',effect:'premod',value:${c.thread.id}})">Set premod</a>]
    [<a onclick="$.post('/${c.board.board}/delete', {task:'delete',${c.thread.display_id}:${c.thread.id}})">Delete</a>]
</td></tr>
</table>
<table>
<tr><td class="oppost">
<%include file="../view/post.mako" args="board=c.board, thread=c.thread, post=c.post" />
</td></tr>
</table>
%if c.events:
<%include file="logs_list.mako" args="events=c.events, admin=c.admin"/>
%endif
%endif
