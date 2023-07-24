# -*- coding: utf-8 -*-
<%inherit file="/header.mako" />
<h3>${_('Post %s revisions') % c.post.display_id}</h3>
<div id="revisions">
<table class="revision-table"><tbody>
%for revision in c.revisions:
   <tr class="revision-header-row">
      <td class="revision-header-index">${revision.index}</td>
      <td>${revision.reason}</td>
      <td>${_("Created by %s at %s") % (revision.changed_by, revision.date)}</td>
   </tr>
   <tr class="revision-content-row" id="revision-${revision.index}-content">
      <td colspan="3">
      %if revision.diff:
         ${revision.diff|n}
      %else:
         ${revision.message_html|n}
      %endif
      </td>
   </tr>
%endfor 
</tbody></table>
</div>