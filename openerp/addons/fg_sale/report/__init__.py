# -*- encoding: utf-8 -*-

from report import report_sxw
from osv import osv
import tools

class fg_order_html(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(fg_order_html, self).__init__(cr, uid, name, context)
        #picking_item_obj = self.pool.get('fuguang.picking.item')
        pass
    
report_sxw.report_sxw('report.fg_sale.order.html', 'fg_sale.order',
                      'addons/fg_sale/report/order.html',parser=fg_order_html)