# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
# -*- encoding: utf-8 -*-
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from tutorial.items import DmozItem
from scrapy.shell import inspect_response
import re
import xlrd
import os
#http://s.etao.com/search?q=fgl&sort=price-asc&mt=144&s=0#filterbar

class DmozSpider(BaseSpider):
	
    name = "dmoz"
    allowed_domains = ["http://s.etao.com"]
    dirf = os.path.abspath(".")
    wkb = xlrd.open_workbook(dirf+"\\updateitems.xls")
    sheet = wkb.sheets()[0]
    
    itemname = []
    for rows in range(sheet.nrows):
	if rows >0:
	    itemname.append(sheet.cell(rows,0).value)
	
    urls = []
    for product in itemname:
	for num in range(4):
	    urls.append("http://s.etao.com/search?&q="+product+"&sort=price-asc" + "&s=" + str(num*40)) 
		
    start_urls = [it for it in urls]
    
    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        sites = hxs.select('//div[@class="griditem"]')
        items = []
        for site in sites:
	    item = DmozItem()          
	    item['title'] = site.select('div/a[@class="LS_history"]').extract()[0]
	    item['link'] = site.select('div/div/a[@class="label-m-info"]').extract()[0]
	    items.append(item)
        return items
    
    
