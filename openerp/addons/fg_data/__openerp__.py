# -*- encoding: utf-8 -*-

{
    'name': '富光数据导入',
    'version': '1.0',
    'category' : '富光',
    'description': """富光数据导入""",
    'author': 'Daniel',
    'website': 'http://www.ide.fm',
    'depends': ['base', 'fg_product_attr'],
    'init_xml': [],
    'update_xml': [
        'data/customer/category.xml',
        'data/customer/customer.xml',
        'data/product/base.xml',
        'data/product/color.xml',
        'data/product/category_ex.xml',
        'data/product/product.xml',
        'data/user.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
    'application':False,
}