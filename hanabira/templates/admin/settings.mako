# -*- coding: utf-8 -*-
<%inherit file="admin.mako" />
${_('Settings')}
<form method="POST">
<table class="hlTable">
%for s in sorted(c.settings.values(), key=lambda x:x.name):
<tr>
  <td>
    ${s.description}
  </td>
  <td>
    ${s.render() |n}
  </td>
</tr>
%endfor
<tr>
  <td colspan="2">
    <input type="submit" value="${_('Edit')}" />
  </td>
</tr>
</table>
</form>
