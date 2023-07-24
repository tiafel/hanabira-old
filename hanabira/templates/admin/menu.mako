%if c.admin.has_permission('view_admins'):
<a href="${h.url('admins')}">${_('Admins')}</a><br />
%endif
%if c.admin.get_permission('boards'):
<a href="${h.url('boards')}">${_('Boards')}</a><br />
%endif
%if c.admin.get_permission('view_log'):
<a href="${h.url('logs')}">${_('Logs')}</a><br />
%endif
%if c.admin.has_permission('invites'):
<a href="${h.url('invites_new')}">${_('Invites')}</a><br />
%endif
%if c.admin.get_permission('statistics'):
<a href="${h.url('statistics')}">${_('Statistics')}</a><br />
%endif
%if c.admin.has_permission('referers'):
<a href="${h.url('referers')}">${_('Referers')}</a><br />
%endif
%if c.admin.has_permission('permissions'):
<a href="${h.url('permissions')}">${_('Permissions')}</a><br />
%endif
%if c.admin.has_permission('settings'):
<a href="${h.url('edit_settings')}">${_('Settings')}</a><br />
%endif
%if c.admin.get_permission('restrictions'):
<a href="${h.url('restrictions')}">${_('Restrictions')}</a><br />
%endif
%if c.admin.get_permission('see_invisible'):
<a href="${h.url('lastposts')}">${_('Last posts')}</a><br />
%endif
%if c.admin.has_permission('files'):
<a href="${h.url('files_list')}">${_('Files')}</a><br />
%endif
%if c.admin.has_permission('help'):
<a href="${h.url('help_list')}">${_('Help')}</a><br />
%endif
<a href="${h.url('profile')}">${_('Profile')}</a><br />
