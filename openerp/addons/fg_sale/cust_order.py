# -*- encoding: utf-8 -*-
import pooler, time
from osv import fields, osv
from tools import get_initial



class cust_order(osv.osv):
    _name = "fg_sale.cust.order"
    _description = "富光销售部定制杯清单"
    
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = { 'amount_total':0.0 }
            amount = 0
            for line in order.order_line:
                #todo: got to decide which one to add. subtotal_amount or, discount_amount
                amount = amount + line.subtotal_amount
            res[order.id]['amount_total'] = amount
        return res
    
    _columns = {
        'name': fields.char('单号', size=64, select=True, readonly=True),
        'date_order': fields.date('日期', required=True, readonly=True, select=True, states={'draft': [('readonly', False)]}),
        'date_confirm': fields.date('审核日期', readonly=True, select=True),
        'due_date_from':fields.function(lambda *a,**k:{}, method=True, type='date',string="开始日期"),
        'due_date_to':fields.function(lambda *a,**k:{}, method=True, type='date',string="结束日期"),
        
        'user_id': fields.many2one('res.users', '填单人', select=True, readonly=True),
        'confirmer_id': fields.many2one('res.users', '业务接单人', select=True, readonly=True),
        'partner_id': fields.many2one('res.partner', '客户', readonly=True, states={'draft': [('readonly', False)]}, required=True, change_default=True, select=True),
        'contact':fields.char('联系人', size=64, readonly=True, states={'draft': [('readonly', False)]}),
        'phone':fields.char('联系电话', size=64, readonly=True, states={'draft': [('readonly', False)]}),
        'date_delivery':fields.date('交货日期', readonly=True, states={'draft': [('readonly', False)]}),
        'delivery_addr':fields.char('交货地址', size=128, readonly=True, states={'draft': [('readonly', False)]}),
        'amount_paid': fields.float('已付金额', digits=(10,2), readonly=True, states={'draft': [('readonly', False)]}),
        'invoice_type':fields.char('发票类型',size=64, readonly=True, states={'draft': [('readonly', False)]}),
        'amount_left_info': fields.char('余额支付说明', size=64, readonly=True, states={'draft': [('readonly', False)]}),
        'delivery_method':fields.char('交货方式', size=64, readonly=True, states={'draft': [('readonly', False)]}),
        'delivery_fee':fields.char('运费承担方', size=64, readonly=True, states={'draft': [('readonly', False)]}),
        
        'amount_total': fields.function(_amount_all, string='金额', store=False, multi='sums'),
        'order_line': fields.one2many('fg_sale.cust.order.line', 'order_id', '订单明细', readonly=True, states={'draft': [('readonly', False)]}),
        
        'state': fields.selection([('draft', '未审核'), ('done', '已审核'), ('cancel','已取消')], '订单状态', readonly=True, select=True),
        'note': fields.text('备注'),
    }
    
    
    def create(self, cr, uid, vals, context=None):
        if not vals.has_key('name'):
            obj_sequence = self.pool.get('ir.sequence')
            vals['name'] = obj_sequence.get(cr, uid, 'fg_sale.cust.order')
            
            
        id = super(cust_order, self).create(cr, uid, vals, context)
        
        return id
    
    _defaults = {
        'date_order': fields.date.context_today,
        'state': 'draft',
        'user_id': lambda obj, cr, uid, context: uid,
    }
    
    def copy(self, cr, uid, id, default={}, context=None):
        raise osv.except_osv('不允许复制', '订单不允许复制.')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', '订单编号不能重复!'),
    ]
    _order = 'id desc'
    

class cust_order_line(osv.osv):
    _name = "fg_sale.cust.order.line"
    _description = "富光销售部定制杯清单"

    _columns = {
        'order_id': fields.many2one('fg_sale.cust.order', '订单', required=True, ondelete='cascade', select=True),
        'product_id': fields.many2one('product.product', '产品', required=True, domain=[('sale_ok', '=', True)], change_default=True),
        'product_uom_qty': fields.float('数量', required=True, digits=(16,0)),
        'unit_price': fields.float('开票价', required=True, digits=(16,4)),
        'cust_price': fields.float('版费', required=True, digits=(16,4)),
        'subtotal_amount': fields.float('小计', digits=(16,4)),
        'note': fields.char('附注', size=100),
    }

class sale_order(osv.osv):
    _inherit = 'fg_sale.order'
    _columns = {
        'cust_order_id': fields.float('原定制单', digit=2, required=False),
    }