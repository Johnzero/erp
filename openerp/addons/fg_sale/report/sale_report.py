# -*- coding: utf-8 -*-


import tools
from osv import fields, osv

class sale_report_by_month(osv.osv):
    _name = "fg_sale.order.report.monthly"
    _auto = False
    _rec_name = 'month'
    
    _columns = {
        'year': fields.char('年份', size=4, readonly=True),
        'month': fields.selection([(1.0, '一月'), (2.0, '二月'), (3.0, '三月'), (4.0, '四月'),
            (5.0, '五月'), (6.0, '六月'), (7.0, '七月'), (8.0, '八月'), (9.0, '九月'),
            (10.0, '十月'), (11.0, '十一月'), (12.0, '十二月')], '月份', readonly=True),
        'amount': fields.float('金额'),
        'source':fields.char('事业部', size=10),
    }
    _order = 'year desc, month desc'
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'fg_sale_order_report_monthly')
        cr.execute("""
            create or replace view fg_sale_order_report_monthly as (
            SELECT 
              min(l.id) as id,
              extract(month FROM s.date_order) AS month,
              extract(year FROM s.date_order) AS year,
              sum(l.subtotal_amount) as amount,
              p.source as source
            FROM 
              public.fg_sale_order_line l 
            left join product_product p on (l.product_id=p.id) 
            left join fg_sale_order s on (l.order_id=s.id) 
             group by p.source,month, year
            order by year desc, month desc
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