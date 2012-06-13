# -*- coding: utf-8 -*-

import tools, base64
from osv import fields, osv
import xlwt, cStringIO

class amount_by_partner_wizard(osv.osv_memory):
    _name = "fg_sale.amount.parnter.wizard"
    _description = "客户销量统计"
    _columns = {
        'date_start': fields.date('开始日期', required=True),
        'date_end': fields.date('截止日期', required=True),
        'source':fields.boolean('分事业部统计'),
    }
    _defaults = {
        'date_end': fields.date.context_today,
    }
    
    def show_result(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids)[0]
        sql = """
        SELECT
        	P . NAME,
        	SUM(amount)
        FROM
        	fg_sale_order_report_daily d
        JOIN res_partner P ON P ."id" = d.partner_id
        WHERE
        	d."date" >= to_date('%s', 'YYYY-MM-DD')
        AND d."date" <= to_date('%s', 'YYYY-MM-DD')
        GROUP BY
        	P . NAME
        """
        if this.source:
            sql = """
            SELECT
            	P . NAME,
            	SUM(amount),
            	source
            FROM
            	fg_sale_order_report_daily d
            JOIN res_partner P ON P ."id" = d.partner_id
            WHERE
            	d."date" >= to_date('%s', 'YYYY-MM-DD')
            AND d."date" <= to_date('%s', 'YYYY-MM-DD')
            GROUP BY
            	P . NAME,
            	source
             ORDER BY
            	p."name"
            """
        
        cr.execute(sql % (this.date_start, this.date_end))
        
        report_obj = self.pool.get('fg_data.report.horizontal')
        
        ids = [report_obj.create(cr, uid, {'name':p[0], 'value':p[1], 'desc':(len(p)==3) and p[2] or ''}) for p in cr.fetchall()]
        
        act_obj = self.pool.get('ir.actions.act_window')
        mod_obj = self.pool.get('ir.model.data')
        
        result = mod_obj.get_object_reference(cr, uid, 'fg_data', 'action_fg_data_report_horizontal')
        id = result and result[1] or False
        
        result = act_obj.read(cr, uid, [id], context=context)[0]
        result['domain'] = "[('id','in', ["+','.join(map(str, ids))+"])]"
        return result


class amount_by_source_wizard(osv.osv_memory):
    _name = "fg_sale.amount.source.wizard"
    _description = "事业部销量统计"
    _columns = {
        'date_start': fields.date('开始日期', required=True),
        'date_end': fields.date('截止日期', required=True),
    }
    _defaults = {
        'date_end': fields.date.context_today,
    }
    
    def show_result(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids)[0]
        
        sql = """
        SELECT
                "source",
                SUM (amount)
        FROM
                fg_sale_order_report_daily
        WHERE
                DATE >= to_date('%s', 'YYYY-MM-DD')
        AND DATE <= to_date('%s', 'YYYY-MM-DD')
        GROUP BY
                "source"
        """
        
        cr.execute(sql % (this.date_start, this.date_end))
        
        report_obj = self.pool.get('fg_data.report.horizontal')
        
        ids = [report_obj.create(cr, uid, {'name':p[0], 'value':p[1]}) for p in cr.fetchall()]
        
        act_obj = self.pool.get('ir.actions.act_window')
        mod_obj = self.pool.get('ir.model.data')
        
        result = mod_obj.get_object_reference(cr, uid, 'fg_data', 'action_fg_data_report_horizontal')
        id = result and result[1] or False
        
        result = act_obj.read(cr, uid, [id], context=context)[0]
        result['domain'] = "[('id','in', ["+','.join(map(str, ids))+"])]"
        return result

class report_order(osv.osv_memory):
    _name = "fg_sale.order.export.wizard"
    _description = "导出订单明细"
    
    _columns = {
        'name': fields.char('文件名', 16, readonly=True),
        'date_start': fields.date('开始日期', required=True),
        'date_end': fields.date('截止日期', required=True),
        'source':fields.selection([(u'真空事业部',u'真空事业部'),
                            (u'塑胶事业部',u'塑胶事业部'),(u'玻璃事业部',u'玻璃事业部'), (u'财务部',u'财务部'),
                            (u'安全帽事业部',u'安全帽事业部'),(u'其他',u'其他'),(u'塑胶制品',u'塑胶制品')], '事业部'),
        'data': fields.binary('文件', readonly=True),
        'state': fields.selection( [('choose','choose'),   # choose 
                                     ('get','get'),         # get the file
                                   ] ),
    }
    
    _defaults = {
        'date_end': fields.date.context_today,
        'state': lambda *a: 'choose',
        'name': 'lines.xls',
    }
    
    def export_excel(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids)[0]
        order_obj = self.pool.get('fg_sale.order')
        
        book = xlwt.Workbook(encoding='utf-8')
        sheet1 = book.add_sheet(u'总体统计')
        
        order_list = order_obj.search(cr, uid, [
                ('date_confirm','>=', this.date_start),
                ('date_confirm','<=', this.date_end),
                ('state','=','done')
            ], order='date_confirm asc')
        cols = ['日期','发票号码','产品名称','规格型号','购货单位','单位','数量','数量/只','单价','金额','事业部','摘要']
        i = 0
        for c in cols:
            sheet1.write(0, i, c)
            i = i + 1
            
        i = 1
        _first = True
        for order in order_obj.browse(cr, uid, order_list):
                for line in order.order_line:
                    if this.source:
                        if this.source != line.product_id.source:
                            continue
                    if _first:
                        sheet1.write(i, 0, order.date_confirm)
                        sheet1.write(i, 1, order.name)
                        _first = False
                    
                    sheet1.write(i, 2, line.product_id.name)
                    sheet1.write(i, 3, line.product_id.default_code or '')
                    sheet1.write(i, 4, order.partner_id.name)
                    sheet1.write(i, 5, line.product_uom.name)
                    sheet1.write(i, 6, line.product_uom_qty)
                    sheet1.write(i, 7, line.aux_qty)
                    sheet1.write(i, 8, line.unit_price)
                    sheet1.write(i, 9, line.subtotal_amount)
                    sheet1.write(i, 10, line.product_id.source)
                    sheet1.write(i, 11, line.note or '')
                    i = i + 1
                _first = True
        
        buf=cStringIO.StringIO()
        book.save(buf)

        out=base64.encodestring(buf.getvalue())

        return self.write(cr, uid, ids, {'state':'get', 'data':out, 'name':this.name }, context=context)


class report_product(osv.osv_memory):
    _name = "fg_sale.product.export.wizard"
    _description = "按单品统计"
    
    _columns = {
        'name': fields.char('文件名', 16, readonly=True),
        'date_start': fields.date('开始日期', required=True),
        'date_end': fields.date('截止日期', required=True),
        'data': fields.binary('文件', readonly=True),
        'state': fields.selection( [('choose','choose'),   # choose 
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
