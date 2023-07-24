# -*- coding: utf-8 -*-
%if c.errors:
<div class="theader">${_('There are some errors in your post.')}</div>
%endif

<div id="hideinfodiv" class="hideinfo rightaligned"${(not c.board.board in c.hideinfo) and ' style="display:none"' or '' |n}>
  [
  <a href="${h.url('hide_info', board=c.board.board, format='redir')}" onclick="${"hide_info(event, '%s')"%c.board.board}">
    ${_('Unhide form')}
  </a>
  ]
  <hr />
</div>
%if c.reply:
<div class="theader">
  ${_('Reply to thread %s.')%c.thread.display_id}
  [<a href="${h.url('board', board=c.board.board)}">${_('Back')}</a>]
</div>
%endif 
<div id="postform_placeholder">
  <div class="postarea" id="postFormDiv">
    <table>
      <tbody>
	<tr>
	  <td class="hideinfo" id="hideinfotd"${(c.board.board in c.hideinfo or c.errors) and ' style="display:none"' or '' |n}>
	    &nbsp;[<a href="${h.url('hide_info', board=c.board.board, format='redir')}" onclick="${"hide_info(event, '%s')"%c.board.board}">
	    ${_('Hide form')}
	    </a>]
	  </td>
	</tr>
	<tr class="topformtr"${c.board.board in c.hideinfo and ' style="display:none;"' or '' |n}>
	  <td>
	    <form id="postform" action="${h.url('post', board=c.board.board, post_id=(c.post and c.post.post_id or 'new'))}" method="post" enctype="multipart/form-data" >
	      <input type="hidden" name="thread_id" value="${c.thread and c.thread.display_id or 0}" />
	      <input type="hidden" name="task" value="post" />
%if c.scroll_threads and c.thread and c.thread.posts and c.thread.posts_count > 1:
        <input id="scroll_to" type="hidden" name="scroll_to" value="${c.thread.posts[-1].display_id}" />
%endif
	      <table>
		<tbody>
		  ${h.show_errors('general') | n}
		  %if c.board.allow_names:
		  ${h.show_errors('name') | n}
		  <tr id="trname">
		    <td class="postblock">${_('Name')}</td>
		    <td>
		      <input type="text" name="name" size="35" value="${h.post_name(c.board, c)}" />
		    </td>
		  </tr>
		  %endif
		  ${h.show_errors('sage') | n}
		  <tr id="trsage">
		    <td class="postblock">${_('Sage')} </td>
		    <td><input type="checkbox" name="sage" ${h.post_sage()} /></td>
		  </tr>
		  ${h.show_errors('subject') | n}
		  <tr id="trsubject">
		    <td class="postblock">${_('Subject')}</td>
		    <td>
		      <input type="text" name="subject" size="35" maxlength="64" value="${h.post_value('subject')}" />
		      <input type="submit" name="new_post" value="${_('Post')}" />
		    </td>
		  </tr>
		  ${h.show_errors('message') | n}
		  <tr id="trmessage">
		    <td class="postblock">${_('Text')}</td>
		    <td><textarea id="replyText" name="message" cols="60" rows="6">${h.post_message()}</textarea></td>
		  </tr>
		  ${h.show_errors('captcha') | n}
		  <tr id="trcaptcha">
		    <td class="postblock">${_('Captcha')}</td>
		    <td>
		      <img src="${h.url('captcha', board=c.board.board, rand=h.now())}" alt="${_('Captcha')}" id="captcha-image" onclick="reload_captcha(event);" /><br />
		      %if c.board.check_require_captcha():
		      <input id="captcha" type="text" name="captcha" size="35" onfocus="reload_captcha(event);" onkeypress="CaptchaProcess(event, '${c.language}')" />
		      %else:
		      ${_('You do not need to enter captcha.')}
		      %endif
		    </td>
		  </tr>
		  ${h.show_errors('password') | n}
		  <tr id="trrempass">
		    <td class="postblock">${_('Password')}</td>
		    <td>
		      <input type="password" name="password" size="35" value="${c.password}" />
		    </td>
		  </tr>
		  ${h.show_errors('file') | n}
		  <tr id="trfile">
		    <td class="postblock">${_('File')}</td>
		    <td id="files_parent">
		      <input id="post_files_count" type="hidden" name="post_files_count" value="${c.post and len(c.post.files) + 1 or 1}" />
		      %if c.post and c.post.files:
		      %for f in c.post.files:
		      <div id="file_${c.post.post_id}_${f.file_id}"><a href="${h.static(f.path)}">${_('File %s, %s bytes.')%(f.filename, f.size)}</a></div>
		      %endfor
		      %endif
		      %for i in range((c.post and len(c.post.files) or 0) + 1, c.board.files_max_qty + 1):
		      <div id="file_${i}_div"${i != (c.post and len(c.post.files) or 0) + 1 and ' style="display:none"' or '' |n}>
			<input id="file_${i}" onchange="update_file_fields(event, this);" type="file" name="file_${i}" size="28" /><select name="file_${i}_rating"><option>SFW</option><option>R-15</option><option>R-18</option><option>R-18G</option></select>
		      </div> 
		      %endfor
		      %if c.board.allowed_new_files:
		      <div id="file_new">
			<select name="new_file_type">
			  %for ft in c.board.allowed_new_files:
			  <option>${ft}</option>
			  %endfor
			</select>
			<input type="submit" name="new_file" value="${_('Add new file')}" />
		      </div>
		      %endif
		    </td>
		  </tr>
		  <tr id="trgetback">
		    <td class="postblock">${_('Go back to')}</td>
		    <td>
		      <select name="goto">
			<option value="board"${c.redirect == 'board' and ' selected="selected"' or '' |n}>${_('board')}</option>
			<option value="thread"${c.redirect == 'thread' and ' selected="selected"' or '' |n }>${_('thread')}</option>
			<option value="${c.pageinfo.page}"${c.redirect == 'page' and ' selected="selected"' or '' |n }>${_('page %s')%c.pageinfo.page}</option>
		      </select>
		    </td>
		  </tr>
		</tbody>
	      </table>
	    </form>
	  </td>
	</tr>
	<tr class="topformtr"${c.board.board in c.hideinfo and ' style="display:none;"' or '' |n}>
	  <td>
	    <%include file="/boardinfo.mako" />
	  </td>
	</tr>
      </tbody>
    </table>
  </div>
</div>
