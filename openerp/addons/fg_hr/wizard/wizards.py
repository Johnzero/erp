# -*- coding: utf-8 -*-

from osv import osv, fields
import time, xlrd, base64
from datetime import datetime
from tools import DEFAULT_SERVER_DATE_FORMAT
import xlwt, cStringIO

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
                if sh.cell(rx, 2).value:
                    print '---------------'
                    print sh.cell(rx, 2).value
                    print datetime.strptime(' '.join([sh.cell(rx, 2).value, '07:30:00']), '%Y-%m-%d %H:%M:%S')
                    print '---------------'
                
                data = {}
                try:
                    date_s = sh.cell(rx, 2).value.strip()
                    print date_s
                    date = time.strptime(date_s.strip(),'%Y.%m.%d')
                    data['date'] = date
                except:
                    continue
                
                am_start_work = datetime.strptime(' '.join([date_s, '07:30:00']), '%Y-%m-%d %H:%M:%S')
                am_end_word = datetime.strptime(' '.join([date_s, '11:30:00']), '%Y-%m-%d %H:%M:%S')
                pm_start_work = datetime.strptime(' '.join([date_s, '13:30:00']), '%Y-%m-%d %H:%M:%S')
                pm_end_word = datetime.strptime(' '.join([date_s, '17:30:00']), '%Y-%m-%d %H:%M:%S')
                if wiz.work_time == 'summer':
                    am_start_work = datetime.strptime(' '.join([date_s, '07:00:00']), '%Y-%m-%d %H:%M:%S')
                    pm_start_work = datetime.strptime(' '.join([date_s, '14:30:00']), '%Y-%m-%d %H:%M:%S')
                    pm_end_word = datetime.strptime(' '.join([date_s, '18:00:00']), '%Y-%m-%d %H:%M:%S')
                
                empl_name = str(sh.cell(rx, 0).value).strip()
                print empl_name
                if empl_name:
                    empl_list = empl_obj.search(cr, uid, [('name','=',empl_name)])
                    if empl_list:
                        data['employee_id'] = empl_list[0]
                    else:
                        continue
                else:
                    continue
                try:
                    if str(sh.cell(rx, 3).value).strip():
                        data['am_checkin'] = datetime.strptime(' '.join([date_s, str(sh.cell(rx, 3).value).strip()]), 
                            '%Y-%m-%d %H:%M:%S')
                    if str(sh.cell(rx, 4).value).strip():
                        data['am_checkout'] = datetime.strptime(' '.join([date_s, str(sh.cell(rx, 4).value).strip()]), 
                            '%Y-%m-%d %H:%M:%S')
                    if str(sh.cell(rx, 5).value).strip():
                        data['pm_checkin'] = datetime.strptime(' '.join([date_s, str(sh.cell(rx, 5).value).strip()]), 
                            '%Y-%m-%d %H:%M:%S')
                    if str(sh.cell(rx, 6).value).strip():
                        data['pm_checkout'] = datetime.strptime(' '.join([date_s, str(sh.cell(rx, 6).value).strip()]), 
                            '%Y-%m-%d %H:%M:%S')
                except:
                    continue
                
                #see that is the state.
                data['state'] = 'normal'
                if data['am_checkin'] and data['am_checkout'] and data['pm_checkin'] and data['pm_checkout']:
                    if data['am_checkin'] < am_start_work or data['pm_checkin'] < pm_start_work:
                        data['state'] = 'late'
                    if data['am_checkout'] > am_end_work or data['pm_checkout'] > pm_end_work:
                        data['state'] = 'early'
                else:
                    data['state'] = 'abnormal'
                
                id = att_obj.create(cr, uid, data)
                new_ids.append(id)
            
            result = mod_obj.get_object_reference(cr, uid, 'fg_hr', 'fghr_attendance_tree_action')
            id = result and result[1] or False
            result = act_obj.read(cr, uid, [id], context=context)[0]
            result['domain'] = "[('id','in', ["+','.join(map(str, new_ids))+"])]"
            
        return result