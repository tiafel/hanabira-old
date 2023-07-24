# -*- coding: utf-8 -*-
<%inherit file="/header.mako" />

        <%include file="menu.mako" />
        <%include file="logo.mako" />
  %if c.playlist:
	<%include file="player.mako" />
  %endif
        <hr />
        ${next.body()}
  %if not c.mini:
        <%include file="menu.mako" />
        <%include file="footer.mako" />
  %endif
