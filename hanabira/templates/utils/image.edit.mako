# -*- coding: utf-8 -*-
<%inherit file="/header.mako" />
<script type="text/javascript" src="${h.static('js/jquery.jcrop-0.9.8.js')}"></script>
<script type="text/javascript" src="${h.static_versioned('js/images.js')}"></script>
<script type="text/javascript">
  var image_width = ${c.file.metainfo['width']};
  var image_height = ${c.file.metainfo['height']};
</script>
<form method="POST">
  <input type="hidden" id="x" name="x" />
  <input type="hidden" id="y" name="y" />
  <input type="hidden" id="w" name="w" />
  <input type="hidden" id="h" name="h" />
  <table>
    <tr><td>
    <table width="100%">
      <tr>
	<td class="postblock" colspan="2">${_('Preview')}</td>
      </tr>
      <tr>
	<td colspan="2">
	  <div style="width:200px;height:200px;overflow:hidden;margin-left:5px;" id="jcrop-preview-div">
	    <img src="${h.static(c.file.path)}" id="jcrop-preview" />
	  </div>
	</td>
      </tr>
      <tr>
	<td class="postblock" colspan="2">${_('Source image')}</td>
      </tr>
      <tr>
	<td colspan="2"><img id="jcrop-image" src="${h.static(c.file.path)}" width="${c.file.metainfo['width']}" height="${c.file.metainfo['height']}" /></td>
      </tr>
    </table>
    <table width="100%">
      <tr>
	<td class="postblock">${_('Tool')}</td>
	<td>
	  <select name="tool" onchange="update_tool(event, this);">
	    <option value="motivator">${_('(De)motivator')}</option>
	    <option value="macro">${_('Macro')}</option>
	    <option value="shi_normal">${_('Shi Painter Normal')}</option>
	    <option value="shi_pro">${_('Shi Painter Pro')}</option>
	  </select>
	</td>
      </tr>
    </table>
    <table width="100%" id="motivator-options" style="display:none;">
      <tr>
	<td class="postblock">${_('Orientation')}</td>
	<td>
	  <input id="aspect1" type="radio" name="motivator_aspect" value="landscape" checked="" onclick="update_aspect(this);" />
	  <label for="aspect1">${_('Landscape')}</label>
	  <input id="aspect2" type="radio" name="motivator_aspect" value="portrait" onclick="update_aspect(this);" />
	  <label for="aspect2">${_('Portrait')}</label>
	  <input id="aspect3" type="radio" name="motivator_aspect" value="custom" onclick="update_aspect(this);" />
	  <label for="aspect3">${_('Custom')}</label>
	</td>
      </tr>
      <tr>
	<td class="postblock">${_('Title')}</td>
	<td><input name="motivator_title" value="" /></td>
      </tr>
      <tr>
	<td class="postblock">${_('Comment')}</td>
	<td><textarea name="motivator_text"></textarea></td>
      </tr>
    </table>
    <table width="100%" id="macro-options" style="display:none;">
      <tr>
	<td class="postblock" colspan="2">${_('Top text')}</td>
      </tr>
      <tr>
	<td class="postblock">${_('Text')}</td>
	<td><input name="macro_top_text" value="" /></td>
      </tr>
      <tr>
	<td class="postblock">${_('Align')}</td>
	<td>
	  <select name="macro_top_align">
	    <option value="left">${_('Left')}</option>
	    <option value="center" selected="True">${_('Center')}</option>
	    <option value="right">${_('Right')}</option>
	  </select>
	</td>	
      </tr>
      <tr>
	<td class="postblock">${_('Font')}</td>
	<td>
	  <select name="macro_top_font">
	    %for font in c.fonts:
	    <option value="${font}">${c.fonts[font]['name']}</option>
	    %endfor
	  </select>
	</td>	
      </tr>
      <tr>
	<td class="postblock" colspan="2">${_('Bottom text')}</td>
      </tr>
      <tr>
	<td class="postblock">${_('Text')}</td>
	<td><input name="macro_bottom_text" value="" /></td>
      </tr>
      <tr>
	<td class="postblock">${_('Align')}</td>
	<td>
	  <select name="macro_bottom_align">
	    <option value="left">${_('Left')}</option>
	    <option value="center" selected="True">${_('Center')}</option>
	    <option value="right">${_('Right')}</option>
	  </select>
	</td>	
      </tr>
      <tr>
	<td class="postblock">${_('Font')}</td>
	<td>
	  <select name="macro_bottom_font">
	    %for font in c.fonts:
	    <option value="${font}">${c.fonts[font]['name']}</option>
	    %endfor
	  </select>
	</td>	
      </tr>
    </table>
    <table width="100%" id="shi-options" style="display:none;">
      <tr>
	<td class="postblock">${_('Dimensions')}</td>
	<td><input name="shi_width" id="shi-width" size="5" value="600" />×<input name="shi_height" id="shi-height" size="5" value="600" /></td>
      </tr>
      <tr>
	<td class="postblock">${_('Filename')}</td>
	<td><input name="shi_filename" value="${c.file.filename}" /></td>
      </tr>
      <tr>
	<td class="postblock">${_('Save animation')}</td>
	<td><input name="shi_animation" type="checkbox" /></td>
      </tr>
    </table>
    <table width="100%">
      <tr>
	<td colspan="2"><input type="submit" name="draw" value="${_('Draw')}"></td>
      </tr>
    </table>
    </td></tr>
  </table>
</form>
