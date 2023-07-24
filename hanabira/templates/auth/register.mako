# -*- coding: utf-8 -*-
<%inherit file="/main.mako" />

<div class="postarea">
  <h2>${_('New account')}</h2>
  <form id="postform" action="${h.url('register', code='doesntmatteranymore')}" method="post">
  ${c.form.render()}
  <div><input type="submit" value="Create"></div>
  </form>
</div>
