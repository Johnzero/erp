# -*- encoding: utf-8 -*-

{
    'name': '富光业务部销售',
    'version': '1.0',
    'category' : '富光',
    'description': """富光业务部销售子系统""",
    'author': 'Daniel',
    'website': 'http://www.ide.fm',
    'depends': ['base', 'board', 'product'],
    'init_xml': [],
    'update_xml': [
	'fg_sale_view.xml',
	'security/group.xml',
	'security/ir.model.access.csv',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
    'application':True,
}