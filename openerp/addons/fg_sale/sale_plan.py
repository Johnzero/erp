# -*- encoding: utf-8 -*-
import pooler, time
from osv import fields, osv

class annual_plan(osv.osv):
    _name = "fg_sale.annual.plan"
    _description = "富光年度计划单"
    
    _columns = {
        'name': fields.char('年度', size=64, ),
        'date_plan': fields.date('制定日期', select=True),
        'user_id': fields.many2one('res.users', '制定人', select=True, readonly=True),
        'plan_line': fields.one2many('fg_sale.annual.plan.line', 'plan_id', '明细',),
        'note': fields.text('附注'),
    }
    
    _defaults = {
        'date_plan': fields.date.context_today,
        'user_id': lambda obj, cr, uid, context: uid,
    }
    

class annual_plan_line(osv.osv):
    _name = "fg_sale.annual.plan.line"
    _columns = {
        'plan_id': fields.many2one('fg_sale.annual.plan', '计划', required=True, ondelete='cascade', select=True),
        'partner_id': fields.many2one('res.partner', '客户',  required=True, select=True),
        'plastic': fields.float('塑胶事业部', required=True, digits=(16,0)),
        'glass': fields.float('玻璃事业部', required=True, digits=(16,0)),
        'vacuume': fields.float('真空事业部', required=True, digits=(16,0)),
        'note': fields.char('附注', size=60),
    }

