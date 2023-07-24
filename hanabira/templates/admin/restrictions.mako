# -*- coding: utf-8 -*-
<%inherit file="admin.mako" />
<%include file="filter.mako" args="filter=c.filter" />
<table style="border:1px #000000 solid;">
<tr>
  <td>
    <form action="${h.url('restrictions_new')}" method="POST">
    ${_('New restriction')} <br/>
    ${_('Type')}: <select name='type'>
    %for rt in c.restriction_types:
    <option>${rt}</option>
    %endfor
    </select>, 
    ${_('value')}: <input type="text" name="value"/>
    ${_('effect')}: <select name="effect">
    %for ef in c.effects:
    <option>${ef}</option>
    %endfor
    </select>
    ${_('comment')}: <input type="text" name="comment" />
    <input type="submit" value="${_('Add')}"/>
    </form>
  </td>
</tr>
</table>
<%include file="filter.paging.mako" args="filter=c.filter, route='restrictions'" />
<table style="border: 1px #000000 solid;">
<tr>
  <td>${_('Type')}</td>
  <td>${_('Value')}</td>
  <td>${_('Effect')}</td>
  <td>${_('Active')}</td>
  <td>${_('Comment')}</td>
  <td>${_('Actions')}</td>
</tr>
%for r in c.restrictions:
<tr>
  <td>${r.type}</td>
  <td>${r.value}</td>
  <td>${r.effect}</td>
  <td>${not r.expired and _('Yes') or _('No')}</td>
  <td>${r.comment}</td>
  <td><a href="${h.url('restrictions_expire', restriction_id=r.restriction_id)}">${r.expired and _('Enable') or _('Disable')}</a></td>
</tr>
%endfor
</table>
<%include file="filter.paging.mako" args="filter=c.filter, route='restrictions'" />
