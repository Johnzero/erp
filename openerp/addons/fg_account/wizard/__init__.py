# -*- coding: utf-8 -*-

from osv import osv, fields
import time, xlrd, base64
from tools import DEFAULT_SERVER_DATE_FORMAT
import xlwt, cStringIO

class bank_bill_import(osv.osv_memory):
    _name = "fg_account.bank_bill.import.wizard"
    _description = "导入账单明细"
    
    _columns = {
        'excel': fields.binary('excel文件', filters='*.xls'),
    }
    
    def import_bill(self, cr, uid, ids, context=None):
        result = {'type': 'ir.actions.act_window_close'}
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

                if not cash_in continue
                
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


class reconcile_wizard(osv.osv_memory):
    _name = "fg_account.reconcile.confirm.wizard"
    _description = "对账"
    
    _columns = {
        'confirm':fields.boolean('确认对账/取消对账'),   
    }
    
    def confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        
        period_check_obj = self.pool.get('fg_account.period.check')
        order_obj = self.pool.get('fg_sale.order')
        bill_obj = self.pool.get('fg_account.bill')
        
        data = self.read(cr, uid, ids, [], context=context)[0]
        record_ids = context and context.get('active_ids', False)
        
        for record in period_check_obj.browse(cr, uid, record_ids, context):
            if record.ref_doc._table_name == 'fg_sale.order':
                order_obj.write(cr, uid, [record.id], {'reconciled':data['confirm']})
                
            if record.ref_doc._table_name == 'fg_account.bill':
                bill_obj.write(cr, uid, [record.id], {'reconciled':data['confirm']})
        
        return {'type': 'ir.actions.act_window_close'}
    
class reconcile_export(osv.osv_memory):
    _name = "fg_account.reconcile.export.wizard"
    _description = "对账单导出"
    
    _columns = {
        'partner_id': fields.many2one('res.partner', '客户'),
        'reconciled':fields.boolean('已对账'),
        'date_start': fields.date('开始日期'),
        'date_end': fields.date('结束日期'),
        'name': fields.char('文件名', 16,),
        'data': fields.binary('文件',),
        'state': fields.selection( [('choose','choose'),   # choose
                                     ('get','get'),         # get the file
                                   ] ),
    }
    
    _defaults = {
        'date_end': fields.date.context_today,
        'state': lambda *a: 'choose',
        'name': 'reconcile.xls',
    }
    
    
    def export_excel(self, cr, uid, ids, context=None):
        book = xlwt.Workbook(encoding='utf-8')
        
        this = self.browse(cr, uid, ids)[0]
        
        sql = """
        SELECT
            o_date,
        	name,
        	t,
        	reconciled,
        	amount,
        	note
        FROM
        	fg_account_period_check
        WHERE
        	reconciled = %s
        AND o_partner = %s
        AND o_date >= to_date('%s', 'YYYY-MM-DD')
        AND o_date <= to_date('%s', 'YYYY-MM-DD')
        
        """
        
        sheet1 = book.add_sheet(this.partner_id.name)
        sheet1.write(0, 0, this.partner_id.name)
        sheet1.write(0, 1, this.date_start)
        sheet1.write(0, 2, this.date_end)
        
        sources = ['日期','单号','发货额','退回','收现','备注','转帐','让利','余额']
        c_i = 0
        for c in sources:
            sheet1.write(1, c_i, c)
            c_i = c_i + 1
        
        i = 2
        cr.execute(sql % (this.reconciled, this.partner_id.id, this.date_start, this.date_end))
        for p in cr.fetchall():
            print p
            sheet1.write(i, 0, p[0])
            sheet1.write(i, 1, p[1])
            sheet1.write(i, 9, p[3])
            sheet1.write(i, 5, p[5])
            sheet1.write(i, sources.index(p[2]), p[4])
            i = i + 1
        
        buf=cStringIO.StringIO()
        book.save(buf)

        out=base64.encodestring(buf.getvalue())

        return self.write(cr, uid, ids, {'state':'get', 'data':out, 'name':this.name }, context=context)
        