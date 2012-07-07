# -*- encoding: utf-8 -*-
import pooler, time
from osv import fields, osv
from tools import get_initial



class cust_order(osv.osv):
    _name = "fg_sale.cust.order"
    _description = "富光销售部定制杯清单"
    
    def _get_logs(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        log_obj = self.pool.get('res.log')
        
        for id in ids:
            logs = log_obj.search(cr, uid, [('res_model','=','fg_sale.cust.order'),('res_id', '=', id)])
            if logs:
                res[id] = logs
            else:
                res[id] = False
    
        return res
        
    
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = { 'amount_total':0.0 }
            amount = 0
            for line in order.order_line:
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
        'partner_id': fields.many2one('res.partner', '客户', readonly=True, states={'draft': [('readonly', False)]}, change_default=True, select=True),
        'client': fields.char('客户', size=64, readonly=True, states={'draft': [('readonly', False)]}),
        'contact':fields.char('联系人', size=64, readonly=True, states={'draft': [('readonly', False)]}),
        'phone':fields.char('联系电话', size=64, readonly=True, states={'draft': [('readonly', False)]}),
        'date_delivery':fields.date('交货日期', readonly=True, states={'draft': [('readonly', False)]}),
        'date_arrival_req':fields.date('要求到货日期', readonly=True, states={'draft': [('readonly', False)]}),
        'delivery_addr':fields.char('交货地址', size=128, readonly=True, states={'draft': [('readonly', False)]}),
        'amount_paid': fields.float('已付金额', digits=(10,2), readonly=True, states={'draft': [('readonly', False)]}),
        
        'type':fields.selection([('common','普通单'),('partner','客户单')], '定制单类型', readonly=True, states={'draft': [('readonly', False)]}),
        'invoice_type':fields.selection([('none','不开票'),('common','普通发票'),('va','增值税发票')], '发票类型', readonly=True, states={'draft': [('readonly', False)]}),
        'invoice_title':fields.char('发票抬头', size=64, readonly=True, states={'draft': [('readonly', False)]}),
        
        'amount_left_info': fields.char('余额支付说明', size=64, readonly=True, states={'draft': [('readonly', False)]}),
        'delivery_method':fields.char('交货方式', size=64, readonly=True, states={'draft': [('readonly', False)]}),
        'delivery_fee':fields.char('运费承担方', size=64, readonly=True, states={'draft': [('readonly', False)]}),
        
        'amount_total': fields.function(_amount_all, string='金额', store=False, multi='sums'),
        'order_line': fields.one2many('fg_sale.cust.order.line', 'order_id', '订单明细', readonly=True, states={'draft': [('readonly', False)]}),
        'logs':fields.function(_get_logs, type="one2many", readonly=True, relation="res.log"),
        
        'state': fields.selection([('draft', '未审核'), ('done', '已提交')], '订单状态', readonly=True, select=True),
        'note': fields.text('备注'),
        'ref_order_id':fields.many2one('fg_sale.order', 'Ref Order ID', required=False),
    }
    
    
    def create(self, cr, uid, vals, context=None):
        if not vals.get('partner_id') and not vals.get('client'):
            raise osv.except_osv('没有填写客户名称', '请填写客户名称.')
        
        if not vals.has_key('name'):
            obj_sequence = self.pool.get('ir.sequence')
            vals['name'] = obj_sequence.get(cr, uid, 'fg_sale.cust.order')
            
            
        id = super(cust_order, self).create(cr, uid, vals, context)
        #self.log(cr, uid, id, '创新了新的订单 %s' % vals['name'],'由用户%s'%uid, context)
        
        return id
    
    def write(self, cr, uid, ids, vals, context=None):
        if not vals.get('partner_id') and not vals.get('client'):
            raise osv.except_osv('没有填写客户名称', '请填写客户名称.')
        
        return super(cust_order, self).write(cr, uid, ids, vals, context)
    
    
    _defaults = {
        'date_order': fields.date.context_today,
        'state': 'draft',
        'user_id': lambda obj, cr, uid, context: uid,
        'type': 'common',
    }
    
    def copy(self, cr, uid, id, default={}, context=None):
        raise osv.except_osv('不允许复制', '订单不允许复制.')

    _sql_constraints = [
        ('cust_order_name_uniq', 'unique(name)', '订单编号不能重复!'),
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
        'extra_amount':fields.float('附加费用', digits=(16,4)),
        'subtotal_amount': fields.float('小计', digits=(16,4)),
        'note': fields.char('附注', size=100),
    }

class sale_order(osv.osv):
    _inherit = 'fg_sale.order'
    _columns = {
        'cust_order_id': fields.one2many('fg_sale.cust.order', 'ref_order_id', '原定制单', required=False),
    }