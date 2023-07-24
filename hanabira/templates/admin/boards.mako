# -*- coding: utf-8 -*-
<%inherit file="admin.mako" />
${_('Sections and boards')}

<table class="hlTable">
<tr>
    <td>${_('Section')} [<a href="${h.url('sections_new')}">${_('New')}</a>]</td>
    <td>${_('Boards')} [<a href="${h.url('boards_new')}">${_('New')}</a>]</td>
</tr>
%for section in app_globals.sections:
<tr>
    <td><a href="${h.url('sections_edit', section_id=section.section_id)}">${section.title}</a></td>
    <td>
    %for board in section.boards:
    	 <a href="${h.url('boards_edit', board_id=board.board_id)}">${board.title}</a> | 
    %endfor
    </td>
</tr>
%endfor
</table>
