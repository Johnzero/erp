# -*- coding: utf-8 -*-

from osv import osv, fields
import time, xlrd, base64
from tools import DEFAULT_SERVER_DATETIME_FORMAT


class bank_bill_import(osv.osv_memory):
    
    _name = "fg_account.bank_bill.import.wizard"
    _description = "导入账单明细"
    
    _columns = {
        'excel': fields.binary('excel文件', filters='*.xsl'),
    }
    
    def import_bill(self, cr, uid, ids, context=None):
        for wiz in self.browse(cr,uid,ids):
            if not wiz.excel: continue
            
            excel = xlrd.open_workbook(file_contents=base64.decodestring(wiz.excel))
            sh = excel.sheet_by_index(0)
            print sh.name, sh.nrows, sh.ncols
            for rx in range(sh.nrows):
                for ry in range(sh.ncols):
                    print sh.cell(rx, ry).value
            
        return {'type': 'ir.actions.act_window_close'}