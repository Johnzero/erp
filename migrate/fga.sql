# delete orders
DELETE
FROM
	fg_sale_order
WHERE
	partner_id IN(
		SELECT
			partner."id"
		FROM
			res_partner partner
		JOIN res_partner_category_rel rel ON rel.partner_id = partner."id"
		JOIN res_partner_category cate ON cate."id" = rel.category_id
		WHERE
			cate."id" <> 4
	)
OR date_order < to_date('2012-08-01', 'YYYY-MM-DD')

# deactivate partner
UPDATE
	res_partner
SET active = FALSE 
WHERE
	"name" not like '%FGA'

# deactivate partner address
UPDATE res_partner_address
SET active = FALSE
WHERE
	ID IN(
		SELECT
			ID
		FROM
			res_partner
		WHERE
			"name" NOT LIKE '%FGA'
	)
	
# deactivate product.
UPDATE product_product
SET active = FALSE
WHERE
	default_code NOT LIKE 'FZ%'
AND default_code NOT LIKE 'FB%'
AND default_code NOT LIKE 'FS%'
OR default_code is NULL

# update sequence of order.
update fg_sale_order 
set name = replace(name, 'FGSO', 'FGASO')
