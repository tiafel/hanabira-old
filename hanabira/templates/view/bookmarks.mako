# -*- coding: utf-8 -*-
<%inherit file="/main.mako" />
<table class="threadlist" style="text-align:left">
%if c.bookmarks_data:
    %for board, threads in c.bookmarks_data:
        <tr class="logo"><td style="font-size:.8em"><a href="${h.url('board', board=board.board)}">/${board.board}/</a> — ${board.title}:</td></tr>
        %for thread, last_visit in threads:
        <tr class="highlight">
            <td>
                <a href="${h.url('thread', board=board.board, thread_id=thread.display_id)}" onmouseover="ShowRefPost(event,${"'{0.board}', {1.display_id}, {1.display_id}".format(board, thread)})">&gt;&gt;${thread.display_id}</a>
                %if thread.archived:
                <img src="/images/archive.gif" alt="${_('Archived')}" title="${_('Archived')}" />
                %endif
                %if thread.autosage:
                <img src="/images/autosage.gif" alt="${_('Autosage')}" title="${_('Autosage')}" />
                %endif
		${thread.title}
                [<a onclick="unsign_thread(event, ${"'{0.board}', {1.display_id}".format(board, thread)})">${_('Unsubscribe')}</a>]
		<br />
                %if thread.posts_count > 1:
                ${h.ugt("%s reply", "%s replies", thread.posts_count - 1)},
		%if last_visit < thread.last_modified:
		<b>${_(' has new changes since last visit,')}</b>
             	%else:
		${_('no changes, ')}
		%endif
                ${_('last change')}: ${h.show_time(thread.last_modified, c)}
                %else:
                ${_('No replies.')}
                %endif
	    </td>
	</tr>
        %endfor
    %endfor
%else:
    ${_('There is nothing here!')}
%endif
</td></tr></table>
<hr/>
<br class="clear" />
