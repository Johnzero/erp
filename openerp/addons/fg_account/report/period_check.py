# -*- coding: utf-8 -*-


import tools
from osv import fields, osv

class period_check(osv.osv):
    _name = "fg_account.period.check"
    _auto = False
    _rec_name = 'ref_doc'
    _columns = {
        'ref_doc':fields.reference('单据', selection=[('fg_sale.order','销售订单'),('fg_account.bill','收款单')], 
                size=128, readonly=True),
        'o_date': fields.date('单据日期', readonly=True),
        'name':fields.char('单号', size=24),
        'o_partner': fields.many2one('res.partner', '客户', readonly=True),
        't':fields.char('项目', size=12, readonly=True),
        'reconciled':fields.boolean('已对账', readonly=True),
        'cleared':fields.boolean('已清账', readonly=True),
        'amount': fields.float('金额', digits=(16,4), readonly=True),
        'due_date_from':fields.function(lambda *a,**k:{}, method=True, type='date',string="开始日期"),
        'due_date_to':fields.function(lambda *a,**k:{}, method=True, type='date',string="结束日期"),
        'note':fields.text('附注'),
    }
    _order = 'o_date asc'
    
    def button_clear(self, cr, uid, ids, context=None):
        order_obj = self.pool.get('fg_sale.order')
        #this should all be order.
        #check_record's id IS the id of order.
        order_obj.write(cr, uid, ids, {'clear':True})

        return True
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'fg_account_period_check')
        cr.execute("""
            create or replace view fg_account_period_check as (
            (
            	SELECT
            		o."id" AS ID,
            		o.name as name,
            		'fg_sale.order,' || o."id" AS ref_doc,
            		o.date_confirm AS o_date,
            		o.partner_id AS o_partner,
            		'发货额' AS T,
            		o.reconciled AS reconciled,
            		SUM(line.subtotal_amount)AS amount,
            		o.note AS note,
            		o.clear as cleared
            	FROM
            		fg_sale_order_line line
            	JOIN fg_sale_order o ON o."id" = line.order_id
            	WHERE
            		o."state" = 'done'
            	AND NOT o.minus
            	GROUP BY
            		o. ID,
            		o."name",
            		o.date_confirm,
            		o.partner_id
            )
            UNION ALL
            	(
            		SELECT
            			o."id" AS ID,
            			o.name as name,
            			'fg_sale.order,' || o."id" AS ref_doc,
            			o.date_confirm AS o_date,
            			o.partner_id AS o_partner,
            			'退回' AS T,
            			o.reconciled AS reconciled,
            			SUM(line.subtotal_amount)AS amount,
            			o.note AS note,
            			o.clear as cleared
            		FROM
            			fg_sale_order_line line
            		JOIN fg_sale_order o ON o."id" = line.order_id
            		WHERE
            			o."state" = 'done'
            		AND o.minus
            		GROUP BY
            			o. ID,
            			o."name",
            			o.date_confirm,
            			o.partner_id
            	)
            UNION ALL
            	(
            		SELECT
            			(bill."id"+ 1000000000) AS ID,
            			bill.name as name,
            			'fg_account.bill,' || bill."id" AS ref_doc,
            			bill.date_check AS o_date,
            			bill.partner_id AS o_parnter,
            			cate."name" AS T,
            			bill.reconciled AS reconciled,
            			bill.amount AS amount,
            			bill.note AS note,
            			False as cleared
            		FROM
            			fg_account_bill bill
            		JOIN fg_account_bill_category cate ON bill.category_id = cate. ID
            		WHERE
            			bill."state" IN('check', 'done')
            	)
            )
            """)
            