# -*- coding: utf-8 -*-


{
    'name': '富光人力资源',
    'version': '1.0',
    'category' : '富光',
    'description': """人员工资计算，考勤记录""",
    'author': 'Daniel',
    'website': 'http://www.fuguang.cn',
    'depends': ['base','hr'],
    'init_xml': [],
    'update_xml': [
        'security/ir.model.access.csv',
        'hr_view.xml',
        'wizard/wizards.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
    'application':True,
}