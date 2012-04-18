# -*- coding: utf-8 -*-

from osv import osv
import pyodbc

class order_import(osv.osv_memory):
    _name = "fg_sale.order.wizard_import"
    _description = "order importing."
    
    _columns = {
        
        
    }
    
    
    def import_order(self, cr, uid, ids, context=None):
        import chardet
        
        user_dict = {}
        
        #cache local dict first.
        # user name->id.
        # partner name->id-.
        cr.execute("""
                   SELECT
                    "public".res_users."id",
                    "public".res_users."name"
                    FROM
                    "public".res_users
                   """)
        for r in cr.fetchall():
            print r[1], chardet.detect(r[1].encode('utf-8'))
            user_dict[r[1]] = r[0]

        cr.execute("""
                   SELECT
                    "public".res_partner."id",
                    "public".res_partner."name"
                    FROM
                    "public".res_partner
                   """)

        cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=192.168.209.128;DATABASE=jd;UID=erp;PWD=erp')
        cursor = cnxn.cursor()
        cursor.execute("""
                SELECT
                TOP 10 FBillNo,
                FDate,
                t_Item.FName AS FPartnerName,
                t_o.FAddress AS FAddress,
                FNote,
                tu_1.FName AS FBillerName,
                tu_2.FName AS FCheckerName,
                FCheckDate,
                FInvoiceAmount,
                FROB
                FROM ICSale
                JOIN t_Item ON FCustID = t_Item.FItemID
                JOIN t_User tu_1 ON FBillerID = tu_1.FUserID
                JOIN t_User tu_2 ON FCheckerID = tu_2.FUserID
                JOIN t_Organization t_o ON FCustID = t_o.FItemID
                """)

        rows = cursor.fetchall()
        
        for row in rows:
            print row.FBillNo, row.FBillerName, chardet.detect(row.FBillerName.decode('big5').encode('utf-8'))
        
        return {'type': 'ir.actions.act_window_close'}