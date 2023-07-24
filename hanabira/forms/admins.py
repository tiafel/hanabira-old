from pylons.i18n import _, ungettext, N_
from hanabira.forms import *
from hanabira.model.admins import Admin
from formalchemy.fields import Field

import logging
log = logging.getLogger(__name__)

class RegisterFieldSet(FieldSet):
    def validate(self):
        log.info("RegisterFieldSet.validate()")
        f = FieldSet.validate(self)
        self.errors.__setitem__('wtf', ["Passwords do not match"])
        if self.passwd1.value != self.passwd2.value:
            log.info("Passwords do not match")
            f2 = False
            #if not self.errors.get(None, False):
            #    self.errors[None] = []
            self.errors['passwd2'] = [_("Passwords do not match")]
        else:
            f2 = True
        log.info("Errors: %s" % self.errors)
        log.info("Result: %s" % (f and f2))
        return f and f2

def unique_login(login):
    if Admin.query.filter(Admin.login == login).first():
        raise validators.ValidationError(_(u'Account with such login already exists'))

def unique_email(email):
    if Admin.query.filter(Admin.email == email).first():
        raise validators.ValidationError(_(u'Account with such email already exists'))
    
def AdminForm(admin=Admin):
    return FieldSet(admin)

def AdminEditForm(admin):
    fs = AdminForm(admin)
    fs.add(Field('passwd1').label(_(u"Password")))
    fs.add(Field('passwd2').label(_(u"Repeat password")))
    fs.configure(options=[fs.passwd1.password(), fs.passwd2.password()],
                 exclude=[fs.password, fs.permissions, fs.keys], global_validator=password_validator)
    return fs
    

def RegisterForm():
    fs = AdminForm()
    fs.add(Field('passwd1').required().label(_(u"Password")))
    fs.add(Field('passwd2').required().label(_(u"Repeat password")))
    fs.configure(options=[fs.login.validate(unique_login), fs.email.validate(unique_email), fs.passwd1.password(), fs.passwd2.password()],
                 exclude=[fs.password, fs.enabled, fs.permissions, fs.keys], global_validator=password_validator)
    return fs


def ProfileForm(admin):
    fs = AdminForm(admin)
    fs.add(Field('passwd1').label(_(u"Password")))
    fs.add(Field('passwd2').label(_(u"Repeat password")))
    fs.configure(options=[fs.passwd1.password(), fs.passwd2.password()],
                 exclude=[fs.password, fs.enabled, fs.permissions, fs.keys], global_validator=password_validator)
    return fs
