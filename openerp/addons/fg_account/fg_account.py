# -*- encoding: utf-8 -*-

from osv import osv
from osv import fields
import time
import tools


class account_bill(osv.osv):
    _name = "fg_account.bill"
    _description = "富光财务部收款单"
    
    
    _columns = {
        'name': fields.char('单号', size=64, select=True, readonly=True),
        'user_id': fields.many2one('res.users', '录入', select=True, readonly=True),
        'date_paying': fields.date('收款日期', select=True),
        'checker_id': fields.many2one('res.users', '审核', select=True, readonly=True),
        'date_check': fields.date('审核日期', readonly=True, select=True),
        'partner_id': fields.many2one('res.partner', '客户', states={'draft': [('readonly', False)]}, select=True),
        'amount': fields.float('金额', digits=(16,4)),
        'state': fields.selection([('draft', '未审核'), ('done', '已审核'), ('cancel','已取消')], '订单状态', readonly=True, select=True),
        'done':fields.boolean('确认'),
        'note': fields.text('附注'),
    }
    
    _defaults = {
        'date_paying': fields.date.context_today,
        'state': 'draft',
        'user_id': lambda obj, cr, uid, context: uid,
        'done':False,
    }
    
    def copy(self, cr, uid, id, default={}, context=None):
        raise osv.except_osv('不允许复制', '单据不允许复制.')
    
    def create(self, cr, uid, vals, context=None):
        if not vals.has_key('name'):
            obj_sequence = self.pool.get('ir.sequence')
            vals['name'] = obj_sequence.get(cr, uid, 'fg_account.bill')
        
        return super(account_bill, self).create(cr, uid, vals, context)
    
    #钱总确认.
    def button_shou(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 
            'done': True, 
            }
        )
        return True
    
    #钱总确认.
    def button_suan(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 
            'done': False, 
            }
        )
        return True
    
    def button_review(self, cr, uid, ids, context=None):
        
        bill_ids = []
        for bill in self.browse(cr, uid, ids, context):
            if not bill['partner_id']:
                bill_ids.append(bill['name'])
        if bill_ids:
            raise osv.except_osv('未确认客户的单据', '以下单据还没有确认用户: %s' % ','.join(bill_ids))
        
        self.write(cr, uid, ids, { 
            'state': 'done', 
            'checker_id': uid, 
            'date_check': time.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)
            }
        )

        return True
    
    
    def button_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 
            'state': 'cancel', 
            'checker_id': uid, 
            'date_check': time.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)
            }
        )
        return True