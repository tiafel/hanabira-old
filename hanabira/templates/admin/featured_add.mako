# -*- coding: utf-8 -*-
<%inherit file="admin.mako" />

<div class="postarea">
  <h2>Featured Add</h2>
  <form id="postform" method="post">
  <div>${c.post.message_raw}</div>
  <div>Description<input name="description" /></div>
  <div>Show file<input name="show_file" type="checkbox" /></div>
  <div>Show text<input name="show_text" type="checkbox" /></div>
  <div><input type="submit" value="${_('Add')}"></div>
  <div>
    %for img in c.post.files:
    <img src="/${img.thumb_path}" />
    %endfor
  </div>
  </form>
</div>