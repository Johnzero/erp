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
        'work_time': fields.selection([('summer', '夏季'), ('winter', '冬季')], '时令'),
        'excel': fields.binary('excel文件', filters='*.xls'),
    }
    
    _defaults = {
        'work_time': 'winter',
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
            partner_obj = self.pool.get('res.partner')
            empl_obj = self.pool.get('hr.employee')
            
            new_ids = []
            for rx in range(sh.nrows):
                data = {}
                empl_name = sh.cell(rx, 2).value.strip()
                if not empl_name or empl_name=='姓名' : continue
                empl_list = empl_obj.search(cr, uid, [('name','=',empl_name)])
                if empl_list:
                    data['employee_id'] = empl_list[0]
                else:
                    continue

                try:
                    date_s = sh.cell(rx, 4).value.strip()
                    date = time.strptime(date_s,'%Y-%m-%d')
                    data['date'] = date_s
                    am_s = am_e = pm_s = pm_e = ''
                    if sh.cell(rx, 5).value:
                        am_s = xlrd.xldate_as_tuple(sh.cell(rx, 5).value, 0)
                        am_s = convert_datetime(date, am_s)
                        data['am_checkin'] = datetime.strftime(am_s-timedelta(hours=8), '%Y-%m-%d %H:%M:%S')
                        
                    if sh.cell(rx, 6).value:
                        am_e = xlrd.xldate_as_tuple(sh.cell(rx, 6).value, 0)
                        am_e = convert_datetime(date, am_e)
                        data['am_checkout'] = datetime.strftime(am_e-timedelta(hours=8), '%Y-%m-%d %H:%M:%S')
                    
                    if sh.cell(rx, 7).value:
                        pm_s = xlrd.xldate_as_tuple(sh.cell(rx, 7).value, 0)
                        pm_s = convert_datetime(date, pm_s)
                        data['pm_checkin'] = datetime.strftime(pm_s-timedelta(hours=8), '%Y-%m-%d %H:%M:%S')
                        
                    if sh.cell(rx, 8).value:
                        pm_e = xlrd.xldate_as_tuple(sh.cell(rx, 8).value, 0)
                        pm_e = convert_datetime(date, pm_e)
                        data['pm_checkout'] = datetime.strftime(pm_e-timedelta(hours=8), '%Y-%m-%d %H:%M:%S')

                        am_start_work = datetime.strptime(' '.join([date_s, '07:30:00']), '%Y-%m-%d %H:%M:%S')
                        am_end_work = datetime.strptime(' '.join([date_s, '11:30:00']), '%Y-%m-%d %H:%M:%S')
                        pm_start_work = datetime.strptime(' '.join([date_s, '13:30:00']), '%Y-%m-%d %H:%M:%S')
                        pm_end_work = datetime.strptime(' '.join([date_s, '17:30:00']), '%Y-%m-%d %H:%M:%S')
                        
                        if wiz.work_time == 'summer':
                            am_start_work = datetime.strptime(' '.join([date_s, '07:00:00']), '%Y-%m-%d %H:%M:%S')
                            pm_start_work = datetime.strptime(' '.join([date_s, '14:30:00']), '%Y-%m-%d %H:%M:%S')
                            pm_end_work = datetime.strptime(' '.join([date_s, '18:00:00']), '%Y-%m-%d %H:%M:%S')
                    
                    if am_s and am_e and pm_s and pm_e:
                        #see if it's late.
                        data['late'] = 0
                        am_dd = (am_s-am_start_work).total_seconds()
                        if am_dd > 60:
                            data['state'] = 'late'
                            data['late'] = round(am_dd/60)
                        
                        pm_dd = (pm_s-pm_start_work).total_seconds()
                        if pm_dd > 60:
                            data['state'] = 'late'
                            data['late'] = data['late'] + round(pm_dd/60)
                        
                        if (am_e < am_end_work) or (pm_e<pm_end_work):
                            data['state'] = 'early'
                    else:
                        data['state'] = 'abnormal'
                except Exception as e:
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
        'work_time': fields.selection([('summer', '夏季'), ('winter', '冬季')], '时令'),
        'date_start': fields.date('开始日期',  required=True),
        'date_end': fields.date('结束日期',  required=True),
        'name': fields.char('文件名', 16,),
        'data': fields.binary('文件',),
        'state': fields.selection( [('choose','choose'),   # choose
                                     ('get','get'),         # get the file
                                   ] ),
    }
    
    _defaults = {
        'date_end': fields.date.context_today,
        'state': lambda *a: 'choose',
        'name': 'salary.xls',
    }
    
    
    def export_excel(self, cr, uid, ids, context=None):
        book = xlwt.Workbook(encoding='utf-8')
        this = self.browse(cr, uid, ids)[0]
        
        sheet1 = book.add_sheet('salary')
        sql = """
        SELECT
        	att.employee_id,
        	SUM(
        		CASE
        		WHEN att."state" = 'normal' THEN
        			1
        		ELSE
        			0
        		END
        	)AS normal,
        	SUM(
        		CASE
        		WHEN att."state" = 'late' THEN
        			att.late
        		ELSE
        			0
        		END
        	)AS late,
        	SUM(
        		CASE
        		WHEN att."state" = 'early' THEN
        			1
        		ELSE
        			0
        		END
        	)AS early,
        	SUM(
        		CASE
        		WHEN att."state" = 'abnormal' THEN
        			1
        		ELSE
        			0
        		END
        	)AS abnormal
        FROM
        	fg_hr_attendance att
        WHERE
        	att."date" >= to_date('2012-11-01', 'YYYY-MM-DD')
        AND att."date" <= to_date('2012-11-30', 'YYYY-MM-DD')
        GROUP BY
        	att.employee_id
        """
        
        cr.execute()
        
        buf=cStringIO.StringIO()
        book.save(buf)

        out=base64.encodestring(buf.getvalue())

        return self.write(cr, uid, ids, {'state':'get', 'data':out, 'name':this.name }, context=context)
        
            
    