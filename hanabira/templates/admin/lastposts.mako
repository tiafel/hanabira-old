# -*- coding: utf-8 -*-
<%inherit file="admin.mako" />
<form action="/admin/exec/lastposts" method="post">List posts for last <input type="text" name="time" value="1"/> hours.<br>
<ul>
<li>
<select name="board">
   <option value="0">${_('All boards')}</option>
   %for id, board in sorted(app_globals.boards.board_ids.items()):
   ##%if not board.restrict_read:
   <option value="${id}">/${board.board}/</option>
   ##%endif
   %endfor
</select>
%if c.can_see_invisible:
<li><input type="checkbox" name="inv" checked="true"/> ${_('Only invisible')}</li>
<li><input type="checkbox" name="exclude_api" checked="true"/> ${_('Exclude API invisible')}</li>
%endif
<li><input type="checkbox" name="op"/> ${_('Only OP-posts')}</li>
<li><input type="checkbox" name="files"/> ${_('Only with files')}</li>
<li><input type="checkbox" name="sage"/> ${_('Only with sage')}</li>
</ul>
<br><input type="submit" value="List"/></form>
