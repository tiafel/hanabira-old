# -*- coding: utf-8 -*-
<%inherit file="admin.mako" />

<div class="postarea">
  <h2>${_('Profile')}</h2>
  <form id="postform" action="${h.url('profile')}" method="post">
  ${c.form.render()}
  <div><input type="submit" value="${_('Change')}"></div>
  </form>
</div>
