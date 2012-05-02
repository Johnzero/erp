# -*- encoding: utf-8 -*-
from osv import fields, osv
    
class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'fullnum': fields.char('num', size=40)
    }

class res_user(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'fullnum': fields.char('num', size=40)
    }

class product_uom(osv.osv):
    _inherit = 'product.uom'
    _columns = {
        'fullnum': fields.char('num', size=40)
    }

class product_product(osv.osv):
    _inherit = 'product.product'
    _columns = {
        'fullnum': fields.char('num', size=40),
        'source':fields.char('来源', size=40),
    }