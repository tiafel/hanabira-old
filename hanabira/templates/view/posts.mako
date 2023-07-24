# -*- coding: utf-8 -*-
<%inherit file="/main.mako" />

%if not (c.nopostform or c.archive or c.deleted) and ((c.reply and c.board.check_permissions('new_reply', c.admin)) or (not c.reply and c.board.check_permissions('new_thread', c.admin))):
<%include file="/newpost.mako" />
<hr class="topformtr"${c.board.board in c.hideinfo and ' style="display:none"' or '' |n} />
%endif

<form id="delete_form" action="${h.url('delete', board=c.board.board)}" method="post">
%for thread in c.threads:
     <%include file="thread.mako" args="thread=thread, board=c.board" />
    %if c.scroll_to:
      <script type="text/javascript">ScrollTo(${c.scroll_to})</script>
    %endif
%endfor

%if not c.archive:
<%include file="paginator.mako" args="route='board', kwarg={'board':c.board.board}" />

<table class="userdelete">
    <tbody>
        <tr><td>
            <input type="hidden" name="task" value="delete" />
            ${_('Password')}: <input type="password" name="password" size="15" value="${c.password}" />
     ## До следжующего апдейта. Reason выпилен за ненадобностью.
     ##       [<label><input type="checkbox" name="fileonly" value="on" />${_('Only files')}</label>]
            <input value="${_('Delete post(s)')}" type="submit" />
        </td></tr>
    </tbody>
</table>
%else:
<%include file="paginator.mako" args="route='board_arch', kwarg={'board':c.board.board}" />
%endif
</form>
<%include file="/search_form.mako" />
<br class="clear" />
%if c.admin:
<div id="admin_delete_panel" style="display: none;"><span id="adp_posts_selected">Posts: 0, Threads: 0, OPs: 0</span>
<input type="button" value="${_('Move posts')}" onclick="admin_delete_move();"/> 
<input type="button" value="${_('Delete posts')}" onclick="admin_delete_delete();"/> 
<input type="button" value="${_('Un-select all')}" onclick="admin_delete_unselect();"/>
</div>
%endif
