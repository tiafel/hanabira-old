<%page args="referers, admin"/>
<table style="border: 1px #000000 solid;">
<tr>
  <td>${_('Date')}</td>
  <td>${_('Domain')}</td>
  <td>${_('Referer')}</td>
  <td>${_('Target')}</td>
  <td>${_('IP')}</td>
  <td>${_('Session')}</td>
  <td>${_('New')}</td>
</tr>
%for r in referers:
<tr>
  <td>${r.date}</td>
  <td>${r.domain}</td>
  <td><a href="${r.referer}">${r.referer}</a></td>
  <td>${r.target}</td>
  <td>${h.whois_link(r.ip) |n}</td>
  <td><a href="${h.url('session', session_id=r.session_id)}">${r.session_id}</a></td>
  <td>${r.session_new and _('Yes') or _('No')}</td>
</tr>
%endfor
</table>