# -*- coding: utf-8 -*-
<%inherit file="admin.mako" />

%if c.invite:
<div class="postarea">
<textarea cols="60" rows="5" readonly="readonly" >
${h.url('register', code=c.invite.invite)}
</textarea>
</div>
%else:
<div class="postarea">
    <form id="invite-form" method="post" action="${h.url('invites_new')}">
<table>
    <tr>
        <td>${_('Reason:')}</td>
        <td><input type='text' name='reason' /></td>
    </tr>
    <tr>
        <td>&nbsp;</td>
        <td><input type='submit' value='${_('Make invite')}' /></td>
    </tr>
</table>
    </form>
</div>
%endif
