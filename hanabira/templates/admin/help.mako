# -*- coding: utf-8 -*-
<%inherit file="admin.mako" />
${_('Help')}
<ul>
<li><a href="${h.url('help_new')}">${_('New')}</a></li>
%for a in c.articles:
<li><a href="${h.url('help_edit', help_id=a.help_id)}">[${a.handle} ${a.language}] '${a.title}'</a></li>
%endfor
</ul>
