# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

from scrapy.exceptions import DropItem
import sys
import json
import re
import datetime

class GetstorePipeline(object):
    
    def __init__(self):
        self.file = open('importstore.json', 'wb')
    def process_item(self, item, spider):
        
        reload(sys)
        sys.setdefaultencoding('utf8')
        
        if len(item["link"])<1500:
            return item
        reg1 = 'class="seller">(.*)</a>'
        st = re.findall(reg1,item["link"])
        reg2 = 'href="(\S*)".*>(.*)'
        st2 = re.findall(reg2,st[0])
        
        reg3 = 'class="summary"(.*)</a>'
        st3 = re.findall(reg3,item["link"])
        reg4 = 'href="(\S*)".*title="(.*?)">'
        st4 = re.findall(reg4,st3[0])
        string = str(st4[0][0]).replace('amp;','')
        
        reg5 = 'class="loc">(.*?)<'
        st5 = re.findall(reg5,item["link"])
        if not st5:
            reg5 = 'class="place">(.*?)<'
            st5 = re.findall(reg5,item["link"])

        reg6 = 'class="price"><em>(.*)</em>'
        st6 = re.findall(reg6,item["link"])
        
        #reg7 = 'person-count>(.*)</span>'
        #st7 = re.findall(reg7,item["link"])
        reg7 = 'class="price.*?<span>(.*)</span>'
        st7  = re.findall(reg7,item["link"])
        
        cdate = datetime.date.today().strftime("%Y-%m-%d")
        
        self.file.write('"href":'+'"'+st2[0][0]+'"'+','+
                        '"name":'+'"'+st2[0][1]+'"'+','+
                        '"title":'+'"'+st4[0][1]+'"'+','+
                        '"itemHref":'+'"'+string+'"'+','+
                        '"place":'+'"'+st5[0]+'"'+','+
                        '"price":'+'"'+st6[0]+'"'+','+
                        '"sale":'+'"'+st7[0]+'"'+','+
                        '"date":'+'"'+cdate+'"'+"\n")
        
        
        return item
