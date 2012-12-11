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
        'attendance': fields.integer('应出勤'),
        'checkin': fields.integer('实际出勤'),
        'skipping': fields.integer('旷工'),
        'late': fields.integer('迟到(次)'),
        'late_min': fields.integer('迟到(分钟)'),
        'early': fields.integer('早退(次)'),
        'early_min': fields.integer('早退(分钟)'),
    }
    
    _order = 'date desc'
    
    _defaults = {
        'date': fields.date.context_today,
    }