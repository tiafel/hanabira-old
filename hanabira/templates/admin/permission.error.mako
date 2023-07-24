# -*- coding: utf-8 -*-
<%inherit file="admin.mako" />

<div class="error">
<h1>${_('Permissions error')}</h1>
%if c.need_global:
${_("You must have global '%s' permission to do this action.") % c.permission}
%else:
${_("You must have '%s' permission to do this action.") % c.permission}
%endif
</div>
