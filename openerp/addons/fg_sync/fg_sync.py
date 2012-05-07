# -*- encoding: utf-8 -*-

from osv import osv
from osv import fields
import time


class fg_sync_scheduler(osv.osv):
    _name = "fg_sync.scheduler"
    _description = "order importing."
    
    _columns = {
        'name': fields.char('Server name', size=64,required=True),
        'server_url': fields.char('Server URL', size=64,required=True),
        'server_port': fields.integer('Server Port', size=64,required=True),
        'server_db': fields.char('Server Database', size=64,required=True),
        'login': fields.char('User Name',size=50,required=True),
        'password': fields.char('Password',size=64,required=True),
        'model_id': fields.many2one('ir.model', 'Object to synchronize',required=True),
        'domain':fields.char('Domain', size=64, select=1, required=1),
        'div': fields.boolean('Div'),
        'sync_date':fields.datetime('Latest', readonly=True),
    }
    _defaults = {
        'server_port': lambda *args: 8069
    }
    
    
    def do_run_scheduler(self, cr, uid, ids=None, context=None):
        """Scheduler for event reminder
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of whatever’s IDs.
        @param context: A standard dictionary for contextual values
        """
        if context is None:
            context = {}
            
        return True