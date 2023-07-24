# -*- coding: utf-8 -*-
<%inherit file="admin.mako" />

<div class="postarea">
  <h2>${_('Edit admin %s') % c.target_admin.login}</h2>
  <h3>${_('Account')}</h3>
  <form id="postform" action="${h.url('admins_edit', admin_id=c.target_admin.id)}" method="post">
  ${c.form.render()}
  <div><input type="submit" value="${_('Edit')}"></div>
  </form>
  <h3>${_('Keys')}</h3>
  %if c.target_admin.keys:
  %for key in c.target_admin.keys:
  ${key.key} <br/>
  %endfor
  %else:
  ${_('No keys')} <br/>
  %endif
  <form method="POST" action="${h.url('admins_key_add', admin_id=c.target_admin.id)}" onsubmit="$(this).ajaxSubmit(); return false;">
  <input type='submit' value="${_('Add')}" /></form>
  <h3>${_('Permissions')}</h3>
  %for p in c.target_admin.permissions:
       <span class="permission${p.scope and '' or '_global'}">${h.board_name(p.scope)} ${p.name}</span>
       [<a href="${h.url('admins_permission_del', admin_id=c.target_admin.id, permission_id=p.id)}">${_('Delete')}</a>]<br />
  %endfor
  <form action="${h.url('admins_permission_add', admin_id=c.target_admin.id)}" method="post">
  ${_('Permission')}
  <select name="permission">
  %for p in c.permissions:
       <option>${p.name}</option>
  %endfor
  </select>
  ${_('Scope')}
  <select name="scope">
  <option value="0">Global</option>
  %for b in c.boards:
      <option value="${b.board_id}">/${b.board}/</option>
  %endfor
  </select>
  <input type="submit" value="${_('Add')}">
  </form>
  <h3>${_('Effective permissions')}</h3>
  %for p in c.target_admin.global_permissions:
       <span class="permission_global">${h.board_name(0)} ${p}</span><br />
  %endfor
  %for b in c.target_admin.board_permissions:
       %for p in c.target_admin.board_permissions[b]:
       	    <span class="permission">${h.board_name(b)} ${p}</span><br />
       %endfor
  %endfor
</div>
