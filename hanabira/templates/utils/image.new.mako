# -*- coding: utf-8 -*-
<%inherit file="/header.mako" />
<form method="POST"  enctype="multipart/form-data">
  <table>
    <tbody>
      <tr>
	<td class="postblock">${_('From existing file')}</td>
	<td>
	  <input type="file" name="file"/>
	  <select name="rating"><option>SFW</option><option>R-15</option><option>R-18</option><option>R-18G</option></select>
	  <input type="submit" name="upload" value="${_('Upload')}" />
	</td>
      </tr>
      <tr>
	<td class="postblock">${_('Filename')}</td>
	<td><input name="shi_filename" size="35" /></td>
      </tr>
      <tr>
	<td class="postblock">${_('Dimensions')}</td>
	<td><input name="shi_width" size="5" value="600" />×<input name="shi_height" size="5" value="600" /></td>
      </tr>
      <tr>
	<td class="postblock">${_('Save animation')}</td>
	<td><input name="shi_animation" type="checkbox" /></td>
      </tr>
      <tr>
	<td class="postblock">${_('Tool')}</td>
	<td><select name="tool"><option value="shi_normal">Shi Painter Normal</option><option value="shi_pro">Shi Painter Pro</option></select></td>
      </tr>
      <tr>
	<td colspan="2"><input type="submit" name="draw" value="${_('Draw')}"></td>
      </tr>
    </tbody>
  </table>
</form>