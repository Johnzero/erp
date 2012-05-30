# -*- coding: utf-8 -*-


import tools
from osv import fields, osv

class period_check(osv.osv):
    _name = "fg_account.period.check"
    _auto = False
    _rec_name = 'name'
    _columns = {
    
    }

"""
(
	SELECT
		o. ID AS o_id,
		o."name" AS o_name,
		o.date_confirm AS o_date,
		o.partner_id AS o_partner,
		'发货额' AS T,
		SUM(line.subtotal_amount)AS amount
	FROM
		fg_sale_order_line line
	JOIN fg_sale_order o ON o."id" = line.order_id
	WHERE
		o."state" = 'done'
	AND NOT o.minus
	AND o.date_confirm >= to_date('2012-04-30', 'YYYY-MM-DD')
	GROUP BY
		o. ID,
		o."name",
		o.date_confirm,
		o.partner_id
)
UNION ALL
	(
		SELECT
			o. ID AS o_id,
			o."name" AS o_name,
			o.date_confirm AS o_date,
			o.partner_id AS o_partner,
			'退回' AS T,
			SUM(line.subtotal_amount)AS amount
		FROM
			fg_sale_order_line line
		JOIN fg_sale_order o ON o."id" = line.order_id
		WHERE
			o."state" = 'done'
		AND o.minus
		AND o.date_confirm >= to_date('2012-04-30', 'YYYY-MM-DD')
		GROUP BY
			o. ID,
			o."name",
			o.date_confirm,
			o.partner_id
	)
UNION ALL
	(
		SELECT
			bill."id" AS o_id,
			bill."name" AS o_name,
			bill.date_check AS o_date,
			bill.partner_id AS o_parnter,
			cate."name" AS T,
			bill.amount AS amount
		FROM
			fg_account_bill bill
		JOIN fg_account_bill_category cate ON bill.category_id = cate. ID
		WHERE
			bill."state" = 'done'
	)
"""