# -*- coding: utf-8 -*-
<%inherit file="admin.mako" />
<script>files_max_qty=5</script>
<%include file="privacy.mako" />
%if c.post:
<table class="hlTable">
<%include file="user_actions.mako" />
</table>
<table>
<tr><td class="${c.post.op and 'oppost' or 'reply'}">
<%include file="../view/post.mako" args="board=c.board, thread=c.thread, post=c.post" />
</td></tr>
</table>
%if c.events:
<%include file="logs_list.mako" args="events=c.events, admin=c.admin"/>
%endif
%endif

