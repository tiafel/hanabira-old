# -*- coding: utf-8 -*-
<%inherit file="admin.mako" />

<div class="postarea">
  <h2>Featured</h2>
  <form id="postform" method="post">
  <div>Post ID<input name="post_display_id" /></div>
  <div>Thread ID<input name="thread_display_id" /></div>
  <div>Board<input name="boardname" /></div>
  <div><input type="submit" value="${_('Find')}"></div>
  </form>
</div>