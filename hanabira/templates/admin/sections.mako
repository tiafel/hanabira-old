# -*- coding: utf-8 -*-
<%inherit file="admin.mako" />

<div class="postarea">
  %if c.section:
  <h2>${_('Edit section')}</h2>
  <form id="postform" action="${h.url('sections_edit', section_id=c.section.section_id)}" method="post">
  %else:
  <h2>${_('New section')}</h2>
  <form id="postform" action="${h.url('sections_new')}" method="post">
  %endif
  ${c.form.render()}
  %if c.section:
  <div><input type="submit" value="${_('Edit')}"></div>
  %else:
  <div><input type="submit" value="${_('Create')}"></div>
  %endif
  </form>
</div>
