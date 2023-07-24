<%page args="events, admin"/>
<table style="border: 1px #000000 solid;">
<tr>
  <td>${_('Date')}</td>
  %if admin.has_permission('manage_admins'):
  <td>${_('IP')}</td>
  <td>${_('session')}</td>
  %endif
  <td>${_('Record')}</td>
</tr>
%for l in events:
<tr>
  <td>${l.date}</td>
  %if admin.has_permission('manage_admins'):
  <td>${h.whois_link(l.ip) |n}</td>
  <td><a href="${h.url('session', session_id=l.session_id)}">${l.session_id}</a></td>
  %endif
  <td>${l.get_message() |n}</td>
</tr>
%endfor
</table>
