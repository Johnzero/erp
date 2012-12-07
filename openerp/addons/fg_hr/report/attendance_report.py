# -*- coding: utf-8 -*-

import tools
from osv import fields, osv

# class attendance_item(osv.osv):
#     _name = "fg_hr.attendance.item"
#     
#     _columns = {
#         'employee_id': fields.many2one('hr.employee', '员工', required=True),
#         'period': fields.char('月份'),
#         'work_hour':fields.integer('工作小时'),
#         'late': fields.integer('迟到'),
#         'late_minutes': fields.integer('迟到分钟'),
#         'non_check': fields.integer('不正常打卡'),
#     }
#     
#     _order = 'period asc'
#     
#     
#     def init(self, cr):
#         tools.drop_view_if_exists(cr, 'fg_account_period_check')
#         cr.execute("""
#             create or replace view fg_account_period_check as (
#             (
#             
#             )
#             )""")
#         