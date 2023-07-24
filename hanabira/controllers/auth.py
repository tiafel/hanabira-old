import logging
from hanabira.forms.admins import AdminForm, RegisterForm
from hanabira.model.admins import Admin
from hanabira.model.invites import Invite
from hanabira.model.logs import ModLogin
from hanabira.lib.base import *

log = logging.getLogger(__name__)

class AuthController(BaseController):
    def login(self):
        # if admin is already authorized, redirect to admin panel
        admin = session.get('admin', None)
        if admin and admin.valid() and admin.enabled:
            return redirect(url('admin'))
        
        if request.POST and request.POST.get('login', None):
            admin = Admin.get(login=request.POST.get('login', None), password=request.POST.get('password', None))
            if admin:
                session['admin'] = admin
                session.save()
                ModLogin(ip=ipToInt(request.ip), session_id=session.id, admin=admin, commit=True)
                return redirect(url('admin'))
        return render('/auth/login.mako')

    def logout(self):
        if session.get('admin', False):
            del session['admin']
            session.save()
        return redirect(url('login'))

    def register(self, code=None):
        if not session.get('invite', False):
            invite = Invite.get(code)
            if not invite:
                return redirect(url('login'))
            else:
                session['invite'] = code
                session.save()

        admin = session.get('admin', None)
        if admin and admin.valid() and admin.enabled:
            del session['invite']
            session.save()
            return redirect(url('admin'))

        form = RegisterForm()
        if request.POST:
            form.rebind(Admin, data=request.POST)
            if form.validate():
                form.sync()
                meta.Session.add(form.model)
                form.model.set_password(form.passwd1.value)
                del session['invite']
                session.save()
                return redirect(url('login'))
                
        c.form = form
        return render('/auth/register.mako')
        
        
        
