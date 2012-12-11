# -*- coding: utf-8 -*-

from osv import osv, fields
import time, xlrd, base64, xlwt, cStringIO
from datetime import datetime,timedelta

def convert_datetime(dt, t):
    return datetime(dt.tm_year, dt.tm_mon, dt.tm_mday, *t[-3:])

class attendance_import(osv.osv_memory):
    _name = "fg_hr.attendance.import.wizard"
    _description = "导入考勤明细"
    
    _columns = {
        'date': fields.date('日期',  required=True),
        'excel': fields.binary('excel文件', filters='*.xls'),
    }
    
    _defaults = {
        'date': fields.date.context_today,
    }
    
    def import_list(self, cr, uid, ids, context=None):
        result = {'type': 'ir.actions.act_window_close'}
        
        for wiz in self.browse(cr,uid,ids):
            if not wiz.excel: continue
            excel = xlrd.open_workbook(file_contents=base64.decodestring(wiz.excel))
            sh = excel.sheet_by_index(0)
            
            att_obj = self.pool.get('fg_hr.attendance')
            act_obj = self.pool.get('ir.actions.act_window')
            mod_obj = self.pool.get('ir.model.data')

            empl_obj = self.pool.get('hr.employee')
            
            new_ids = []
            for rx in range(sh.nrows):
                data = {'date': wiz.date}
                
                empl_name = sh.cell(rx, 3).value.strip()
                if not empl_name or empl_name=='姓名' : continue
                empl_list = empl_obj.search(cr, uid, [('name','=',empl_name)])
                if empl_list:
                    data['employee_id'] = empl_list[0]
                else:
                    continue
                
                try:
                    data['attendance'] = sh.cell(rx, 4).value
                    data['checkin'] = sh.cell(rx, 5).value
                    data['skipping'] = sh.cell(rx, 7).value
                    data['late'] = sh.cell(rx, 8).value
                    data['late_min'] = sh.cell(rx, 9).value
                    data['early'] = sh.cell(rx, 10).value
                    data['early_min'] = sh.cell(rx, 11).value
                except Exception as err:
                    print err
                    continue

                id = att_obj.create(cr, uid, data)
                new_ids.append(id)
            
            result = mod_obj.get_object_reference(cr, uid, 'fg_hr', 'fghr_attendance_tree_action')
            id = result and result[1] or False
            result = act_obj.read(cr, uid, [id], context=context)[0]
            result['domain'] = "[('id','in', ["+','.join(map(str, new_ids))+"])]"
            
        return result
        
        
class salary_export(osv.osv_memory):
    _name = "fg_hr.salary.export.wizard"
    _description = "导出"
    
    _columns = {
        'date': fields.date('考勤开始日期',  required=True),
        'name': fields.char('文件名', 16,),
        'data': fields.binary('文件',),
        'state': fields.selection( [('choose','choose'),   # choose
                                     ('get','get'),         # get the file
                                   ] ),
    }
    
    _defaults = {
        'date': fields.date.context_today,
        'state': lambda *a: 'choose',
        'name': 'salary.xls',
    }
    
    def export_excel(self, cr, uid, ids, context=None):
        book = xlwt.Workbook(encoding='utf-8')
        this = self.browse(cr, uid, ids)[0]
        
        sheet1 = book.add_sheet('salary')
        sql = """
            SELECT
                    res."name",
                    att.attendance,
                    att.checkin,
                    att.late,
                    att.late_min,
                    att.early,
                    att.early_min,
                    salary.basic,
                    salary.post,
                    salary.performance,
                    round(
                            (salary.basic + salary.post) / att.attendance * att.checkin - att.late_min * 5 + salary.performance
                    ) AS salary
            FROM
                    fg_hr_attendance att
            JOIN fg_hr_salary salary ON att.employee_id = salary.employee_id
            JOIN hr_employee empl ON empl."id" = att.employee_id
            JOIN resource_resource res ON res."id" = empl.resource_id
            WHERE
                    EXTRACT (YEAR FROM att."date") = %s
            AND EXTRACT (MONTH FROM att."date") = %s
        """
        m = this.date.split('-')[1]
        y = this.date.split('-')[0]
        
        cr.execute(sql % (y, m))
        
        sheet1.write(0, 0, '员工')
        sheet1.write(0, 1, '应出勤')
        sheet1.write(0, 2, '实际出勤')
        sheet1.write(0, 3, '迟到(次数)')
        sheet1.write(0, 4, '迟到(分钟)')
        sheet1.write(0, 5, '早退(次数)')
        sheet1.write(0, 6, '早退(分钟)')
        sheet1.write(0, 7, '基本工资')
        sheet1.write(0, 8, '岗位工资')
        sheet1.write(0, 9, '绩效')
        sheet1.write(0, 10, '社保')
        sheet1.write(0, 11, '工资')
        
        row = 1
        
        for p in cr.fetchall():
            col = 0
            for n in p:
                sheet1.write(row, col, n)
                col = col + 1
            row = row + 1
            
        buf=cStringIO.StringIO()
        book.save(buf)

        out=base64.encodestring(buf.getvalue())

        return self.write(cr, uid, ids, {'state':'get', 'data':out, 'name':this.name }, context=context)