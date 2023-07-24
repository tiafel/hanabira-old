# -*- coding: utf-8 -*-

from pylons import tmpl_context as c, cache, config, app_globals as g, request, response, session, url
from hanabira.view.error import *
from hanabira.lib.decorators import getargspec, make_args_for_spec, decorator

class PermissionException(Exception):
    pass

def check_permissions(permission, need_global=True, allow_key=False):
    """
    Used as
    @check_permissions(permission) for global check
    @check_permissions(permission, False) for scoped check
    In later case, function *MUST* accept 'scopes' keyword, and have it *LAST* in list
    """
    def do_check(func, self, *args, **kwargs):
        if allow_key and 'key' in request.GET:
            session.set_admin_from_key(request.GET['key'])
        if need_global:
            if session.get_token(permission):
                return func(self, *args, **kwargs)
            else:
                return PermissionErrorView(permission, need_global)
        else:
            scopes = session.get_token(permission)
            if scopes:
                kwargs['scopes'] = scopes
                if args:
                    args = list(args)[:-1]
                try:
                    return func(self, *args, **kwargs)
                except PermissionException as e:
                    return error_forbidden
            else:
                return PermissionErrorView(permission, need_global)
    return decorator(do_check)