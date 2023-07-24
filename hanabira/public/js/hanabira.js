var Hanabira = {
      ExpImgs : {},
      ExpThreads : {},
      ReplyForm : null,
      LastReply : null,
      Refs : {},
      zIndex : 0,
      LoadedPosts : {},
      Highlighted : [],
      TextSize : 1.62
    };
function UploadProgress(e, obj)
{
    if ($('#post_files_count', obj).val() == 1)
	return true;

    if (obj.action.indexOf('X-Progress-ID') < 0)
    {
	var frame = $('<iframe id="uploadframe" name="uploadframe" width="0" height="0" frameborder="0" border="0" src="about:blank"></iframe>');
	var bar = $('<span class="uploadprogress" id="uploadprogress" style="display:none">0</span>');
	$('#files_parent', obj).append(frame);
	$('#files_parent', obj).append(bar);
	obj.action = obj.action + "?X-Progress-ID=" + upload_handler;
	obj.target = "uploadframe";
    }
    var upload_progress_timer = null;
    var upload_progress_count = 0;
    var stop_upload_progress = 0;
    var msg = null;  
    var bar = $('#uploadprogress', obj);
    var frame = $('#uploadframe')
    update = function() {
	$.ajax({
	    url: '/uploads/stats?rand='+upload_progress_count+++'&X-Progress-ID='+upload_handler,
	    dataType: 'json',
	    timeout: 1000,
	    success: function(response) 
	    {
		if (!(response.received && response.size) && response.status)
		{
		    clearInterval(upload_progress_timer);
		    stop_upload_progress = 1;
		}
		if (!stop_upload_progress)
		    bar.progressBar(response.received, {max: response.size, textFormat: 'fraction'})
		if (response.received == response.size)
		{
		    clearInterval(upload_progress_timer);
		    stop_upload_progress = 1;
		}
	    },
	    error: function (xhr, ts, et) 
	    {
		if (ts != 'timeout') 
		{
		    clearInterval(upload_progress_timer);
		    stop_upload_progress = 1;
		}
	    }
	})
    }
    //  if (!($.browser.mozilla))
    upload_progress_timer = window.setInterval(update, 1000);
    bar.progressBar({max: 0, textFormat: 'fraction'});
    bar.fadeIn();
}    
function reputation_action(e, obj)
{
    var url = obj.href;
    var span = obj.parentNode;
    $.ajax({url: url,
	    dataType: 'json',
	    success: function(response)
	    {
		$(span).find('a').remove();
		if (response.status == 'ok')
		{
		    $(span).find('img')[0].nextSibling.data = " " + response.reputation;
		    if (response.reputation >= 0)
		    {
			$(span).removeClass('reputation-negative').addClass('reputation-positive');
		    }
		    else
		    {
			$(span).removeClass('reputation-positive').addClass('reputation-negative');
		    }
		}
	    }
	   });
    return false;
}
function reputation_show_post(e, obj)
{
    var parent = obj.parentNode.parentNode;
    $(parent).find("div").show();
    $(obj).remove();
    return false;
}
function expand_image(e, width, height)
{
  var img = $(e.target);
  var imgSrc = img.parent().attr('href');
  var expImg = Hanabira.ExpImgs[imgSrc];
  if (expImg)
  {
	  img.attr('src', expImg.src);
  	img.attr('width', expImg.width);
	  img.attr('height', expImg.height);
	  img.css('border', 'none').css('float', 'none');
	  delete Hanabira.ExpImgs[imgSrc];
  }
  else
  {
	  Hanabira.ExpImgs[imgSrc] = {
            'src'     : img.attr('src'),
            'width'  : img.attr('width'),
            'height' : img.attr('height')
	  };
    
    var newWidth	  = width;
    var newHeight	= height;
    var ratio = newWidth/newHeight;
    var img_container = img.closest('.post');
    if (img_container.length == 0)
        img_container = img.closest('.popup');
    if (img_container.length == 0)
        img_container = img.closest('table');	
    var maxWidth = $(window).width() - $('.file:first', img_container).offset().left;
    if (maxWidth < newWidth)
    {
        newWidth = maxWidth;
        newHeight = newWidth/ratio;
    }
    img.attr('width', newWidth).attr('height', newHeight).attr('src', imgSrc);
    img.css('float', 'left').css('border', '2px dashed #FFBB00').one('load', function() {
        img.css('border', 'none');
    }).one('error', function() {
        img.unbind('load');
        img.css('borderColor', '#FF0000');
    });
  }
  e.preventDefault();
}
ExpandAll = function(event, thread)
{
  $('.thumb', thread ? $('#thread_'+thread) : SelectThread(event)).click();
}
function code_view()
{
    if (edit)
    {
	edit = false;
	$("#code_edit").hide()
	$("#code_view").show()
    }
}
function code_edit()
{
    if (!edit || !loaded)
    {
	if (!loaded)
	{
	    eaload();
	    loaded = true;
	}
	edit = true;
	$("#code_view").hide()
	$("#code_edit").show()
    }
}
function code_edit_simple()
{
    if (!edit || loaded)
    {
	edit = true;
	if (loaded)
	{
	    loaded = false;
	    editAreaLoader.delete_instance("code_edit_ta");
	}
	$("#code_view").hide()
	$("#code_edit").show()
    }
}
function switch_row(id)
{
	obj = document.getElementById(id).style;
	tmp = (obj.display == 'none')?'block':'none';
	obj.display = tmp;
	return false;
}

