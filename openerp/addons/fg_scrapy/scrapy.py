# -*- encoding: utf-8 -*-

from osv import osv
from osv import fields
import time
from time import strptime, strftime
import datetime
import os
import re
import xlrd,xlwt
import urllib,urllib2
import base64

class scrapy(osv.osv):
    
    _name = "scrapy"
    
    _description = "Scrapy Schedule Everyday"
    
    def _get_image(self, cr, uid, ids, name, arg, context=None):
        
        res={}
        img = self.read(cr,uid,ids,["itemImg"])
        
        if img[0]["itemImg"]:
            urllib2.socket.setdefaulttimeout(3)
            req = urllib2.Request(img[0]["itemImg"])
            try:
                response = urllib2.urlopen(req) 
            except:
                return res
            value = response.read()
            res[int(ids[0])]= base64.encodestring(value)
        
        return res
    
    

      
    _columns = {
        
        'itemHref':fields.char('商品地址', size=512,),
        
        'itemTitle':fields.char('商铺产品名称', size=128,),
        
        'itemImg':fields.char('图片地址',size=512,),
        
        'itemPrice':fields.float('商品价格'),
        
        'itemStoreImg':fields.char('商城图片',size=256,),
        
        'itemStoreName':fields.char('平台',size=128,),
        
        'itemStoreHref':fields.char('店铺地址',size=512),
        
        'href':fields.char('一淘返利',size=512,),
        
        'date':fields.date('抓取时间',),
        
        'item':fields.char('货号',size=64,),
        
        'standardprice':fields.char('标准价格',size=64,),
        
        'name':fields.char('店铺ID',size=64,),
        
        'image':fields.function(_get_image, method=True, string=u'产品图片', type='binary', store=True), 
        
    }
    
    def run_scheduler(self, cr, uid, ids=None, context=None):
        
        """通过配置里的商品更新xls，读取xls找到要爬取的商品更新start_urls执行scrapy存储到json文件,通过json文件处理数据读取图片(_get_image)写入数据库
        """
        
        #D:\erp\openerp\addons\scrapyscheduled
        absdir = os.path.abspath('.')
        print absdir
        if not '\\fg_scrapy' in absdir:
                absdir = os.path.abspath('.') + "\\openerp\\addons\\fg_scrapy"
        elif '\\getstore' in absdir:
                absdir = absdir.replace('\\getstore','')
        elif '\\tutorial' in absdir:
                absdir = absdir.replace('\\tutorial','')
        xls = absdir + "\\tutorial\\updateitems.xls"
        orfile =  absdir + "\\tutorial\\items.json"     
        filedir = absdir + "\\tutorial\\datatable.json"
        print absdir,"!!!!"
        absdir = absdir +'\\tutorial'
        #删除旧文件
        try :
            os.remove(filedir)
            os.remove(orfile)
        except :
            pass
        
        #更新updateitems.xls
        obj = self.pool.get("scrapy.item")
        cr.execute('SELECT name,standardprice FROM scrapy_item')
        listitem = cr.fetchall()
        if listitem:
            wb = xlwt.Workbook()
            sheet = wb.add_sheet('sheet 1',)
            sheet.write(0,0,'Item')
            sheet.write(0,1,'Price')
            for row in range(len(listitem)):
                sheet.write(row+1,0,listitem[row][0].upper())
                sheet.write(row+1,1,listitem[row][1])
            wb.save(xls)
            #wb = xlrd.open_workbook(xls)
            #newwb = copy(wb)
            #sheet = newwb.get_sheet(0)
            #row = len(sheet.rows)
            #for item in listitem:
                #sheet.write(row,0,item[0])
                #sheet.write(row,1,item[1])
            #newwb.save(xls)
        
        #执行scrapy crawl dmoz
        try:
            os.chdir(absdir)
        except:
            return True
        
        print absdir,"**********"
        print filedir
        print xls
        print orfile
        
        cmd = 'scrapy crawl dmoz -o items.json -t json'
        try:
            os.system(cmd)
        except:
           return True

        #读数据
        try:
            datatable = open(filedir,'rb')
        except:
            return True

        #筛选导入数据库
        for items in datatable.readlines():
            if len(items):
                items =eval("{" + items + "}")
                if float(items['itemPrice']) < float(items['standardprice']):
                    items["itemPrice"] = float(items["itemPrice"])
                    items['itemHref']=items['itemHref'].replace('amp;','')
                    items['itemImg'] = items['itemImg'].replace('.jpg_sum','')
                    items['itemImg'] = items['itemImg'].replace('_sum','')
                    #reg  = '(.*/)(.*)'
                    #imglist  = re.findall(reg,items['itemImg'])
                    #if imglist:
                    #    name1 = imglist[0][-1].split('.')
                    #    del name1[-2]
                    #   name1 = '.'.join(name1)
                    #items['itemImg'] = imglist[0][0] + name1
                    items['itemStoreHref'] = items["itemStoreHref"].replace("amp;",'')
                    items['href'] = items['href'].replace('amp;','')
                    self.create(cr,uid,items)
                    #select name,item,"itemPrice" from scrapy where (name,date,item,"itemPrice") in (select name,date,item,"itemPrice" from scrapy group by name,date,item,"itemPrice" having count(*)>1) and "itemPrice" not in (select min("itemPrice") from scrapy group by name,date,item,"itemPrice" having count(*)>1)
        datatable.close()

        return True
    
    #def create(self,cr,uid,items,context=None):
    #   res = super(scrapy, self).create(cr, uid, items, context=context)
        


