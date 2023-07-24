# -*- coding: utf-8 -*-
<%inherit file="/header.mako" />
<div class="file-info"><a href="${h.static(c.file.path)}">${c.file.filename}</a>: ${c.file.show_metadata()}</div>
<pre id="archive_view">
%for filename in c.files:
${filename}
%endfor
</pre>
