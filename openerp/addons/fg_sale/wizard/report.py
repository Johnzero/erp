# -*- coding: utf-8 -*-

import tools, base64
from osv import fields, osv
import xlwt, cStringIO

class report_product(osv.osv_memory):
    _name = "fg_sale.product.export.wizard"
    _description = "按单品统计"
    
    _columns = {
        'name': fields.char('文件名', 16, readonly=True),
        'date_start': fields.date('开始日期', required=True),
        'date_end': fields.date('截止日期', required=True),
        'data': fields.binary('文件', readonly=True),
        'state': fields.selection( [('choose','choose'),   # choose language
                                     ('get','get'),         # get the file
                                   ] ),
    }
    
    _defaults = {
        'date_end': fields.date.context_today,
        'state': lambda *a: 'choose',
        'name': 'report.xls',
    }
    
    def export_excel(self, cr, uid, ids, context=None):
        book = xlwt.Workbook(encoding='utf-8')
        sheet1 = book.add_sheet(u'总体统计')
        sheet2 = book.add_sheet(u'塑胶事业部')
        sheet3 = book.add_sheet(u'真空事业部')
        sheet4 = book.add_sheet(u'玻璃事业部')
        sheet5 = book.add_sheet(u'财务部')
        sheet6 = book.add_sheet(u'安全帽事业部')
        sheet7 = book.add_sheet(u'塑胶制品')
        sheet8 = book.add_sheet(u'其他')
        sources = ['总体统计', '塑胶事业部', '真空事业部', '玻璃事业部', '财务部', '安全帽事业部', '塑胶制品', '其他']
        
        for i in range(len(sources)):
            book.get_sheet(i).write(0,0,'排名')
            book.get_sheet(i).write(0,1,'产品')
            book.get_sheet(i).write(0,2,'货号')
            book.get_sheet(i).write(0,3,'事业部')
            book.get_sheet(i).write(0,4,'售出只数')
            book.get_sheet(i).write(0,5,'金额')
        
        this = self.browse(cr, uid, ids)[0]

        sql = """
        SELECT
            product.id,
        	product.name_template,
        	product.default_code,
        	product.source,
        	SUM(line.aux_qty)AS qty,
        	SUM(line.subtotal_amount)AS amount
        FROM
        	product_product product
        JOIN fg_sale_order_line line ON line.product_id = product."id"
        JOIN fg_sale_order o ON o."id" = line.order_id
        WHERE
        	product."source" IS NOT NULL
        AND o."state" = 'done'
        AND o.date_confirm >= to_date('%s', 'YYYY-MM-DD')
        AND o.date_confirm <= to_date('%s', 'YYYY-MM-DD')
        GROUP BY
            product.id,
        	product.name_template,
        	product.source,
        	product.default_code
        ORDER BY
        	amount DESC
        """
        
        def _write_cell(s, r, p):
            s.write(r, 0, r)
            s.write(r, 1, p[1])
            s.write(r, 2, p[2])
            s.write(r, 3, p[3])
            s.write(r, 4, p[4])
            s.write(r, 5, p[5])
        cr.execute(sql % (this.date_start, this.date_end))
        i = 1
        for p in cr.fetchall():
            _write_cell(sheet1, i, p)
            i = i + 1
            
            if p[3] in sources:
                sheet = book.get_sheet(sources.index(p[3]))
                if sheet:
                    row_count = len(sheet.rows)
                    _write_cell(sheet, row_count, p)
        
        _write_cell(sheet1, len(sheet1.rows), ['','统计时间: %s 到 %s' % (this.date_start, this.date_end),'','','',''])
        
        buf=cStringIO.StringIO()
        book.save(buf)
        
        out=base64.encodestring(buf.getvalue())
        
        return self.write(cr, uid, ids, {'state':'get', 'data':out, 'name':this.name }, context=context)
