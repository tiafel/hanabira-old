# -*- coding: utf-8 -*-

from .base import *

import logging
log = logging.getLogger(__name__)

__all__ = ['ErrorView', 'PermissionErrorView', 'error_codes']

class ErrorView(BaseView):
    is_error = True
    def __init__(self, code, alias, message):
        self.code = code
        self.alias = alias
        self.message = message
        self.data = None
        
    def make_xhtml(self):
        return self.message
    
    def make_dict(self):
        if self.data:
            data = self.data.copy()
        else:
            data = {}
        if not 'alias' in data:
            data['alias'] = self.alias
        
        return {'code':self.code,
                'message':self.message,
                'data':data}
    
    def __call__(self, **data):
        new_err = self.__class__(self.code, self.alias, self.message)
        new_err.data = data
        return new_err
    
class PermissionErrorView(ErrorView):
    def __init__(self, token, need_global=False):
        self.code = 40310
        self.alias = 'admin_permission'
        self.message = error_codes[self.code].message
        self.permission = token
        self.need_global = need_global
        self.data = {'token':token}
        
    def make_xhtml(self):
        c.permission = self.permission
        c.need_global = self.need_global
        return render('/admin/permission.error.mako')        

error_codes_list = [
    # 404xx - does not exit
    (40401, 'element_not_found', N_('Specified element does not exist.')),
    (40420, 'element_deleted', N_('Specified element is deleted.')),    
    (40421, 'post_deleted', N_('Post is deleted.')),
    (40422, 'thread_deleted', N_('Thread is deleted.')),    
    
    # 403xx - permissions error
    # 4030x - read permission error
    (40300, 'forbidden', N_('Current session does not have permissions to execute this request')),
    (40301, 'element_read_not_allowed', N_('Current session does not have access to specified element.')),
    (40302, 'board_read_not_allowed', N_('Current session does not have access to specified board.')),
    (40303, 'temporary_restricted_to_author', N_('This feature is temporarily restricted to post author and moderators.')),
    (40310, 'admin_permission', N_('Your account does not have needed permission token.')),
    # 4035x - modify permission error
    (40351, 'element_modify_not_allowed', N_('Current session does not have permissions to edit specified element')),
    
    # 400xx - bad params
    (40001, 'api_missing_parameter', N_('Some mandatory parameters are missing.')),
    (40002, 'api_bad_parameter', N_('Some parameters have invalid value specified.')),

    ]

g = globals()
error_codes = {}
for error_code, error_alias, error_message in error_codes_list:
    error_codes[error_code] = g['error_' + error_alias] = ErrorView(error_code, error_alias, error_message)                                 
    __all__.append('error_' + error_alias)
