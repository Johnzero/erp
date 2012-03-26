#!/usr/bin/env python
# encoding: utf-8
"""
process.py

Created by Daniel Yang on 2011-08-22.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import os

xml = """<?xml version="1.0" encoding="utf-8"?>
<openerp>
    <data>
        <!--
        Resource: res.partner
        -->
		%s
		</data>
	</openerp>
"""

template = """
<record id="res_partner_%s" model="res.partner">
    <field name="name">%s</field>
    <field eval="[(6, 0, [ref('res_partner_category_%s')])]" name="category_id"/>
    <field name="customer">1</field>
</record>
<record id="res_partner_address_%s" model="res.partner.address">
    <field name="city">%s</field>
    <field name="name">%s</field>
    <field name="country_id" search="[('model','=','res.country'),('name','=','China')]"/>
    <field name="state_id" search="[('model','=','res.country.state'),('name','=','%s')]"/>
    <field name="mobile">%s</field>
    <field name="phone">%s</field>
    <field name="street">%s</field>
    <field name="type">default</field>
    <field name="partner_id" ref="res_partner_%s"/>
</record>
"""

cates = ['一级经销商', '订制杯客户', '二级经销商', 'FGA客户', '富光专卖店']


def main():
	file_input = open('20120229.txt', 'r')
	lines = file_input.readlines()
	file_input.close()
	i = 1
	file_output = open('customer.xml', 'w')
	doc = ""
	for line in lines:
	    data = line.split(',') #got 11 elm.
	    print data[2]
	    c = 0
	    cus = template % (i, data[0], c, i, data[4], data[0], data[5], data[2], data[3], data[1], i)
	    i = i + 1
	    doc = doc + cus
	
	file_output.write(xml % doc)
	file_output.close()
	print 'ok'
    
if __name__ == '__main__':
	main()

