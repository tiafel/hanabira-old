<!-- Not valid XHTML, should be used for AJAX only. Each post is encapsulated in additional div, strip it down prior to insertion in the page -->
%for post in c.thread.posts:
<div class="api-post-container" id="post-${post.display_id}">
<%include file="../view/post.mako" args="board=c.board, thread=c.thread, post=post" />
</div>
%endfor
