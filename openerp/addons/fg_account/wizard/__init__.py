# -*- coding: utf-8 -*-

from osv import osv, fields
import time, xlrd, base64
from tools import DEFAULT_SERVER_DATE_FORMAT


class bank_bill_import(osv.osv_memory):
    _name = "fg_account.bank_bill.import.wizard"
    _description = "导入账单明细"
    
    _columns = {
        'excel': fields.binary('excel文件', filters='*.xls'),
    }
    
    def import_bill(self, cr, uid, ids, context=None):
        for wiz in self.browse(cr,uid,ids):
            if not wiz.excel: continue
            
            excel = xlrd.open_workbook(file_contents=base64.decodestring(wiz.excel))
            sh = excel.sheet_by_index(0)
            
            bill_obj = self.pool.get('fg_account.bill')
            act_obj = self.pool.get('ir.actions.act_window')
            mod_obj = self.pool.get('ir.model.data')
            
            new_ids = []
            for rx in range(sh.nrows):
                #如果第一个单元格是日期，则解析.
                date_s = sh.cell(rx, 0).value
                cash_in = sh.cell(rx, 3).value
                cash_out = sh.cell(rx, 4).value
                
                if not cash_in: continue
                
                try:
                    date = time.strptime(date_s.strip(),'%Y.%m.%d')
                    
                except:
                    continue
                
                id = bill_obj.create(cr, uid, {
                    'user_id':uid,
                    'date_paying':time.strftime(DEFAULT_SERVER_DATE_FORMAT, date),
                    'note':sh.cell(rx, 1).value,
                    'amount':float(cash_in),
                })
                new_ids.append(id)
            
            result = mod_obj.get_object_reference(cr, uid, 'fg_account', 'action_fg_account_bill_all')
            id = result and result[1] or False
            result = act_obj.read(cr, uid, [id], context=context)[0]
            result['domain'] = "[('id','in', ["+','.join(map(str, new_ids))+"])]"
            
        return result

class confirm_customer(osv.osv_memory):
    _name = "fg_account.bank_bill.customer.confirm.wizard"
    _description = "确认客户"
    
    _columns = {
        'partner_id': fields.many2one('res.partner', '客户', required=True),
    }
    
    def view_init(self, cr, uid, fields_list, context=None):
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False)
        bill = self.pool.get('fg_account.bill').browse(cr, uid, record_id, context=context)
        if bill.state != 'draft':
            raise osv.except_osv('提醒','所选单据中有些已经确认过客户.')
        return False
    
    def confirm_customer(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        bill_obj = self.pool.get('fg_account.bill')
        
        data = self.read(cr, uid, ids, [], context=context)[0]
        
        record_id = context and context.get('active_ids', False)

        bill_obj.write(cr, uid, record_id, { 
            'partner_id': data['partner_id'][0], 
            }
        )
        
        return {'type': 'ir.actions.act_window_close'}