function reload_captcha(e)
{
  var capt = e.target;
  if (capt.nodeName.toLowerCase() == 'input')
    capt = $('img', capt.parentNode)[0];
  Refresh(capt);
}
function update_file_fields(event, obj)
{
    var parent = $(obj.parentNode.parentNode);
    var fields = parent.find('div:visible').not('div[id$=file_new]').find('input');
    var th = [];
    var nf = 1;
    
    for (var i=0; i < fields.length; i++)
    {
      if (fields[i].value)
        nf++;
    }
    nf += parent.find('a').length
    
    if (nf <= files_max_qty)
      parent.find("#file_"+nf+"_div").show();
      
    parent.find("#post_files_count").val(nf);
}


function update_board_stats()
{
  setTimeout(update_board_stats, 30000);
  if ($t(get_settings(1)) < 29900)
    return;
  set_settings($t(), 1);
  $.get('/api/chan/stats/diff.json', {}, function(data) {for (b in data)
    {
      var bcs = document.getElementById('count_'+b);
      if (bcs)
        $(bcs).html('['+data[b]+']');
    } },'json');
}
function sign_thread(event, board, thread)
{
  $.get('/api/thread/'+board+'/'+thread+'/sign.json', {}, function(res) {
    var button = $(event.target).parent();
    button.attr('class', 'signed icon').attr('onclick', 'un'+button.attr('onclick'));
  });
  event.preventDefault();
}
function unsign_thread(event, board, thread)
{
  $.get('/api/thread/'+board+'/'+thread+'/unsign.json', {}, function(res) {
    var button = $(event.target).parent();
    if (button.hasClass('signed'))
      button.attr('class', 'unsigned icon').attr('onclick', button.attr('onclick').slice(2));
  });
  event.preventDefault();
}
function unhide_thread(event, board, thread)
{
  $.get('/api/thread/'+board+'/'+thread+'/unhide.json', {}, function(res) {$(event.target).parent().remove()});
}
function hide_thread(event, board, thread)
{
  if (confirm("Скрываем?"))
    $.get('/api/thread/'+board+'/'+thread+'/hide.json', {}, function(response){$('#thread_'+thread).hide("slow")});
  event.preventDefault();
}
function hide_info(event, board)
{
  var topform = $('.topformtr');
  if (topform.css('display') == 'none')
  {
    topform.show(200);
    $("#hideinfodiv").css('display', 'none');
    $("#hideinfotd").css('display', '');
  }
	else
  {
    topform.hide(200);
    $("#hideinfodiv").css('display', '');
    $("#hideinfotd").css('display', 'none');
  }
  $.get('/api/board/hide/'+board+'.xhtml');
  event.preventDefault();
}
toLoading = function(el)
{
  return el.attr('class', 'waiting'+Math.floor(Math.random()*3)+' icon').html('<img src="/images/blank.png" />');
}
GetFullText = function(event)
{
  var a = $(event.target);
  var node = a.closest('.post');
  node.find('.postbody:first').html(node.find('.alternate').html());
  a.parent().remove();
  event.preventDefault();
} 
UpdateThread = function(event, reply_mode, board, thread, last_post)
{
  if (!board) {
    thread = SelectThread(event);
    if (thread)
      $('.update', thread).click();
    return;
  }
  $.get('/api/thread/update/'+board+'/'+thread+'/'+last_post+'/'+reply_mode+'/html', function(res) {
    $(event.target).closest('.thread').append($(res));
  });
}
ExpandThread = function(e, board, thread)
{
  e.preventDefault();
  var th = $('#thread_'+thread);
  var html = th.html();
  if (Hanabira.ExpThreads[thread])
    th.html(Hanabira.ExpThreads[thread]);
  else
  {
    $(e.target.parentNode).html(toLoading($('<span></span>')));
    $.get('/api/thread/expand/'+board+'/'+thread, function(res) {
      th.html(res);
      BindCrosses($(".delete input", th));
    });
  }
  Hanabira.ExpThreads[thread] = html;
}
Truncate = function(e, thread)
{
  var th = $('#thread_'+thread);
  var html = th.html();
  th.html(Hanabira.ExpThreads[thread]);
  Hanabira.ExpThreads[thread] = html;
}
Highlight = function(event, num, el)
{
  var hl;
  var post = $(el || "#reply"+num);
  if (post.length)
  {
    if (Hanabira.Highlighted.length)
    {
      if (Hanabira.Highlighted[0] == num)
        return;
      
      hl = Hanabira.Highlighted[1];
      hl.attr('class', 'reply');
    }
    post.attr('class', 'highlight');
    Hanabira.Highlighted = [num, post];
  }
  else if (event && document.location.href.indexOf(/[^#]+/.exec(event.target.href)) >= 0)
    event.preventDefault();
}
ClosePopup = function(pressed)
{
  if (pressed.keyCode == 27)
  {
    var node = Hanabira.Refs[Hanabira.zIndex];
    if (node && node.parentNode)
    {
      node.parentNode.removeChild(node);
      Hanabira.zIndex--;
    }
    else
    {
      while (Hanabira.zIndex && !(node && node.parentNode))
      {
        node = Hanabira.Refs[Hanabira.zIndex];
        Hanabira.zIndex--;
      }
      if (node && node.parentNode)
        node.parentNode.removeChild(node);
    }
  }
}
BindCrosses = function(arr)
{
  arr.click(function() {
    $(this.parentNode).toggleClass('checked', this.checked);
    if (typeof is_admin != "undefined" && is_admin)
    {
        admin_delete_clicked(this);
    }
  }).filter(':checked').parent().toggleClass('checked');
}
InsertInto = function(textarea, text)
{
	if(textarea.createTextRange && textarea.caretPos)
  {
    var caretPos=textarea.caretPos;
    caretPos.text=caretPos.text.charAt(caretPos.text.length-1)==" "?text+" ":text;
  }
  else if(textarea.setSelectionRange)
  {
    var start=textarea.selectionStart;
    var end=textarea.selectionEnd;
    textarea.value=textarea.value.substr(0,start)+text+textarea.value.substr(end);
    textarea.setSelectionRange(start+text.length,start+text.length);
  }
  else
    textarea.value+=text+" ";
}
GetTextFrom = function(textarea)
{
  return textarea.value.substr(textarea.selectionStart, textarea.selectionEnd);
}
QuoteSelected = function()
{
  var t = document.getElementById('reply-replyText');
	InsertInto(t, '>'+window.getSelection().toString().replace(/\n/gm, '\n>')+'\n');
  if ($.browser.mozilla || $.browser.opera)
    ResizeTextarea(t);
}
SwapLayout = function(str, lang)
{
  if (lang.indexOf('ru')>-1)
    str = str.replace(/[\-=0-9]/,'').replace(/`/, "ё").replace(/q/i, "й").replace(/w/i, "ц").replace(/e/i, "у").replace(/r/i, "к").replace(/t/i, "е").replace(/y/i, "н").replace(/u/i, "г").replace(/i/i, "ш").replace(/o/i, "щ").replace(/p/i, "з").replace(/\[/, "х").replace(/[\]\\]/, "ъ").replace(/a/i, "ф").replace(/s/i, "ы").replace(/d/i, "в").replace(/f/i, "а").replace(/g/i, "п").replace(/h/i, "р").replace(/j/i, "о").replace(/k/i, "л").replace(/l/i, "д").replace(/;/, "ж").replace(/'/, "э").replace(/z/i, "я").replace(/x/i, "ч").replace(/c/i, "с").replace(/v/i, "м").replace(/b/i, "и").replace(/n/i, "т").replace(/m/i, "ь").replace(/,/, "б").replace(/[\.\/]/, "ю");
  else if (lang.indexOf('en')>-1)
    str = str.replace(/[;\[\]',\.\/`\-=0-9ъЪЭэ]/,'').replace(/[фФ]/, "a").replace(/[иИ]/, "b").replace(/[сС]/, "c").replace(/[вВ]/, "d").replace(/[уУ]/, "e").replace(/[аА]/, "f").replace(/[пП]/, "g").replace(/[рР]/, "h").replace(/[шШ]/, "i").replace(/[оО]/, "j").replace(/[лЛ]/, "k").replace(/[дДжЖ]/, "l").replace(/[ьЬбБ]/, "m").replace(/[тТ]/, "n").replace(/[щЩ]/, "o").replace(/[зЗхХ]/, "p").replace(/[йЙ]/, "q").replace(/[кК]/, "r").replace(/[ыЫ]/, "s").replace(/[еЕ]/, "t").replace(/[гГ]/, "u").replace(/[мМ]/, "v").replace(/[цЦ]/, "w").replace(/[чЧ]/, "x").replace(/[нН]/, "y").replace(/[яЯ]/, "z");
  return str;
}
CaptchaProcess = function(event, lang)
{
  var key = event.which;  
  if (key > 38 && !event.ctrlKey)
  {
    var keychar = SwapLayout(String.fromCharCode(key), lang);
    InsertInto(event.target, keychar);
    event.preventDefault();
  }
}

ResizeTextarea = function(texta)
{    
  var height;
  var reply = $(texta);
  var line = parseInt(reply.css('line-height'));
  var fs = parseInt(reply.css('font-size'));
  if ($.browser.mozilla)
  {
    var ns = reply.val().split("\n");
    var ls = ns.length;
    $.each(ns, function() {ls += Math.floor(this.length/Math.floor(texta.scrollWidth*Hanabira.TextSize/fs))})
    height = ls*line;
  }
  else
  {
    height = texta.scrollHeight;
    line = line || fs*2/Hanabira.TextSize;
    return false;
  }
  // Что я уёбывал, когда писал всё это? Надо заказать ещё...
  
  height += (1 - height%line);
  if (height > 6*line)
    texta.style.height = (height + line)+"px";
  else
    texta.style.height = 7*line+'px';
}
AutoResize = function(event)
{
  var key = event.keyCode;
  if (key < 37 || key > 40)
  {
    var texta = event.target;
    ResizeTextarea(texta);
  }
}
ParseUrl = function(url)
{
  m = (url || document.location.href).match( /https?:\/\/([^\/]+)\/([^\/]+)\/((\d+)|res\/(\d+)|\w+)(\.x?html)?(#i?(\d+))?'/)
  return m?{host:m[1], board:m[2], page:m[4], thread:m[5], pointer:m[8]}:{};
}
ThisBoard = function(board) {return Hanabira.URL.board == board}
Refresh = function(c)
{
  c.src = c.src.split('/').slice(0,-1).join('/')+"/"+$t()+'.png';
}

GetReplyForm = function(click, board, tid, pid)
{
  if ($.browser.msie)
  {
    InsertInto($('#replyText')[0], ">>"+pid+"\n");
    return;
  }
  if (Hanabira.ready)
  {
    var op = tid == pid;
    var thisBoard = ThisBoard(board);
    if (!Hanabira.ReplyForm)
    {
      var form = $('<form id="replyform" class="reply" enctype="multipart/form-data" method="post" action="/'+board+'/post/new.xhtml" onsubmit="UploadProgress(event, this);"></form>').append('<input type="hidden" name="thread_id" value="'+tid+'" />\n<input type="hidden" name="task" value="post" />\n');
      var scroll_to = $('#scroll_to')[0];
      var scroll_input = $('<input id="reply-scroll_to" type="hidden" name="scroll_to" />\n');
      form.append(scroll_input);
      if (scroll_to)
        scroll_to = scroll_to.value;
      else if (Hanabira.ScrollAny)
        scroll_to = pid;
      
      var cmntable	= $('<table></table>');
      var fieldtable	= $('<table id="fieldtable"></table>');
      var fieldrow	  = $('<tr></tr>');
      var righttd	    = $('<td></td>');
      var lefttd	      = $('<td></td>');
      var right	      = $('<table></table>');
      var left	        = $('<table></table>');
      
      var replyText, trcaptcha, trrempass, trfile, trgetback, trrempass, trsubject, trsage, trname;
      
      $.each(['replyText','trcaptcha','trrempass','trfile','trgetback','trsubject','trname','trsage'], function(i, v) {
        eval("var top_"+v+"=$('#"+v+"');"+v+"=top_"+v+".clone(true);"+v+".attr('id', 'reply-"+v+"');");
        if (i)
        {
          eval((i < 5 ? "left" : "right")+".append("+v+");");
          if (v == 'trfile')
            $(window).unload(function() {top_trfile.replaceWith(trfile.clone(true).attr('id','trfile'))});
          else if (v == 'trsage')
            $(window).unload(function() {top_trsage.find('input')[0].checked = trsage.find('input')[0].checked});
          else if (v != 'trgetback')
            eval("$(window).unload(function() {top_"+v+".find('input').val("+v+".find('input').val())});");
        }
        else
        {
          $(window).unload(function() {top_replyText.val(replyText.val())});
          replyText.val(top_replyText.val());
        }
      });
      
      trsubject.before($('<tr><td></td><td style="text-align:right"><a onclick="QuoteSelected()" class="quote icon" title="'+(Hanabira.LC_ru?'Скопипастить выделенный текст':'Copypaste selected text')+'"><img src="/images/blank-double.png" alt="Quote" style="vertical-align:middle; min-height:17px"></a><img src="/images/blank.png"/><a class="close icon" title="'+(Hanabira.LC_ru?'Убрать':'Remove')+'" onclick="$(Hanabira.ReplyForm).hide()"><img src="/images/blank.png" alt="Remove" style="vertical-align:middle; min-height:17px"/></a></td></tr>'));
      
      trgetback.find('td:eq(1)').append(trsubject.find('input[type=submit]'));
      var capt = $('#captcha-image', trcaptcha).attr('id', 'reply-captcha-image');
      var fn = $('#file_new', trfile).attr('id', 'reply-file_new');
      
      form.append(cmntable.append(replyText).append(fieldtable.append(fieldrow.append(lefttd.append(left)).append(righttd.append(right).css('vertical-align', 'top')))));
      
      Hanabira.ReplyForm = form[0];
    }
    else
    {
      var replyText = $('#reply-replyText');
      var form = $(Hanabira.ReplyForm);
      var capt = $('#reply-captcha-image');
      var scroll_input = $('#reply-scroll_to');
      form.attr('action', '/'+board+'/post/new.xhtml');
      form.find('input[name=thread_id]').val(tid);
    }
    
    if ((Hanabira.LastReply && Hanabira.LastReply.split('-')[0] != board) || (!Hanabira.LastReply && !thisBoard))
      var file_new = $('#reply-file_new', form);
      
    var node = $(click.target);
    var ppp = node.closest('.popup');
    if (ppp.length)
    {
      node = node.closest('tr');
      if (node[0] != form.prev()[0])
        node.after($('<tr></tr>').append($('<td></td>').append(form)));
    }
    else
    {
      node = node.closest('.post');
      if (node[0] != form.prev()[0])
        node.after(form);
    }
    form.show();
      
    var rfn = $('#reply-file_new', node).clone(true).attr('style', '');
    if (file_new)
    {
      if (thisBoard || !rfn.length)
        file_new.replaceWith($('#file_new').clone(true).attr('id', 'reply-file_new'));
      else if (rfn.length)
        file_new.replaceWith(rfn);
    }
      
    setTimeout(function() {
      capt.load(function() {$(this).css('border', 'none')});
      capt.css('border', '2px dashed #FFBB00');
      Refresh(capt[0]);
    }, 200);
    if (Hanabira.ScrollAny || Hanabira.URL.thread)
      scroll_input.val(pid);
    Hanabira.LastReply = board+'-'+pid;
    InsertInto(replyText[0], ">>"+pid+"\n");
  }
}

ShowRefPost = function(e, board, tid, pid)
{
  var a	   = $(e.target);
  var to0 = setTimeout(function()
  {
    var op = tid == pid;
    var thisBoard = ThisBoard(board);
    var postid = (op?'post_':'reply')+pid;
    var id	= board+'-'+postid;
    var w	= $(window).width();
    var x	  = e.pageX;
    var y	  = e.pageY + 30;
    var wx	= w - x;

    set_style = function(r, red) {
      if (red)
      {
        if (Hanabira.Settings&2)
        {
          var y2 = y - r.innerHeight() - 45;
          if (y2 > 0)
            y = y2;
        }
        if ((wx < 600 || wx < w/2) && r.innerWidth() > wx)
        {
          var mw = w - 400;
          x = null;
        }
      }
      r.attr('style', 'top: '+y+'px; max-width: '+(mw||wx)+'px; '+(x == null ? 'right: 0' : 'left: '+x)+'px;');
    } 
    
    var reftab = document.getElementById('ref'+id);
    if (reftab)
    {
      set_style($(reftab), 1);
      $(reftab).click();
      return;
    }
    
    reftab	    = document.createElement('table');
    document.body.appendChild(reftab);
    set_style($(reftab));
    reftab.className = op ? 'oppost popup' : 'popup';
    reftab.id	  = 'ref'+id;
    var reftr	= document.createElement('tr');
    reftr.id	    = 'load'+id;
    var load	  = document.createElement('td');
    reftr.appendChild(load);
    reftab.appendChild(reftr);
    
    if (Hanabira.Settings&1)
      BindRemoveRef(a, reftab);

    var post = Hanabira.LoadedPosts[id] || (thisBoard && document.getElementById(postid));
    if (post)
    {
      load.innerHTML = post.innerHTML || post;
      set_style($(reftab), 1);
      if (!(Hanabira.Settings&1))
        BindCloseRef(reftab);
    }
    else if (thisBoard && Hanabira.URL.thread == tid)
    {
      load.innerHTML = (Hanabira.LC_ru ? 'Пост удалён.' : "Post is deleted.");
      if (!(Hanabira.Settings&1))
        BindRemoveRef(a, reftab);
    }
    else
    {
      reftab.className = 'transparent popup';
      toLoading($(load));
      $.get('/api/post/'+board+'/'+tid+'/'+pid+'.xhtml', {}, function(post, status)
      {
        Hanabira.LoadedPosts[id] = post;
        load.className = '';
        load.innerHTML = post;
        reftab.className = op ? 'oppost popup' : 'popup';
        if (post.indexOf('<') >= 0)
        {
          set_style($(reftab), 1);
          if (!(Hanabira.Settings&1))
            BindCloseRef(reftab);
        }
        else if (!(Hanabira.Settings&1))
          BindRemoveRef(a, reftab);
      });
    }
    
  }, (Hanabira.Settings&2)?200:100);
  
  a.mouseout(function() {clearTimeout(to0)});
}
BindRemoveRef = function(binded, reftab)
{
  var to;
  var rt = $(reftab);
  binded = binded.add(rt);
  binded.mouseout(function() {
    to = setTimeout(function() {rt.remove()}, 300)
  });
  binded.mouseover(function() {clearTimeout(to)});
}
BindCloseRef = function(reftab)
{
  var closetr = document.createElement('tr');
  var close = document.createElement('td');
  var rt = $(reftab);
  close.setAttribute('style', "padding-left: 4px;");
  close.innerHTML = '<span class="close icon"><img src="/images/blank.png" /></span>';
  $(close).click(function() {rt.remove()});
  closetr.appendChild(close);
  reftab.appendChild(closetr);
    
  rt.click(function() {
    Hanabira.Refs[reftab.style.zIndex=Hanabira.zIndex++] = reftab;
  }).click();
}
SetRedir = function()
{
  var redir = {32: (Hanabira.URL.thread?'thread':'page'), 16:Hanabira.URL.page, 8:'board', 4:'thread'}[Hanabira.Settings&60];
  if (redir) 
    $('#trgetback option').each(function() {
      if (this.value == redir)
        this.setAttribute('selected','selected');
      else
        this.removeAttribute('selected');
    });
}
SelectThread = function(event)
{
  var threads = $('.thread');
  var cond, cur_y, y = event.pageY, last_y = threads.offset().top;
  for (i=0;i<threads.length;i++) {
    if (i == threads.length-1)
      cond = last_y < y;
    else {
      cur_y = $(threads[i+1]).offset().top;
      cond = (last_y < y && y < cur_y);
    }
    if (cond)
      return threads[i];
    last_y = cur_y;
  }
}
ExpandList = function(t)
{
  var t = $(t.parentNode.parentNode);
  var tds = t.parent().find('td:hidden');
  t.remove();
  tds.slideDown(200);
}
ScrollTo = function(post)
{
  window.scrollTo(0, $("#post_"+post).offset().top);
}

initialize = function()
{    
    if(typeof(files_max_qty) == "undefined")
      return;
    
    var reply = $('#replyText')
    if (!$.browser.safari)
      reply.keypress(AutoResize).keyup(AutoResize);
  
    var texta = reply[0];
    if (Hanabira.URL.pointer)
    {
        if (!reply.val() && reply.filter(':visible').length)
            InsertInto(texta, ">>"+Hanabira.URL.pointer);
        Highlight(0, Hanabira.URL.pointer);
    }
      
    $('#postform').bind('submit', function(e){
      return UploadProgress(e, this);
    })
    
    if (!(Hanabira.Settings&1))
    {
      if ($.browser.safari)
        $(window).keydown(ClosePopup);
      else
        $(window).keypress(ClosePopup);
    }
    
    var fparent = $('#file_1')[0];
    if (fparent)
      for (var i = 0; i < files_max_qty; i++) {update_file_fields(0, fparent)}
    
    BindCrosses($(".delete input"));
    SetRedir();
    Hanabira.ready = 1;
    if (typeof(init_music_player) != "undefined")
      init_music_player();
}
$(window).unload(function() {set_cookie("wakabastyle", get_active_stylesheet(), 365)});

function fill_opts()
{
  $("#js-form select").each(function() {
    var sum = 0;
    $(this).find('option').each(function() {sum += parseInt(this.value)}).end().val(Hanabira.Settings&sum);
  });
  $("#textsize").val(Hanabira.TextSize);
}
function set_opts(gb2)
{
  var value = 0;
  $("#js-form select").each(function() {value += parseInt(this.value)});
  set_settings(value);
  set_settings($("#textsize").val(), 2);
  $('#ajax-form').ajaxSubmit();
  $('#done').text(Hanabira.LC_ru?"Применила":"Accepted").animate({opacity:0},{duration:1000,complete:function(){
    $('#done').text(' ').css('opacity',100);
    gb2 && document.location.replace(gb2);
  }});
}
function get_opts()
{
  var value = get_settings(0);
  Hanabira.Settings = value ? parseInt(value) : 1;
}
function set_settings(value, unit)
{
  var c = get_settings();
  if (!unit)
    set_cookie('settings', value+c[1], 1000);
  else
    set_cookie('settings', c[0]+' '+value, 1000);
}
function get_settings(unit)
{
  var c = $m(get_cookie('settings'), /^(\d*)( (\d*))?/);
  if (unit == undefined)
    return c;
  else
    return c[unit*2];
}
$t = function(last) {return (new Date).getTime() - (last?parseInt(last):0)}
$m = function(str, re) {return $.map(str.match(re)||[], function(e) {return e||''}).slice(1)}

//            Wakaba css-processing stuff

function get_cookie(name)
{
	with(document.cookie)
	{
		var regexp=new RegExp("(^|;\\s+)"+name+"=(.*?)(;|$)");
		var hit=regexp.exec(document.cookie);
		if(hit&&hit.length>2) return unescape(hit[2]);
		else return '';
	}
};
function set_cookie(name,value,days)
{
	if(days)
	{
		var date=new Date();
		date.setTime(date.getTime()+(days*24*60*60*1000));
		var expires="; expires="+date.toGMTString();
	}
	else expires="";
	document.cookie=name+"="+value+expires+"; path=/";
}
function get_frame_by_name(name)
{
	var frames = window.parent.frames;
	for(i = 0; i < frames.length; i++)
	{
		if(name == frames[i].name) { return(frames[i]); }
	}
}
function set_stylesheet_all(styletitle)
{
    set_stylesheet(styletitle)
    var list = get_frame_by_name('list');
    if(list) set_stylesheet(styletitle, true, list);    
}
function set_stylesheet(styletitle, norefresh, target)
{
	set_cookie("wakabastyle",styletitle,365);
        var links = target ? target.document.getElementsByTagName("link") : document.getElementsByTagName("link");
	var found=false;
	for(var i=0;i<links.length;i++)
	{
		var rel=links[i].getAttribute("rel");
		var title=links[i].getAttribute("title");
		if(rel.indexOf("style")!=-1&&title)
		{
			links[i].disabled=true; // IE needs this to work. IE needs to die.
			if(styletitle==title) { links[i].disabled=false; found=true; }
		}
	}
	if(!found) set_preferred_stylesheet();
}
function set_preferred_stylesheet(target)
{ 
        var links = target ? target.document.getElementsByTagName("link") : document.getElementsByTagName("link");
	for(var i=0;i<links.length;i++)
	{
		var rel=links[i].getAttribute("rel");
		var title=links[i].getAttribute("title");
		if(rel.indexOf("style")!=-1&&title) links[i].disabled=(rel.indexOf("alt")!=-1);
	}
}
function get_active_stylesheet()
{
	var links=document.getElementsByTagName("link");
	for(var i=0;i<links.length;i++)
	{
		var rel=links[i].getAttribute("rel");
		var title=links[i].getAttribute("title");
		if(rel.indexOf("style")!=-1&&title&&!links[i].disabled) return title;
	}
	return null;
}
function get_preferred_stylesheet()
{
	var links=document.getElementsByTagName("link");
	for(var i=0;i<links.length;i++)
	{
		var rel=links[i].getAttribute("rel");
		var title=links[i].getAttribute("title");
		if(rel.indexOf("style")!=-1&&rel.indexOf("alt")==-1&&title) return title;
	}
	return null;
}
function delete_notice(mid)
{
   $.get('/api/notice/delete/'+mid+'.json', {}, function()
   {
     $('#notice_'+mid).empty();
     // Why the fuck it doesn't work?
     $('#notice_'+mid).remove();
     $('#notice_'+mid).remove();
     $('#notice_'+mid).remove();
   });  
}
set_stylesheet(get_cookie("wakabastyle")||get_preferred_stylesheet());
get_opts();
Hanabira.URL = ParseUrl();
if (!$.browser.opera && !$.browser.safari)
$(window).keypress(function(f5) {if(f5.keyCode==116)
{f5.preventDefault(); window.location.reload()}});
