# -*- encoding: utf-8 -*-
import pooler, time
from osv import fields, osv

class competitor(osv.osv):
    _name = "fg_competitor.competitor"
    _description = "竞争对手"
                   
    _columns = {
        'name': fields.char('公司名', size=128, select=True, required=True),
        'address':fields.char('所在地', size=128, select=True),
        'website':fields.char('网站', size=128),
        'brands':fields.one2many('fg_competitor.brand', 'competitor_id', '品牌'),
        'note': fields.text('说明'),
    }
    
    
class brand(osv.osv):
    _name = "fg_competitor.brand"
    _description = "竞争品牌"
    
    _columns = {
        'competitor_id': fields.many2one('fg_competitor.competitor', '竞争对手', required=True, ondelete='cascade', select=True),
        'name': fields.char('品牌', size=128, select=True, required=True),
        'products': fields.one2many('fg_competitor.product', 'brand_id', '产品'),
        
        'note': fields.text('说明'),
    }
    

class product(osv.osv):
    _name = "fg_competitor.product"
    _description = "产品"
    
    _columns = {
        'brand_id': fields.many2one('fg_competitor.brand', '品牌', required=True, ondelete='cascade', select=True),
        'name': fields.char('名称', size=128, select=True, required=True),
        'model': fields.char('编号', size=128),
        'year': fields.char('发布年份', size=128),
        'meterial': fields.selection([('glass', '玻璃'), ('stainless', '不锈钢'),
            ('pc','PC'), ('pp','PP'), ('etc','其它')], '材质', select=True),
        'color':fields.char('颜色', size=128),
        'style':fields.char('风格', size=128),
        'capacity':fields.integer('容量', size=128),
        'url':fields.char('链接', size=128),
        'photo':fields.binary('图片'),
        'note': fields.text('说明'),
    }