scrapy()


class scrapy_item(osv.osv):
    
    _name = "scrapy.item"
    
    #_inherit = "fuguang.picking.item"
    
    _description = "Product"
    
    _columns ={
        
        'name':fields.char('货号', size=40,),

        'category':fields.selection([(u'FGA事业部',u'FGA事业部'),(u'塑胶事业部',u'塑胶事业部'), (u'安全帽事业部',u'安全帽事业部'), 
                                    (u'玻璃事业部',u'玻璃事业部'), (u'真空事业部',u'真空事业部'),(u'塑胶制品',u'塑胶制品'), (u'财务部',u'财务部'),
                                    (u'其他',u'其他')],'相关事业部',),
        
        'barcode':fields.char('条码', size=20),
        
        'standardprice':fields.float('标准价格',),
        
        'sequence': fields.float('序号', digits=(8, 1)),
        
        'state': fields.selection([('presale', '预售'), ('sale', '在售'), ('expiring', '即将停产'), ('expired', '已停产')], '状态'),
        
        'volume':fields.char('体积', size=40),
        
    }
    
    _order = "name asc"
     
    _sql_constraints = [
        ('item_name_unique', 'unique(name)', '货号不能重复...'),
    ]
    
scrapy_item()


    

class scrapy_stores(osv.osv):
    
    _name = "scrapy.stores"
    
    _description = "All Taobao Stores"
    
    _columns={
        
        'name':fields.char('网店',size=64,select=True),
        
        'href':fields.char('网店地址',size=512,),
        
        'itemname':fields.char('品名',size=128,),
        
        'title':fields.char('商品标题',size=128,select=True),
        
        'itemHref':fields.char('商品地址',size=512,),
        
        'place':fields.char('店铺所在地',size=128,),
        
        'price':fields.char('商品价格',size=128,),
        
        'sale':fields.char('销售情况',size=128,),
        
        'date':fields.char('更新时间',size=64),
        
        'items':fields.one2many('scrapy.store.item', 'store_id', '店铺产品'),
        
    }

    def button(self, cr, uid, ids=None, context=None):
        
        ''' '''
        
        absdir = os.path.abspath('.')
        if not '\\fg_scrapy' in absdir:
                absdir = os.path.abspath('.') + "\\openerp\\addons\\fg_scrapy"
        elif '\\getstore' in absdir:
                absdir = absdir.replace('\\getstore','')
        elif '\\tutorial' in absdir:
                absdir = absdir.replace('\\tutorial','')
            
        orfile =  absdir + "\\getstore\\importstore.json"
        adress =   absdir +'\\getstore'
        fi = absdir +'\\getstore\\'+"stores.json"
        print fi,"*********"
        print absdir,'*********'
        try:
            os.chdir(adress)
        except:
            return True
        
        cmd = 'scrapy crawl item -o stores.json -t json'
        
        try:
            os.system(cmd)
        except:
           return True
        
        try:
            datatable = open(orfile,'rb')
        except:
            return True
        
        listvalue = {}
        obj = self.pool.get('scrapy.store.item')
        cr.execute('TRUNCATE scrapy_store_item')
        cr.execute('TRUNCATE scrapy_stores CASCADE')
        cr.commit()
        for items in datatable.readlines():
            if len(items):
                items =eval("{" + items + "}")
                if items["name"] not in listvalue.keys():
                        ids = self.create(cr,uid,items)
                        listvalue[items["name"]]=ids
                itemid = listvalue[items["name"]]
                del items["place"]
                del items["href"]
                del items["name"]
                items.update(store_id=itemid)
                obj.create(cr,uid,items)

        try :
            os.remove(fi)
        except :
            pass
        
        return True
    
scrapy_stores()

class scrapy_store_item(osv.osv):
    
    _name = "scrapy.store.item"
    
    _description = "All Store Items"
    
    _columns={
        
        'store_id':fields.many2one('scrapy.stores','网店',select=True, required=True),
        
        'title':fields.char('商品标题',size=128,select=True),
        
        'price':fields.char('商品价格',size=128),
        
        'itemHref':fields.char('商品地址',size=512,),
        
        'sale':fields.char('销售情况',size=128,),
        
        'date':fields.char('更新时间',size=64),
        
    }
scrapy_store_item()
