# -*- encoding: utf-8 -*-

from osv import osv, fields
import time, tools

class fg_online_shop_company(osv.osv):

    _name = 'fg_online_shop.company'
    _description = "经销商"

    _columns = {
        'date_created': fields.date('创建日期', readonly=True),
        'partner_id': fields.many2one('res.partner', '上级经销商', required=False),
        'company_name': fields.char('经销商公司名',size=64,select=True),
        'name':fields.char('法定代表人姓名', size=64, select=True, required=True),
        'phone':fields.char('法定代表人手机号',size=64),
        'license':fields.char('营业执照号',size=64),
        'idc_number':fields.char('法定代表人身份证',size=64),
        'address':fields.char('公司地址',size=128),
        'tel':fields.char('责任人电话',size=64),
        'qq':fields.char('QQ',size=128),
        'email':fields.char('Email',size=64),
        'fax': fields.char('Fax', size=64),
        'is_entity': fields.selection([('True','是'),('False','否')],'是否有实体店铺'),
        'manager':fields.char('负责人',size=64),
        
        'company_scale':fields.integer('公司规模'),
        'shops':fields.one2many('fg_online_shop.shop', 'company_id', '网店'),
        "website":fields.char("官网", size=64),
        'note':fields.text('备注'),
    }

    _defaults = {
        'date_created': fields.date.context_today,
    }
    
    _sql_constraints=[('online_shop_name_unique','unique(name)','法定代表人姓名不能重复!')]
    

class fg_online_shop_shop(osv.osv):
    _name = 'fg_online_shop.shop'
    _description = "网店"
    
    _columns = {
        'company_id': fields.many2one('fg_online_shop.company','经销商',select=True, required=True),
        'name': fields.char("网店名称",size=64,select=True, required=True),
        'manager':fields.char('责任人',size=64, required=False),
        'date_started':fields.char('经营年限',size=64),
        'url':fields.char('网店网址',size=128, required=False),
        'phone':fields.char('法定代表人手机号',size=64, required=False),
        
        'level':fields.char('店铺等级',size=32),
        'platform':fields.selection([('taobao', '淘宝店'), ('tmall', '天猫商城'), ('360buy', '京东商城'),
            ('amazon', '亚马逊'), ('paipai', '拍拍'), ('independent', '独立'), ('etc', '其他')], '平台', required=False),
        'brand':fields.char('经营品牌',size=128, help='包括非富光的请详细写清楚', required=False),
        'sale_amount':fields.char('年销售规模', size=64),
        'note':fields.text('附注'),
        "violations":fields.one2many("fg_online_shop.violation","shop_id","违规记录"),
        'scores':fields.one2many('fg_online_shop.score', 'shop_id', '加分记录'),
        "auth_num":fields.char("授权书编号",size=64,select=True, required=False),
        "date_auth_to":fields.date("授权截止日期", required=False),
    }
    
    _sql_constraints=[('name_unique','unique(name)','网店名称不能重复!')]
    

class fg_online_shop_violation(osv.osv):
    _name = "fg_online_shop.violation"
    _description = "违规记录"
    
    _columns= {
        'name': fields.char('单号', size=64, select=True),
        "shop_id":fields.many2one("fg_online_shop.shop", "违规网店", select=True, change_default=True, required=True),
        "date":fields.date("记录时间"),
        "user_id":fields.many2one('res.users', '记录人', readonly=True),
        
        "url":fields.text("页面URL地址", required=True),
        "screenshot":fields.binary("违规页面截图", required=True),
        "product_model":fields.char("货号",size=64,required=True),
        "reason": fields.text('违规原因', required=True),
        "point": fields.integer('扣分', required=True),
        'note':fields.text('附注'),
    }

    _defaults={
        'user_id': lambda obj, cr, uid, context: uid,
        'date':fields.date.context_today,
        'name': lambda self,cr,uid,ctx=None: self.pool.get('ir.sequence').get(cr, uid, 'fg_online_shop.violation', context=ctx),
    }
    
class fg_online_shop_score(osv.osv):
    _name = "fg_online_shop.score"
    _description = "加分记录"
    
    _columns= {
        "name": fields.char('单号', size=64, select=True),
        "shop_id":fields.many2one("fg_online_shop.shop", "网店", select=True, change_default=True, required=True),
        "user_id":fields.many2one('res.users', '记录人', readonly=True),
        "date":fields.date("记录时间", required=True),
        "reason": fields.text('加分原因', required=True),
        "point": fields.integer('加分', required=True),
        'note':fields.text('附注'),
    }
    
    
    _defaults={
        'user_id': lambda obj, cr, uid, context: uid,
        'date':fields.date.context_today,
        'name': lambda self,cr,uid,ctx=None: self.pool.get('ir.sequence').get(cr, uid, 'fg_online_shop.score', context=ctx),
    }

class certificate(osv.osv):
    _name = "fg_online_shop.certificate"
    _description = "授权"
    
    
    _columns= {
        "name": fields.char('授权号', size=64, select=True),
        "shop_id":fields.many2one("fg_online_shop.shop", "网店", select=True, change_default=True, required=True),
        "user_id":fields.many2one('res.users', '记录人', readonly=True),
        "date":fields.date("记录时间", required=True),
        'note':fields.text('附注'),
    }
    
    _defaults={
        'user_id': lambda obj, cr, uid, context: uid,
        'date':fields.date.context_today,
    }
