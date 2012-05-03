# -*- encoding: utf-8 -*-
from osv import fields, osv
    
class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'fullnum': fields.char('num', size=40),
        'sales_ids': fields.many2many('res.users', 'rel_partner_user','partner_id','user_id', '负责业务员', help='内部负责业务员. 设置邮件地址,以备通知使用.'),
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