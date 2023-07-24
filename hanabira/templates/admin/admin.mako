# -*- coding: utf-8 -*-
<%inherit file="/main.mako" />
<table cellpadding="5" width="100%">
  <tbody>
    <tr>
      <td style="vertical-align: top;">
        <%include file="menu.mako" />
      </td>
      <td style="vertical-align: top;">
        ${next.body()}
      </td>
    </tr>
  </tbody>
</table>