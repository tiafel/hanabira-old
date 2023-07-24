# -*- coding: utf-8 -*-
<%inherit file="/header.mako" />
%if str(app_globals.settings.chan.logo):
<div class="logo">
  <img src="${h.static(str(app_globals.settings.chan.logo))}" title="${app_globals.settings.chan.title}" alt="${app_globals.settings.chan.title}" />
</div>
%else:
<%include file="/logo.mako" />
%endif
<hr />
%for section in app_globals.sections:
  %if c.channel.id == section.channel.id:
    <table class="category" width="100%" border="0" cellspacing="0" cellpadding="0">
    <tbody>
        <tr>
            <td class="header">${section.title}</td>
        </tr>
        <tr>
            <td class="list">
                %for board in section.boards:
		%if board.check_permissions('read', c.admin):
                    <div>
                        <a href="${h.url('board', board=board.board)}" title="${board.title}" target="board">
                               /${board.board}/ &mdash; ${board.title} <span id="count_${board.board}"></span>
                        </a>
		    </div>
		%endif
                %endfor
            </td>
        </tr>
    </tbody>
    </table>
  %endif
%endfor
