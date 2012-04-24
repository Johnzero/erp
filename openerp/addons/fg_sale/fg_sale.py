# -*- encoding: utf-8 -*-
import pooler, time
from osv import fields, osv
from tools import DEFAULT_SERVER_DATETIME_FORMAT,get_initial

class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'ratio': fields.float('比率', digit=2)
    }

class sale_order(osv.osv):
    _name = "fg_sale.order"
    _description = "富光业务部销售订单"
    
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
        'sub_name': fields.char('副单号', size=64, select=True, readonly=True),
        'date_order': fields.date('日期', required=True, readonly=True, select=True, states={'draft': [('readonly', False)]}),
        'date_confirm': fields.date('审核日期', readonly=True, select=True),
        'user_id': fields.many2one('res.users', '制单人', select=True, readonly=True),
        'confirmer_id': fields.many2one('res.users', '审核人', select=True, readonly=True),
        'partner_id': fields.many2one('res.partner', '客户', readonly=True, states={'draft': [('readonly', False)]}, required=True, change_default=True, select=True),        
        'partner_shipping_id': fields.many2one('res.partner.address', '送货地址', readonly=True, required=True, states={'draft': [('readonly', False)]}),
        'amount_total': fields.function(_amount_all, string='金额', store=True, multi='sums'),
        'order_line': fields.one2many('fg_sale.order.line', 'order_id', '订单明细', readonly=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection([('draft', '未审核'), ('done', '已审核'), ('cancel','已取消')], '订单状态', readonly=True, select=True),
        'minus': fields.boolean('红字', readonly=True, states={'draft': [('readonly', False)]}),
        'note': fields.text('附注'),
        'sync':fields.boolean('备用'),
    }
    
    _defaults = {
        'date_order': fields.date.context_today,
        'state': 'draft',
        'minus': False, 
        'sync':False,
        'user_id': lambda obj, cr, uid, context: uid,
        'partner_shipping_id': lambda self, cr, uid, context: context.get('partner_id', False) and self.pool.get('res.partner').address_get(cr, uid, [context['partner_id']], ['default'])['default'],
    }
    
    def copy(self, cr, uid, id, default={}, context=None):
        raise osv.except_osv(_('Invalid action !'), '不允许复制.')
    
    def create(self, cr, uid, vals, context=None):
        if not vals.has_key('name'):
            obj_sequence = self.pool.get('ir.sequence')
            vals['name'] = obj_sequence.get(cr, uid, 'fg_sale.order')
            
        if not vals.has_key('sub_name'):
            partner_obj = self.pool.get('res.partner')
            partner_name = partner_obj.name_get(cr, uid, [vals['partner_id']])[0][1]
            initial = get_initial(partner_name)
            
            cr.execute("select count(*) from fg_sale_order where partner_id = %s;" % vals['partner_id'] )
            res = cr.fetchone()
            count = res and res[0] or 0
            
            vals['sub_name'] = "FGSO-%s-%s" % ( initial, count+1 )
            
        id = super(sale_order, self).create(cr, uid, vals, context)
        return id
    
    
    def onchange_partner_id(self, cr, uid, ids, part):
        if not part:
            return {'value': {'partner_shipping_id': False}}
        partner_obj = self.pool.get('res.partner')
        addr = partner_obj.address_get(cr, uid, [part], ['default'])['default']
        
        
        return {'value': {'partner_shipping_id':addr}}
    
    def button_review(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 
            'state': 'done', 
            'confirmer_id': uid, 
            'date_confirm': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            }
        )
        return True
    
    def button_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 
            'state': 'cancel', 
            'confirmer_id': uid, 
            'date_confirmed': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            }
        )
        return True
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', '订单名称不能重复!'),
    ]
    _order = 'name desc'
    
class sale_order_line(osv.osv):
    _name = "fg_sale.order.line"
    _description = "富光业务部销售订单明细"
    
    
    _columns = {
        'order_id': fields.many2one('fg_sale.order', '订单', required=True, ondelete='cascade', select=True),
        'sequence': fields.integer('Sequence'),
        'product_id': fields.many2one('product.product', '产品', domain=[('sale_ok', '=', True)], change_default=True),
        'product_uom': fields.many2one('product.uom', ' 单位', required=True),
        'product_uom_qty': fields.float('单位数量', required=True),
        'aux_qty': fields.float('总只数', required=True),
        'unit_price': fields.float('单位价格', required=True),
        'discount_amount': fields.float(''),
        'subtotal_amount': fields.float('小计'),
        'note': fields.char('附注', size=100),
    }
    
    def product_id_change(self, cr, uid, ids, product_id, context=None):
        if not product_id:
            return {'domain': {}, 'value':{'product_uom':'', 'product_uom_qty':0, 'price_discount':0,'price_subtotal':0}}
        result = {}
        product_obj = self.pool.get('product.product')
        
        product = product_obj.browse(cr, uid, product_id, context=context)
        result['product_uom'] = product.uom_id.id
        
        return {'value': result}
    
    def _get_amount(self,cr,uid, ids, product_id, uom_id, context=None):
        if product_id and product_uom and qty:
            product_obj = self.pool.get('product.product')
            
            product = product_obj.browse(cr, uid, product_id, context=context)
            if product:
                price = product.lst_price
                return {'value': {'price_subtotal':price, 'price_discount':price}}
        return {'value':{}}
    
    
    def product_uom_id_change(self, cr, uid, ids, product_id, uom_id, context=None):
        return {'value': {'product_uom_qty':0, 'price_discount':0, 'price_subtotal':0}}
    
    
    def product_uom_qty_change(self, cr, uid, ids, product_id, product_uom, qty, context=None):
        if product_id and product_uom and qty:
            product_obj = self.pool.get('product.product')
            #product_uom_obj = self.pool.get('product.uom')
            product = product_obj.browse(cr, uid, product_id, context=context)
            if product:
                price = product.lst_price * product.uom_id.factor * qty
                
                return {'value': {'price_subtotal':price, 'price_discount':price}}
        return {'value':{}}
        
    _order = 'sequence, id asc'

class sale_print_log(osv.osv):
    _name = "fg_sale.print.log"
    
    _columns = {
        'user_id': fields.many2one('res.users', '打印人'),
        'date_print': fields.date('打印日期'),
        'order_id': fields.many2one('fg_sale.order', '订单', required=True, ondelete='cascade', select=True),
    }
    
    _order = 'date_print, id'
    
    
    _defaults = {
        'date_print': fields.date.context_today,
        'user_id': lambda obj, cr, uid, context: uid,
    }