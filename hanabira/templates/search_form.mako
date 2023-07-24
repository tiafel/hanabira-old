<form action="${h.url('search_new', ext='xhtml')}" method="post">
    <input type="text" name="query" size="20" value="${c.query}" />
    <select name="board_id">
        <option value="0">${_('All boards')}</option>
        %if c.board:
        <option value="${c.board.id}">${_('This board')}</option>
        %endif
        %for name, board in app_globals.boards.boards.items():
        %if not board.restrict_read:
        <option value="${board.id}">/${name}/</option>
        %endif
        %endfor
    </select>
    <input value="${_('Search')}" type="submit" />
</form>
