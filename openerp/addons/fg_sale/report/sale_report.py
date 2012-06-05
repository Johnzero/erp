# -*- coding: utf-8 -*-


import tools
from osv import fields, osv


class report_product_source_grid(osv.osv_memory):
    _name = 'fg_sale.product.source.summary.grid'
    _description = '事业部销售汇总'
    
    def create(self, cr, uid, vals, cotext=None):
        raise osv.except_osv('Error !','You cannot add an entry to this view!')
    
    def unlink(self, *args, **argv):
        raise osv.except_osv('Error !', 'You cannot delete an entry of this view !')
    
    def write(self, cr, uid, ids, vals, context=None):
        raise osv.except_osv('Error !', 'You cannot write an entry of this view !')
    
    def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        pass
    
    def fields_get(self, cr, uid, view_id=None,view_type='form',context={},toolbar=False):
        result = super(report_product_source_grid, self).fields_get(cr, uid, fields, context)
        result['line_num'] = {'string': '行号/列号','type': 'char','size': 7}
        
        return result
    
    def fields_view_get(self, cr, uid, view_id=None,view_type='form',context={},toolbar=False):
        result = super(report_product_source_grid, self).fields_view_get(
                cr, uid, view_id, view_type, context=context, toolbar=toolbar)
        xml = """<?xml version="1.0"?><%s>"""
        result['arch'] = xml
        return result

class sale_report_by_day(osv.osv):
    _name = "fg_sale.order.report.daily"
    _auto = False
    _rec_name = 'date'
    
    _columns = {
        'date': fields.char('月份', size=12, readonly=True),
        'amount': fields.float('金额'),
        'source':fields.char('事业部', size=10),
    }
    _order = 'date asc'

    def init(self, cr):
           tools.drop_view_if_exists(cr, 'fg_sale_order_report_daily')
           cr.execute("""
               create or replace view fg_sale_order_report_daily as (
               SELECT
               min(line.id) as id,
               	o.date_confirm as date,
               	product."source",
               	SUM(line.subtotal_amount) as amount
               FROM
               	fg_sale_order_line line
               JOIN fg_sale_order o ON o."id" = line.order_id
               JOIN product_product product ON product."id" = line.product_id
               JOIN res_partner partner ON partner."id" = o.partner_id
               WHERE
               	o."state" = 'done' 
               GROUP BY
               	product."source",
               	o.date_confirm
               )
               """)
               

class sale_report_by_month(osv.osv):
    _name = "fg_sale.order.report.monthly"
    _auto = False
    _rec_name = 'month'
    
    _columns = {
        'date': fields.char('月份', size=12, readonly=True),
        'year': fields.char('年份', size=12, readonly=True),
        'month': fields.char('月份', size=12, readonly=True),
        'amount': fields.float('金额'),
        'source':fields.char('事业部', size=10),
    }
    _order = 'date asc'
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'fg_sale_order_report_monthly')
        cr.execute("""
            create or replace view fg_sale_order_report_monthly as (
            SELECT 
              min(l.id) as id,
              to_char(s.date_order, 'YYYY-MM') as date,
              to_char(s.date_order, 'YYYY') as year,
              to_char(s.date_order, 'MM') as month,
              sum(l.subtotal_amount) as amount,
              p.source as source
            FROM 
              public.fg_sale_order_line l 
            left join product_product p on (l.product_id=p.id) 
            left join fg_sale_order s on (l.order_id=s.id)
            where s.state = 'done' or s.minus = TRUE 
             group by p.source,date, year, month
            order by date asc 
            )""")


# class sale_report(osv.osv):
#     _name = "fg_sale.order.report"
#     _description = "Sales Orders Statistics"
#     _auto = False
#     _rec_name = 'date'
#     
#     _columns = {
#         'date': fields.date('日期', readonly=True),
#         'date_confirm': fields.date('审核日期', readonly=True),
#         'year': fields.char('年份', size=4, readonly=True),
#         'month': fields.selection([('01', '一月'), ('02', '二月'), ('03', '三月'), ('04', '四月'),
#             ('05', '五月'), ('06', '六月'), ('07', '七月'), ('08', '八月'), ('09', '九月'),
#             ('10', '十月'), ('11', '十一月'), ('12', '十二月')], '月份', readonly=True),
#         'day': fields.char('日期', size=128, readonly=True),
#         'week':fields.float('星期'),
#         'partner_id': fields.many2one('res.partner', 'Partner', readonly=True),
#         'user_id': fields.many2one('res.users', 'Salesman', readonly=True),
#         'nbr': fields.integer('记录数', readonly=True),
#         'product_id': fields.many2one('product.product', '产品', readonly=True),
#         'cate_id':fields.many2one('product.category', '产品分类', readonly=True),
#         'aux_qty':fields.float('数量'),
#         'subtotal_amount':fields.float('金额', digits=(16,4)),
#         'subtotal_amount_o':fields.float('折前金额', digits=(16,4)),
#         'discount':fields.float('折扣', digits=(16,4)),
#         'source':fields.char('来源', size=40),
#         
#     }
#     
#     _order = 'date desc'
#     
#     def init(self, cr):
#         tools.drop_view_if_exists(cr, 'fg_sale_order_report')
#         cr.execute("""
#             create or replace view fg_sale_order_report as (
#                 select l.id as id, 
#                         1 as nbr,
#                       s.date_order as date,
#                         s.date_confirm as date_confirm,
#                         extract(year FROM s.date_order) AS year,
#                         extract(month FROM s.date_order) AS month,
#                         to_char(s.date_order, 'yyyy-mm-dd') AS date,extract(week FROM s.date_order) AS week,
#                         s.partner_id as partner_id,
#                         s.user_id as user_id,
#                         l.product_id as product_id,
#                         pc.id as cate_id,
#                         l.aux_qty,
#                         l.subtotal_amount,
#                         (l.aux_qty * l.unit_price) as subtotal_amount_o,
#                         ((l.aux_qty * l.unit_price) - l.subtotal_amount) as discount,
#                         p.source
#                 from fg_sale_order s 
#                 left join fg_sale_order_line l on (s.id=l.order_id) 
#                 left join product_product p on (l.product_id=p.id) 
#                 left join product_template t on (p.product_tmpl_id=t.id)
#                 left join product_category pc on (pc.id=t.categ_id) 
#                 where s.state = 'done'
#                 group by l.id, l.product_id,
#                 s.date_order,
#                 s.date_confirm,
#                 s.partner_id,
#                 s.user_id, l.aux_qty, l.subtotal_amount, p.source, pc.id
#             )
#         """)
#     