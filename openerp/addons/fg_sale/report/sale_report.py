# -*- coding: utf-8 -*-


import tools
from osv import fields, osv


class sale_report_by_day(osv.osv):
    _name = "fg_sale.order.report.daily"
    _auto = False
    _rec_name = 'date'
    
    _columns = {
        'date': fields.char('月份', size=12, readonly=True),
        'amount': fields.float('金额'),
        'source':fields.char('事业部', size=10),
        'partner_id':fields.many2one('res.partner', '客户'),
    }
    _order = 'date asc'

    def init(self, cr):
           tools.drop_view_if_exists(cr, 'fg_sale_order_report_daily')
           cr.execute("""
               create or replace view fg_sale_order_report_daily as (
               SELECT
                        MIN (line. ID) AS ID,
                        o.date_confirm AS DATE,
                        product."source",
                        o.partner_id,
                        SUM (line.subtotal_amount) AS amount
                FROM
                        fg_sale_order_line line
                JOIN fg_sale_order o ON o."id" = line.order_id
                JOIN product_product product ON product."id" = line.product_id
                JOIN res_partner partner ON partner."id" = o.partner_id
                WHERE
                        o."state" = 'done'
                GROUP BY
                        product."source",
                        o.partner_id,
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

