# -*- coding: utf-8 -*-
<%inherit file="admin.mako" />
${_('Admins')}
<table class="hlTable">
<tr>
<td width="10%" align="center">Login</td>
<td width="10%" align="center">Email</td>
<td width="10%" align="center">Enabled</td>
<td>Permissions</td>
</tr>
%for a in c.admins:
    <tr ${(a.id == c.admin.id) and "class='highlight'" or ""}>
        <td><a href='${h.url('admins_edit', admin_id=a.id)}'>${a.login}</a></td>
	<td>${a.email}</td>
	<td>${a.enabled}</td>
	<td>
	%for p in a.permissions:
	     <span class="permission${p.scope and '' or '_global'}">${h.board_name(p.scope)} ${p.name}</span>
	%endfor
	</td>
    </tr>
%endfor
</table>
