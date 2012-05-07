# -*- encoding: utf-8 -*-

{
    'name': 'db view',
    'version': '1.0',
    'category' : 'utils',
    'description': """db view""",
    'author': 'openerp',
    'website': 'http://www.openerp.org',
    'depends': ['base'],
    'init_xml': [],
    'update_xml': [
        'fg_sync.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
    'application':True,
}