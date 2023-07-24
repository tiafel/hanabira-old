# -*- coding: utf-8 -*-
<%page args="title='', opts={}, name='', hint='', ajax=False, type='select'"/>
    <tr>
    %if title:
    <td class="postblock"${hint and ' title="%s"'%(_(hint)) or '' |n}>${_(title)}:</td>
    <td>
    %else:
    <td colspan="2">
    %endif
    %if type == 'select':
        <select name="${name}" id="${name}">
        %for o in opts:
            <option value="${o}"${ajax and c.__getattr__(name) == o and ' selected' or ''}>${_(opts[o])}</option>
        %endfor
        </select>
    %elif type == 'checkbox':
        <input type="checkbox" name="${name}" id="${name}"${ajax and c.__getattr__(name) and " checked" or ""}/>
    %elif type == 'text':
        <input type="text" name="${name}" id="${name}" value="${ajax and c.__getattr__(name) or ''}" />
    %endif
    </td></tr>