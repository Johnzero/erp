# -*- coding: utf-8 -*-

from osv import osv
import pyodbc
        
class customer_import(osv.osv_memory):
    _name = "fg_data.customer.wizard.import"
    _description = "customer importing."
    
    _columns = {
        
        
    }
    
    def import_customer(self, cr, uid, ids, context=None):
        
        return {'type': 'ir.actions.act_window_close'}

