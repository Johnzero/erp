# -*- encoding: utf-8 -*-

import sys
import os

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

xml_temp = """<?xml version="1.0" encoding="utf-8"?>
<openerp>
    <data>
		%s
		</data>
	</openerp>
"""

color_xml = """
<record id="pick_item_color_%s" model="fuguang.picking.item.color">
    <field name="item_id" ref="pick_item_%s"/>
    <field name="color">%s</field>
    <field name="sequence">%s</field>
</record>
"""

color_none_xml = """
<record id="pick_item_color_%s" model="fuguang.picking.item.color">
    <field name="item_id" ref="pick_item_%s"/>
    <field name="color">无_透明</field>
    <field name="sequence">%s</field>
</record>
"""

item_xml = """
<record id="pick_item_%s" model="fuguang.picking.item">
	<field name="category">%s</field>
    <field name="name">%s</field>
	<field name="code">%s</field>
	<field name="sequence">%s</field>
	<field name="uoms" eval="[%s]"/>
	<field name="price">%s</field>
	<field name="volume">%s</field>
</record>
"""

uom_xml = """<record id="pick_item_uom_%s" model="fuguang.picking.item.uom">
            <field name="name">件(%s只)</field>
        	<field name="factor">%s</field>
        </record>
"""

# 
# def gen_temp():    # 
#     csv = open('20111219.csv', 'r')
#     lines = csv.readlines()
#     csv.close()
#     html = ''
#     html_file = open('temp.html','w')
#     last_item = None
#     for line in lines:
#       data = line.strip().split(',')
#       if '待插入产品' in data: continue
#       if len(data) != 4: continue
#     
#       if data[1] and data[2]:
#           if last_item:
#               #save it.
#               l = len(last_item['color'])
#               cate = last_item['cate']
#               name = last_item['name']
#               code = last_item['code']
#               colors = last_item['color']
#               
#               html_file.write("""
#                   <tr>
#                       <td>%s</td>
#                       <td rowspan="%s">%s</td>
#                       <td rowspan="%s">%s</td>
#                       <td>%s</td>
#                       <td>${ get_value(hash('%s'+'%s'), 'qty') }</td>
#                       <td>${ get_value(hash('%s'+'%s'), 'uom') }</td>
#                   </tr>
#               """ % ( cate, l, name, l, code, colors[0], code, colors[0], code, colors[0] ))
#               for c in colors[1:]:
#                   html_file.write("""
#                   <tr>
#                       <td>%s</td>
#                       <td>%s</td>
#                       <td>${ get_value(hash('%s'+'%s'), 'qty') }</td>
#                       <td>${ get_value(hash('%s'+'%s'), 'uom') }</td>
#                   </tr>
#                   """ % (cate, c, code, c, code, c))
#     
#               last_item = None
#               
#           
#           item = { 'cate':data[0], 'name':data[1], 'code':data[2], 'color':[ data[3] ] }
#           last_item = item
#           
#       else:
#           if last_item:
#               last_item['color'].append(data[3].replace(' ', ''))
#     
#     html_file.close()

#gen_temp()


def gen_xml():
	xml = ''
	
	xml_file = open('items.xml','w')

	price_file = open('prices.csv', 'r')
	price_data = {}
    
	p_list = price_file.readlines()
	price_file.close()
    
	uom_data_list = []
	for l in p_list:
	    if l and ',,,,' not in l:
	        l_list = l.strip().split(',')
	        if len(l_list) == 6:
	            code = l_list[2].strip().replace('型','')
	            uom = l_list[3].strip()
	            vol = l_list[4].strip()
	            price = l_list[5].strip()
	            if uom not in uom_data_list:
	                uom_data_list.append(uom)
	            price_data[code] = { 'uom': uom, 'vol':vol, 'price':price}
	            
	print 'got price_data', len(price_data)
	#get uom data:
	for u in uom_data_list:
		if '件' in u:
		    u = u.replace('件(','').replace('只)','')
		    xml = xml + (uom_xml % (u, u, u))
    
	csv = open('20120312.csv', 'r')
	lines = csv.readlines()
	csv.close()
	
	last_item_id = ''
	
	item_count = 1
	color_count = 1
	
	for line in lines:
		line = line.strip()
		if line == ',,,': continue
		
		data = line.split(',')
		
		if len(data) == 4:
			if '待插入产品' in data:
				continue
			if data[1] and data[2]:
				item_count = item_count + 1
				color_count = color_count + 1

				last_item_id = item_count

				cate = data[0].strip()
				name = data[1].strip()
				code = data[2].strip().replace('型','')
				
				uoms = ""
				us = price_data.get(code)
				s_s = "(6, 0, [ref('base_pick_item_uom'),ref('pick_item_uom_%s')])"
				if us and us.get('uom'):
					uom_s = us.get('uom')
					uoms = s_s % uom_s.replace('件(','').replace('只)','')
					xml = xml + (item_xml % (item_count, cate, name, code, item_count*100, uoms, us.get('price','0'),us.get('vol','')))
				else:
					print '%s,%s' % (name,code)
			else:
				#save color
				color_count = color_count + 1
			
			if data[3]:
				xml = xml + (color_xml % (color_count, last_item_id, data[3].replace(' ', ''), color_count*10))
			else:
				xml = xml + (color_none_xml % (color_count, last_item_id, color_count*10))
		
	xml_file.write(xml_temp % xml)
	xml_file.close()
	
	
gen_xml()