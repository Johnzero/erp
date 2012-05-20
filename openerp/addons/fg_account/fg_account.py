# -*- encoding: utf-8 -*-

from osv import osv
from osv import fields
import time


class fg_account_journey(osv.osv):
    _name = 'fg_account.journey'
    _description = '账本'
    
    _columns = {
        'name': fields.char('名称', size=40, required=True),
        'factor':fields.float('换算率', digits=(8, 1)),
    }

