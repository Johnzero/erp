# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from getstore.items import GetstoreItem
from scrapy.shell import inspect_response
import re
import xlrd
import os,sys
import urllib2
#http://s.etao.com/search?q=fgl&sort=price-asc&mt=144&s=0#filterbar

class ItemSpider(BaseSpider):
	
    name = "item"
    allowed_domains = ["http://s.taobao.com/"]
    reload(sys)
    #socket.setdefaulttimeout(8.0)
    sys.setdefaultencoding('utf8')
    
    dirf = os.path.abspath('.')
    print dirf,"@@@@@@@"
    wkb = xlrd.open_workbook(dirf+"\\FGA.xls")
    sheet = wkb.sheets()[0]
    
    itemname = []
    for rows in range(sheet.nrows):
    	if rows >0:
    	    itemname.append(sheet.cell(rows,0).value)
    append = 'http://s.taobao.com/search?&q=%B8%BB%B9%E2'
    urls = []
    for i in itemname:
	urls.append(append+i+'&style=grid')
    print urls
    for url in urls:
	try:
	    request = urllib2.Request(urls[0],headers={"User-Agent":"Mozilla-Firefox5.0"})
	    res = urllib2.urlopen(request)
	except:
	    pass
	data = res.read()
    
	#class="cat-noresult"
	reg3 = 'class="cat-noresult"'
	noresult = re.findall(reg3,data)
	
	if not noresult:
	    
	    reg = 'page-bottom">(.*?)page-skip'
	    reg2 = 'href="(.*?)"'
	    string = re.findall(reg,data)
	    print url,"*************"
	    print string,"***************"
	    string2 = re.findall(reg2,string[0])
	    for urlitem in string2:
		url = "http://s.taobao.com" + urlitem
		if not url in urls:
		    urls.append(url)
	else:
	    continue
    
    #start_urls = ['http://s.taobao.com/search?&q=FZ1002-280&style=grid']
    start_urls=[url for url in urls]
    print start_urls
    def parse(self, response):
        hxs = HtmlXPathSelector(response)
	sites = hxs.select('//li[@class="list-item"]')
	items = []
	for site in sites:
	    item = GetstoreItem()          
	    item["link"] = site.extract()
	    items.append(item)
        #sites = hxs.select('//div[@class="griditem"]')
        return items
    
    
