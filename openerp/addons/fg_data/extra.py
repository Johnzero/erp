# -*- encoding: utf-8 -*-
from osv import fields, osv

class product_product(osv.osv):
    _inherit = 'product.product'
    _columns = {
        'fullnum': fields.char('num', size=40)
    }
    
class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'fullnum': fields.char('num', size=40)
    }