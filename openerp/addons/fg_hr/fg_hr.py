# -*- coding: utf-8 -*-

from osv import osv, fields
import time

class fghr_salary(osv.osv):
    _name = 'fg_hr.salary'
    _description = '工资明细'
    
    _columns = {
        'employee_id': fields.many2one('hr.employee', '员工', required=True, select=True),
        'basic':fields.float('基本工资', digits=(8, 1)),
        'post':fields.float('岗位工资', digits=(8, 1)),
        'performance':fields.float('绩效工资', digits=(8, 1)),
    }
    

class fghr_attendance(osv.osv):
    _name = 'fg_hr.attendance'
    _description = '考勤记录明细'
    
    _columns = {
        'employee_id': fields.many2one('hr.employee', '员工', required=True, select=True),
        'date': fields.date('考勤日期', required=True, select=True),
        'date_import': fields.date('导入日期'),
        'am_checkin': fields.datetime('早晨上班'),
        'am_checkout': fields.datetime('早晨下班'),
        'pm_checkin': fields.datetime('下午上班'),
        'pm_checkout': fields.datetime('下午下班'),
        'late': fields.integer('迟到(分钟)'),
        'early': fields.integer('早退(分钟)'),
        'state': fields.selection([('normal', '正常'), ('late', '迟到'), ('early', '早退'), ('abnormal','记录不完整')], '状态', select=True),
        'note':fields.char('附注', size=200),
    }
    
    _order = 'date desc'
    
    _defaults = {
        'date_import': fields.date.context_today,
        'state': 'normal',
    }