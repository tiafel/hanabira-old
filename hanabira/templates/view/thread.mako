# -*- coding: utf-8 -*-
<%page args="thread, board"/>
  <div class="thread" id="thread_${thread.display_id}">
%if not thread.is_censored(c.session):
<%include file="thread_expansion.mako" args="board=board, thread=thread" />
%else:
  <%
  post = thread.posts[0]
  %>
  <div id="post_${post.display_id}" class="oppost post">
  <a name="i${post.display_id}"></a>
  <label${c.can_edit_posts and h.userpan(post, thread) or '' |n}>
  &nbsp;&nbsp;&nbsp;
%if post.subject:
        <span class="replytitle">${post.subject}</span>
%endif
%if post.name:
        <span class="postername">${post.name}</span>
%endif
    %if thread.archived:
	<img src="/images/archive.gif" alt="${_('Archived')}" title="${_('Archived')}" />
    %endif
    %if thread.autosage:
	<img src="/images/autosage.gif" alt="${_('Autosage')}" title="${_('Autosage')}" />
    %endif
    %if thread.locked:
	<img src="/images/locked.png" alt="${_('Locked')}" title="${_('Locked')}" />
    %endif
    %if thread.sticky:
	<img src="/images/sticky.png" alt="${_('Sticky')}" title="${_('Sticky')}" />
    %endif
    ${h.show_time(post.date, c)}
    </label>
    <span class="reflink">
    <a ${h.reflink(board.board, thread.display_id, post, c.reply) |n}>
    No.${post.display_id}</a></span>
    </span>
    <br />
    <div class="postbody">
        Доступ к данному треду ограничен.
    </div>
  </div>

%endif
  </div>
  <br clear="left" />
  <hr />
