# -*- coding: utf-8 -*-
<%inherit file="/main.mako" />

<div class="postarea">
  <h2>${_('Admin login')}</h2>
  <form id="postform" action="${h.url('login')}" method="post">
  <div>
    <label for="login">${_('Login')}</label>
    <input id="login" name="login" type="text" />
  </div>
  <div>
    <label for="password">${_('Password')}</label>
    <input id="password" name="password" type="password" />
  </div>
  <div><input type="submit" value="${_('Log in')}"/></div>
  </form>
</div>
