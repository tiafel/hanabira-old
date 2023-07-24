from pylons import config
from hanabira import model
from hanabira.lib.base import render
from pylons.i18n import _, ungettext, N_
from formalchemy import validators
from formalchemy import fields
from formalchemy import forms
from formalchemy import tables
from formalchemy.ext.fsblob import FileFieldRenderer
from formalchemy.ext.fsblob import ImageFieldRenderer

class FieldSet(forms.FieldSet):
    def _render(self, **kwargs):
        return render('/forms/fieldset.mako',
                      extra_vars=kwargs)
    def _render_readonly(self, **kwargs):
        return render('/forms/fieldset_readonly.mako',
                      extra_vars=kwargs)

class Grid(tables.Grid):
    def _render(self, **kwargs):
        return render('/grid.mako',
                      extra_vars=kwargs)
    def _render_readonly(self, **kwargs):
        return render('/grid_readonly.mako',
                      extra_vars=kwargs)


def password_validator(fieldset):
    if fieldset.passwd1.value != fieldset.passwd2.value:
        raise validators.ValidationError(_(u'Passwords do not match'))

## Initialize fieldsets

#Foo = FieldSet(model.Foo)
#Reflected = FieldSet(Reflected)

## Initialize grids

#FooGrid = Grid(model.Foo)
#ReflectedGrid = Grid(Reflected)
