# -*- coding: utf-8 -*-


import tools
from osv import fields, osv

class sale_report(osv.osv):
    _name = "fg_sale.report"
    _description = "Sales Orders Statistics"
    _auto = False
    _rec_name = 'date'
    
    _columns = {
        'date': fields.date('日期', readonly=True),
        'date_confirm': fields.date('审核日期', readonly=True),
        'year': fields.char('年份', size=4, readonly=True),
        'month': fields.selection([('01', '一月'), ('02', '二月'), ('03', '三月'), ('04', '四月'),
            ('05', '五月'), ('06', '六月'), ('07', '七月'), ('08', '八月'), ('09', '九月'),
            ('10', '十月'), ('11', '十一月'), ('12', '十二月')], '月份', readonly=True),
        'day': fields.char('日期', size=128, readonly=True),
        'product_id': fields.many2one('product.product', '产品', readonly=True),
        'product_category_id':fields.many2one('product.category', '产品分类', readonly=True),
        'product_uom': fields.many2one('product.uom', 'UoM', readonly=True),
        'product_uom_qty': fields.float('# of Qty', readonly=True),

        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True),
        'user_id': fields.many2one('res.users', 'Salesman', readonly=True),
        
    }