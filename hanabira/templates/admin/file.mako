# -*- coding: utf-8 -*-
<%page args="f" />
<tr height="200px">
<td width="200px">
<a href="${h.static(f.path)}"><img src="${h.static(f.thumb_path)}" width="${f.thumb_width}" height="${f.thumb_height}" /></a>
</td>
<td style="border-left: 1px #000000 solid; padding:0 0 0 5px;">
<form action="${h.url('files_edit')}" method="POST">
<input type="hidden" name="file_id" value="${f.file_id}" />
${_('File ID')}: ${f.file_id} <br/>
${_('Filename')}: ${f.filename} <br/>
${_('Filetype')}: ${f.filetype.type} <br/>
${_('Size')}: ${f.size} <br/>
${_('Extension')}: ${f.extension.ext} <br/>
${_('Rating')}: <select name="rating" onchange="$(this).parent().ajaxSubmit()"><option>${f.rating}</option><option>sfw</option><option>r-15</option><option>r-18</option><option>r-18g</option><option>illegal</option><option>unrated</option></select> <br/>
${_('Metadata')}: ${f.metainfo} <br/>
</form>
<a href="${h.url('get_posts_by_file', file_id=f.file_id)}">All posts</a><br/>
</td>
</tr>
