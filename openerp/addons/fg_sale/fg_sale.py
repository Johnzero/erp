# -*- encoding: utf-8 -*-
import pooler
from osv import fields, osv


class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'ratio': fields.float('比率', digit=2)
    }


class sale_order(osv.osv):
    _name = "fg_sale.order"
    _description = "富光业务部销售订单"
    
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        pass
    
    _columns = {
        'name': fields.char('单号', size=64, required=True, readonly=True, select=True),
        'date_order': fields.date('日期', required=True, readonly=True, select=True, states={'draft': [('readonly', False)]}),
        'date_confirm': fields.date('审核日期', readonly=True, select=True, ),
        'user_id': fields.many2one('res.users', '制单人', states={'draft': [('readonly', False)]}, select=True),
        'partner_id': fields.many2one('res.partner', '客户', readonly=True, states={'draft': [('readonly', False)]}, required=True, change_default=True, select=True),        
        'partner_shipping_id': fields.many2one('res.partner.address', '送货地址', readonly=True, required=True, states={'draft': [('readonly', False)]}),
        'amount_total': fields.function(_amount_all, string='金额', store = True, multi='sums'),
        'order_line': fields.one2many('fg_sale.order.line', 'order_id', '订单明细', readonly=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection([('draft', '草稿'), ('done', '已审核'), ('cancel','已取消')], '订单状态', readonly=True, select=True),
        'note': fields.text('附注'),
    }
    
    _defaults = {
        'date_order': fields.date.context_today,
        'state': 'draft',
        'user_id': lambda obj, cr, uid, context: uid,
        'partner_shipping_id': lambda self, cr, uid, context: context.get('partner_id', False) and self.pool.get('res.partner').address_get(cr, uid, [context['partner_id']], ['default'])['default'],
    }
    
    def _log_event(self, cr, uid, ids, factor=0.7, name='FG Sale Order'):
        invs = self.read(cr, uid, ids, ['date_order', 'partner_id', 'amount_untaxed'])
        for inv in invs:
            part = inv['partner_id'] and inv['partner_id'][0]
            pr = inv['amount_untaxed'] or 0.0
            partnertype = 'customer'
            eventtype = 'sale'
            event = {
                'name': 'Order: '+name,
                'som': False,
                'description': 'Order '+str(inv['id']),
                'document': '',
                'partner_id': part,
                'date': time.strftime(DEFAULT_SERVER_DATE_FORMAT),
                'user_id': uid,
                'partner_type': partnertype,
                'probability': 1.0,
                'planned_revenue': pr,
                'planned_cost': 0.0,
                'type': eventtype
            }
            self.pool.get('res.partner.event').create(cr, uid, event)
    
    def review(self, cr, uid, ids, context=None):
        return True
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', '订单名称不能重复!'),
    ]
    _order = 'name desc'
    
class sale_order_line(osv.osv):
    _name = "fg_sale.order.line"
    _description = "富光业务部销售订单明细"
    
    
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = 0.0
        
        return res
    
    _columns = {
        'order_id': fields.many2one('fg_sale.order', '订单', required=True, ondelete='cascade', select=True),
        'sequence': fields.integer('Sequence'),
        'product_id': fields.many2one('product.product', '产品', domain=[('sale_ok', '=', True)], change_default=True),
        'product_uom_qty': fields.float('数量', required=True,),
        'product_uom': fields.many2one('product.uom', ' 单位', required=True,),
        'price_discount': fields.float('打折价格', digit=2),
        'price_subtotal': fields.function(_amount_line, string='小计'),
        'notes': fields.char('附注', size=100),
    }
    
    _order = 'sequence, id'
    
    