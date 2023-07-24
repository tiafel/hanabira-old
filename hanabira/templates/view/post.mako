# -*- coding: utf-8 -*-
<%page args="board, thread, post, need_wrap=False"/>
%if need_wrap:
    %if post.op:
  <div id="post_${post.display_id}" class="oppost post">
    %else:
  <table id="post_${post.display_id}" class="replypost post"><tbody><tr>
  <td class="doubledash">&gt;&gt;</td>
  <td class="reply" id="reply${post.display_id}">
    %endif
%endif
    <a name="i${post.display_id}"></a>
    <label${c.can_edit_posts and h.userpan(post, thread) or '' |n}>
%if not thread.archived:
    %if post.op:
        ${h.button('hide', 'Hide', "hide_thread(event, '%s',%s);"%(board.board, thread.display_id), h.url('hide_thread', board=board.board, thread_id=thread.display_id, format='redir')) |n}
    %endif
    %if c.mini:
        <input type="checkbox" name="${post.display_id}" value="${post.thread_id}" id="delbox_${post.display_id}" />
    %else:
        ${h.button('delete', 'Mark to delete', alt='Delete', insert='<input type="checkbox" name="%s" value="%s" class="delete_checkbox" id="delbox_%s" />'%(post.display_id, post.thread_id, post.display_id)) |n}
    %endif
%else:
        &nbsp;&nbsp;&nbsp;
%endif
%if post.op:
    %if c.bookmarks and c.bookmarks.is_faved(thread.id):
        ${h.button('signed', 'Unsubscribe', "unsign_thread(event, '%s',%s);"%(board.board, thread.display_id)) |n}
    %else:
        ${h.button('unsigned', 'Subscribe', "sign_thread(event, '%s',%s);"%(board.board, thread.display_id)) |n}
    %endif
     ## Припилить вместе с готовым фреймом и иконками
     ##   ${h.button('update', 'Update', "UpdateThread(event,%s,'%s',%s,%s);"%(int(c.reply), board.board, thread.display_id, thread.posts[-1].display_id)) |n}
%endif
%if board.show_hash:
        <span class="iphash">${h.make_ip_hash(thread.id, post.session_id) |n}</span>
%endif
%if board.show_geo:
        ${h.geoip(post.geoip) |n}
%endif
%if post.subject:
        <span class="replytitle">${post.subject}</span>
%endif
%if post.name:
        <span class="postername">${post.name}</span>
%endif
%if post.tripcode:
        <span class="postertrip">${board.restrict_trip and ' ' or h.tripcode(post.tripcode)}</span>
%endif
%if post.op:
    %if thread.archived:
	<img src="/images/archive.gif" alt="${_('Archived')}" title="${_('Archived')}" />
    %endif
    %if thread.autosage:
	<img src="/images/autosage.gif" alt="${_('Autosage')}" title="${_('Autosage')}" />
    %endif
    %if thread.locked:
	<img src="/images/locked.png" alt="${_('Locked')}" title="${_('Locked')}" />
    %endif
    %if thread.sticky:
	<img src="/images/sticky.png" alt="${_('Sticky')}" title="${_('Sticky')}" />
    %endif
%endif
%if c.can_see_invisible and (post.op and thread.invisible or post.invisible):
	<img src="/images/banned.png" alt="${_('Invisible')}" ${post.inv_reason and 'title="%s"'%u', '.join(post.inv_reason) or '' |n} />
%endif
        ${h.show_time(post.date, c)}
    </label>
    <span class="reflink">
    %if c.reply_button or c.nopostform or thread.archived or c.search or thread.locked:
    <a ${h.reflink(board.board, thread.display_id, post, c.reply) |n}>
    %else:
    <a onclick="GetReplyForm(event, '${board.board}', ${thread.display_id}, ${post.display_id})" title="${_('Reply')}">
    %endif
    No.${post.display_id}</a></span>
%if (c.reply_button and not (thread.archived or c.search or thread.locked)) or not c.reply and post.op:
    <span class="cpanel">
  %if c.reply_button and not (thread.archived or c.search or thread.locked):
      ${h.button('reply_', 'Reply', "GetReplyForm(event, '%s', %s, %s)"%(board.board, thread.display_id, post.display_id), double=True) |n}
  %endif
  %if not c.reply and post.op:
      [<a href="${h.url('thread', board=board.board, thread_id=thread.display_id)}">${_('Full thread')}</a>]
  %endif
    </span>
