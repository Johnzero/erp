# -*- encoding: utf-8 -*-

{
    'name': 'scrapyschedule',
    'version': '2.0',
    'category' : 'utils',
    'description': """Scrapy Schedule Everyday""",
    'author': 'openerp',
    'website': 'http://www.openerp.org',
    'depends': ['base'],
    'init_xml': [],
    'update_xml': [
        'security/group.xml',
        'security/ir.model.access.csv',
        'scrapyschedule.xml',
        'scrapy.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
    'application':False,
}