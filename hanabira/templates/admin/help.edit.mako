# -*- coding: utf-8 -*-
<%inherit file="admin.mako" />

<div class="postarea">
  %if c.article:
  <h2>${_('Edit article')}</h2>
  <form id="postform" action="${h.url('help_edit', help_id=c.article.help_id)}" method="post">
  %else:
  <h2>${_('New article')}</h2>
  <form id="postform" action="${h.url('help_new')}" method="post">
  %endif
  ${c.form.render()}
  %if c.article:
  <div><input type="submit" value="${_('Edit')}"></div>
  %else:
  <div><input type="submit" value="${_('Create')}"></div>
  %endif
  </form>
</div>
<script>
$.browser.safari || $('textarea').keypress(AutoResize).keyup(AutoResize);
</script>
