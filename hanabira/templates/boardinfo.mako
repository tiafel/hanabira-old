# -*- coding: utf-8 -*-

<div class="rules">
<script type="text/javascript">
var files_max_qty = ${c.board.files_max_qty};
var upload_handler = $t()*10000;
</script>
<ul>
<li>${_('By posting you confirm that you have read and agreed with <a href="/help/tos">our ToS</a>')|n}</li>
<li>${_('You can use <a href="/help/wakabamark">wakabamark</a> in your messages')|n}</li>
%if c.board.allow_files and c.board.allowed_filetypes:
    %if c.board.require_thread_file:
<li>${_('New threads must have at least one file.')}</li>
    %endif
    %if c.board.require_post_file:
<li>${_('New replies must have at least one file.')}</li>
    %endif
    %if c.board.keep_filenames:
<li>${_('This board shows original filenames.')}</li>
    %endif
<li>${_('Allowed file types: %s') % ', '.join(c.board.allowed_filetypes)}</li>
%else:
<li>${_('Files are not allowed on this board.')}</li>
%endif
%if c.board.allow_OP_moderation:
<li>${_('OP can delete posts with OP-password.')}</li>
%endif
%if c.board.posting_interval:
<li>${_('Only one post per %s seconds is allowed') % c.board.posting_interval}</li>
%endif
<li>${_('Threads stop bumping after %s posts.') % c.board.bump_limit}</li>
<li>${_('Threads with more than %s replies can not be deleted.') % c.board.delete_thread_post_limit}</li>
  %if c.board.archive:
<li>${_('Old threads are moved to <a href="%s">archive</a> after %s pages.') % (h.url('board_arch_last', board=c.board.board), c.board.archive_pages) | n}</li>
%endif
</ul>
</div>
