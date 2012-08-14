# -*- encoding: utf-8 -*-

from osv import osv, fields
import time, tools

class fg_online_shop_company(osv.osv):

    _name = 'fg_online_shop.company'
    _description = "经销商"

    _columns = {
        'partner_id': fields.many2one('res.partner', '上级经销商', required=False),
        'company_name': fields.char('经销商公司名',size=64,select=True),
        'name':fields.char('法定代表人姓名', size=64, select=True, required=True),
        'decl_tel':fields.char('法定代表人手机号',size=64),
        'decl_license':fields.char('营业执照号',size=64),
        'decl':fields.char('法定代表人身份证',size=64),
        'address':fields.char('公司地址',size=128),
        'tel':fields.char('责任人电话',size=64),
        'qq':fields.char('QQ',size=128),
        'e_mail':fields.char('Email',size=64),
        'fax': fields.char('Fax', size=64),
        'decl_date': fields.date('创建日期', readonly=True),
        'store_name':fields.char('店名',size=64),
        'store_address':fields.char('实体店地址',size=128),
        'store': fields.selection([('True','是'),('False','否')],'是否有实体店铺'),
        'store_year':fields.integer('经营年限'),
        'on_charge':fields.char('该店负责人',size=64),
        'note':fields.text('备注'),
        'service':fields.integer('实体店人数'),
        'saleroom':fields.float('预计年销售额',digits=[16,2]),
        'stores':fields.one2many('fg_online_shop.shop', 'company_id', '网店'),
        'web': fields.selection([('True','是'),('False','否')],'是否有独立运行的网站'),
        "web_address":fields.char("网络链接", size=64)
    }

    _defaults = {
        'decl_date': fields.date.context_today,
        'store':'True',
        "web":"False",
        
    }
    
    _sql_constraints=[('online_shop_name_unique','unique(name)','法定代表人姓名不能重复!')]
    

class fg_online_shop_shop(osv.osv):
    _name = 'fg_online_shop.shop'
    _description = "网店"
    
    _columns = {
        'company_id': fields.many2one('fg_online_shop.company','经销商法人',select=True),
        'name': fields.char("网店名称",size=64,select=True),
        'online_store': fields.boolean('是否有网络店铺'),
        'year':fields.char('经营年限',size=64),
        'online_store_address':fields.char('网店网址',size=128),
        'online_store_level':fields.char('店铺等级',size=32),
        'store_fund':fields.char('店铺储备资金',size=32),
        #'warehouse':fields.boolean('是否有专属仓库'),
        'warehouse_size':fields.char('仓储面积',size=64),
        'warehouse_money':fields.char('库存量(金额)',size=32),
        'customer_service':fields.char('网店客服人数',size=32),
        'art_design':fields.char('美术设计人数',size=64),
        'warehouse_person':fields.char('库房发货人数',size=64),
        'online_store_operation':fields.char('网店运营人数',size=64),
        'total_staff':fields.char('公司员工总数',size=64),
        'chief_degree':fields.char('负责人学历',size=32),
        'online_store_belong':fields.char('网店所属网站',size=64),
        'online_store_pro':fields.selection([('Personal', '个人'), ('Company', '商城')],'店铺性质'),       
        'chief':fields.char('责任人',size=64),
        'brand':fields.char('预计经营品牌',size=128, help='包括非富光的请详细写清楚'),
        'saleroom':fields.char('预计年销售额',size=32),
        'note':fields.text('附注'),
        "violations":fields.one2many("fg_online_shop.violation","shop_id","违规记录"),
        "authnum":fields.char("授权书编号",size=64,select=True),
        "authdate":fields.date("授权日期"),
        "authenddate":fields.date("截止日期"),

        "supplier":fields.char("供货商/备注",size=32),
        "contact":fields.char("联系方式",size=32),
        
    }
    _defaults = {
        'online_store': lambda *a: 'True',
        'online_store_pro': lambda *a: 'Personal',
    }
    
    _sql_constraints=[('name_unique','unique(name)','网店名称不能重复!')]
    

class fg_online_shop_violation(osv.osv):
    _name = "fg_online_shop.violation"
    _description = "违规记录"

    _columns= {
        "chief":fields.char("该店负责人",size=64),
        "shop_id":fields.many2one("fg_online_shop.shop", "违规网店", select=True, change_default=True),
        "date":fields.date("记录时间"),
        "user_id":fields.many2one('res.user', '记录人', readonly=True),
        "user_assigned_id":fields.many2one('res.user', '处理人'),
        "desc":fields.char("违规项目", help="未批准折扣，隐形折扣",size=64),
        "url":fields.text("页面URL地址",size=300),
        "pic":fields.binary("违规页面截图"),
        "product_model":fields.char("货号",size=64,required=True),
    }

    _defaults={
        'user_id': lambda obj, cr, uid, context: uid,
        'date':fields.date.context_today,
    }