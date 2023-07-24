# -*- coding: utf-8 -*-
<%inherit file="admin.mako" />

<div class="postarea">
  <form id="postform" method="POST">
    <table style="margin: 0 0 0 0;"><tbody>
      <tr><td colspan="2">  <h3>${_('Edit post <a href="%s">%s</a>') % (
  h.url('post_admin', post_id=c.post.post_id), c.post.post_id) |n}</h3></td></tr>
      %if c.message:
      <tr><td colspan="2"><h3>${c.message}</h3></td></tr>
      %endif
      <tr>
	<td class="postblock">${_('Name')}</td>
	<td>
	  <input type="text" name="name" size="35" value="${c.post.name}" />
	</td>
      </tr>  
      <tr>
	<td class="postblock">${_('Subject')}</td>
	<td>
	  <input type="text" name="subject" size="35" value="${c.post.subject}" />
	</td>
      </tr>  
      <tr>
	<td class="postblock">${_('Text')}</td>
	<td>
	  <textarea id="replyText" name="message" cols="60" rows="6">${c.post.message_raw}</textarea>
	</td>
      </tr>  
      <tr>
	<td class="postblock">${_('Reason')}</td>
	<td>
	  <input type="text" name="reason" size="35" value="" />
	</td>
      </tr>  
      <tr>
	<td colspan="2"><input type="submit" value="${_('Edit post')}" /></td>
      </tr>
    </tbody></table>
  </form>
</div>