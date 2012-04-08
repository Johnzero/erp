# -*- encoding: utf-8 -*-
import pooler
from osv import fields, osv


class sale_order(osv.osv):
    _name = "fg_sale.order"
    _description = "富光业务部销售订单"
    
    _columns = {
        'name': fields.char('单号', size=64, required=True, readonly=True, select=True),
        'date_order': fields.date('日期', required=True, readonly=True, select=True, states={'draft': [('readonly', False)]}),
        'date_confirm': fields.date('审核日期', readonly=True, select=True, ),
        'user_id': fields.many2one('res.users', '制单人', states={'draft': [('readonly', False)]}, select=True),
        'partner_id': fields.many2one('res.partner', '客户', readonly=True, states={'draft': [('readonly', False)]}, required=True, change_default=True, select=True),        
        'partner_shipping_id': fields.many2one('res.partner.address', '送货地址', readonly=True, required=True, states={'draft': [('readonly', False)]}),
        'order_line': fields.one2many('fg_sale.order.line', 'order_id', '订单明细', readonly=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection([('draft', '草稿'), ('done', '已审核'), ], '订单状态', readonly=True, select=True),
        'note': fields.text('附注'),
    }
    
    _defaults = {
        'date_order': fields.date.context_today,
        'state': 'draft',
        'user_id': lambda obj, cr, uid, context: uid,
        'partner_shipping_id': lambda self, cr, uid, context: context.get('partner_id', False) and self.pool.get('res.partner').address_get(cr, uid, [context['partner_id']], ['default'])['default'],
    }
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', '订单名称不能重复!'),
    ]
    _order = 'name desc'
    
class sale_order_line(osv.osv):
    _name = "fg_sale.order.lone"
    _description = "富光业务部销售订单明细"
    
    _columns = {
        'order_id': fields.many2one('fg_sale.order', '订单', required=True, ondelete='cascade', select=True, readonly=True, states={'draft':[('readonly',False)]}),
        'sequence': fields.integer('Sequence'),
        'product_id': fields.many2one('product.product', '产品', domain=[('sale_ok', '=', True)], change_default=True),
        'product_uom_qty': fields.float('数量', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'product_uom': fields.many2one('product.uom', ' 单位', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection([('draft', '草稿'), ('done', '已审核'), ], '订单状态', readonly=True, select=True),
        'notes': fields.text('附注'),
    }
    
    _order = 'sequence, id'
    
    