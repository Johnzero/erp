# -*- encoding: utf-8 -*-

import pooler, time
from osv import fields, osv

class competitor(osv.osv):
    
    _name = "fg_competitor.competitor"
    _description = "competitor"
                   
    _columns = {
        
        'name': fields.char('公司名', size=128, select=True, required=True),
        
        'address':fields.char('所在地', size=128, select=True),
        
        'website':fields.char('网站', size=128),
        
        'brands':fields.one2many('fg_competitor.brand', 'competitor_id', '品牌'),
        
        'note': fields.text('说明'),
        
        'detail':fields.text("公司简介",size=512),
        
        'short':fields.char("口号",size=512,),
    }
    
    _sql_constraints=[('name_unique','unique(name)','公司名称不能重复!')]
    
class brand(osv.osv):
    
    _name = "fg_competitor.brand"
    _description = "competitor.brand"
    
    _columns = {
        
        'competitor_id': fields.many2one('fg_competitor.competitor', '公司全称', required=False, ondelete='cascade', select=True),
        
        'name': fields.char('品牌', size=128, select=True, required=True),
        
        'products': fields.one2many('fg_competitor.product', 'brand_id', '产品'),
        
        'note': fields.text('说明'),
        
    }
    
    _sql_constraints=[('name_unique','unique(name)','品牌不能重复!')]
    

class product(osv.osv):
    
    _name = "fg_competitor.product"
    _description = "competitor.product"
    
    _columns = {
        
        'brand_id': fields.many2one('fg_competitor.brand', '品牌', required=False, ondelete='cascade', select=True),
        
        'name': fields.char('名称', size=128, select=True, required=True),
        
        'model': fields.char('编号', size=128),
        
        'year': fields.char('发布年份', size=128),
        
        'meterial': fields.selection([('glass', '玻璃'), ('stainless', '不锈钢'),
                                    ('pc','PC'), ('pp','PP'), ('etc','其它')], '材质', select=True),
        
        'price':fields.char('价格', size=128),
        
        'color':fields.char('颜色', size=128, select=True),
        
        'style':fields.char('风格', size=128),
        
        'capacity':fields.char('容量', size=128, select=True),
        
        'url':fields.char('链接', size=128),
        
        'tags':fields.many2many('fg_competitor.product.tag','ref_fg_competitor_product_tag','product_id','tag_id','标签'),
        
        'photo':fields.binary('图片'),
        
        
    
    }

class product_tag(osv.osv):
    
    _name = "fg_competitor.product.tag"
    _description = "product_tag"
    
    _columns = {
        
        "tag":fields.integer("标签"),
        
        "attribute":fields.char("属性", size=128),
        
    }