%endif
    <br />
    ## Files block
    %for file in post.files:
        %if post.files_qty > 1:
    <div id="file_${post.display_id}_${file.id}" class="file">
        %endif
        <div class="fileinfo${post.files_qty>1 and ' limited' or ''}"${c.can_view_files and h.filepan(post.files, file.id) or '' |n}>
        %if not file.rating == 'illegal' and not c.mini:
            ${_('File:')} <a href="${h.static(file.path)}" target="_blank">${board.keep_filenames and (post.files_qty > 1 and h.cut_filename(file.filename) or file.filename) or file.timestamp}</a>
             <br />
        %endif
             <em>${file.show_metadata() | n}</em>
	%if h.acceptable_censorship(file, c.rating, c.rating_strict):
        %if post.files_qty == 1 and not c.mini:
            ${file.get_superscription()}
        %endif
        %if file.has_actions():
            %if not c.mini:
	     <br />
            %endif
            %for action in file.get_actions(post):
                %if 'class' in action:
		${h.button(action['class'], action['action'], action.get('click'), action.get('url'), new_tab=action.get('new_tab', False)) |n}
                %else:
		<a ${'url' in action and 'href="%s"'%action['url'] or 'onclick="%s"'%action['click'] |n} title="${action['action']}">${action['action']}</a>
                %endif
            %endfor
        %endif
	## File is censored, show explanation
  %elif not c.mini:
	<br/>${_('Your censorship settings forbid this file.')}
	%endif
        </div>
        %if post.files_qty == 1:
    <div id="file_${post.display_id}_${file.id}" class="file">
        %endif
  
	%if h.acceptable_censorship(file, c.rating, c.rating_strict):
      %if c.mini:
        <a href="${h.static(file.path)}" target="_blank"><img src="${h.static(file.thumb_path)}" class="thumb"  alt="${file.filename}" /></a>
      %else:
        <a href="${h.static(file.path)}" target="_blank"><img src="${h.static(file.thumb_path)}" width="${file.thumb_width}" height="${file.thumb_height}" class="thumb"  alt="${file.filename}" onclick="${file.onclick_handler(post)}" /></a>
      %endif
	%else:
      <img src="${h.static('images/%s.png' % file.rating)}" class="thumb" alt="${file.rating}"/>
	%endif
    </div>
    %endfor
    %if post.files_qty > 1:
    <br style="clear: both" />
    %endif
    ## End of files block
    ## Text block
    <div class="postbody">
%if h.has_shorted(c, post):
        ${post.message_short |n}
    </div>
    <div class="postbody alternate">
%endif
       ${post.message | n}
    </div>
    <div class="abbrev">
%if h.has_shorted(c, post):
      <span>${_('Comment is too long.')}
        <a href="${h.url('thread', board=board.board, thread_id=thread.display_id)}#i${post.display_id}" onclick="GetFullText(event);">${_('Full version')}</a>.
      </span>
%endif
%if post.deleted:
      ${_("Post was deleted by %s at %s") % (post.deleter, post.deletion_time)}
%endif
%if post.last_modified:
    ${_("Post was modified last time at <a href='%s'>%s</a>") % (
    h.url('post_history', post_id=post.id),
    post.last_modified) |n}
%endif
%if post.op:
  %if c.expanded:
      <span>
        ${_("Thread is expanded.")}
        <a onclick="Truncate(event, ${thread.display_id})">${_('Truncate')}</a>.
      </span>
  %elif thread.omitted:
      <span>
        ${h.ugt("%s post is omitted", "%s posts are omitted", thread.omitted) + (thread.omitted_files and _(", %s of them with files.")%thread.omitted_files or '.')}
        <a href="${h.url('thread', board=board.board, thread_id=thread.display_id)}" onclick="ExpandThread(event, '${board.board}', ${thread.display_id})">${_('Expand thread')}</a>.
      </span>
  %endif
  %if thread.op_deleted and not c.deleted:
      <span><a href="${h.url('deleted_posts', board=board.board, thread_id=thread.display_id)}">${h.ugt("%s post is deleted by OP", "%s posts are deleted by OP", thread.op_deleted)}</a></span>
  %endif
%endif
    </div>
    ## End of text block
    %if c.get_reflink and c.board.allowed_new_files:
			<div id="reply-file_new" style="display:none">
			  <select name="new_file_type">
		    %for ft in c.board.allowed_new_files:
			    <option>${ft}</option>
		    %endfor
			  </select>
			  <input type="submit" name="new_file" value="${_('Add new file')}" />
			</div>
		%endif
%if need_wrap:
    %if post.op:
  </div>
    %else:
  </td></tr></tbody></table>
    %endif
%endif
