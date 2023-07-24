# -*- coding: utf-8 -*-
<%inherit file="admin.mako" />

<div class="postarea">
  %if c.board:
  <h2>${_('Edit board')}</h2>
  <form id="postform" action="${h.url('boards_edit', board_id=c.board.board_id)}" method="post">
  %else:
  <h2>${_('New board')}</h2>
  <form id="postform" action="${h.url('boards_new')}" method="post">
  %endif
  ${c.form.render()}
  %if c.board:
  <div><input type="submit" value="${_('Edit')}"></div>
  %else:
  <div><input type="submit" value="${_('Create')}"></div>
  %endif
  </form>
</div>
