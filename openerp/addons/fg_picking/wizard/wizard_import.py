# -*- coding: utf-8 -*-

from osv import osv, fields
import time, xlrd, base64
from tools import DEFAULT_SERVER_DATE_FORMAT

class delivery_import(osv.osv_memory):
    _name = "fg_picking.delivery.import.wizard"
    _description = "导入仓库发货单"
    
    _columns = {
        'excel': fields.binary('Excel文件', filters='*.xls'),
    }
    
    
    def import_delivery(self, cr, uid, ids, context=None):
        result = {'type': 'ir.actions.act_window_close'}
        
        delivery_obj = self.pool.get('fuguang.delivery')
        delivery_line_obj = self.pool.get('fuguang.delivery.line')
        
        
        for wiz in self.browse(cr,uid,ids):
            if not wiz.excel: continue
            
            excel = xlrd.open_workbook(file_contents=base64.decodestring(wiz.excel))
            sh = excel.sheet_by_index(0)
            
            partner_name = sh.cell(1, 0).value.replace('发货单位:','')
            dep_name = sh.cell(1, 3).value
            
            d_id = delivery_obj.create(cr, uid, {'partner_name':partner_name, 'dep_name':dep_name})
            
            
            for row_index in range(3, sh.nrows):
                if sh.cell(row_index, 0).value and '下单签字' not in sh.cell(row_index, 0).value:
                    #print sh.cell(row_index, i).value
                    line = {
                        'delivery_id':d_id,
                        'product': sh.cell(row_index, 0).value,
                        'code': sh.cell(row_index, 1).value,
                        'color': sh.cell(row_index, 2).value,
                        'uom': sh.cell(row_index, 3).value,
                        'plan': sh.cell(row_index, 4).value,
                        'real': sh.cell(row_index, 5).value,
                        'warehouse': sh.cell(row_index, 6).value,
                        'note': sh.cell(row_index, 7).value,
                    }
                    delivery_line_obj.create(cr, uid, line)
                    
        obj_model = self.pool.get('ir.model.data')
        model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),('name','=','fuguang_delivery_form_view')])
        resource_id = obj_model.read(cr, uid, model_data_ids, fields=['res_id'])[0]['res_id']
        
        result = {
        'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'fuguang.delivery',
        'views': [(resource_id,'form')],
        'type': 'ir.actions.act_window',
        'context': context,
        'res_id':d_id,
        }
        
        return result