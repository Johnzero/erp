# -*- coding: utf-8 -*-

from osv import osv

        
class order_import(osv.osv_memory):
    _name = "fg_sale.order.wizard_import"
    _description = "order importing."
    
    _columns = {
        
        
    }
    
    
    def import_order(self, cr, uid, ids, context=None):
        import chardet, pyodbc
        
        user_dict = {}
        parnter_dict = {}
        
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
        for u in cr.fetchall():
            user_dict[u[1].encode('utf-8')] = u[0]
        
        cr.execute("""
                   SELECT
                    "public".res_partner."id",
                    "public".res_partner."name"
                    FROM
                    "public".res_partner
                   """)
        for u in cr.fetchall():
            parnter_dict[u[1].encode('utf-8')] = u[0]

        conn = pyodbc.connect('DRIVER={SQL Server};SERVER=192.168.209.128;DATABASE=jd;UID=erp;PWD=erp')
        cursor = conn.cursor()
        cursor.execute("""
                SELECT
                FBillNo,
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
        
        missed = []
        
        for row in rows:
            order = {}
            order['name'] = ("%s" % row[0]).decode('GB2312').encode('utf-8')
            
            try:
                part = ("%s" % row[2]).decode('GB2312').encode('utf-8')
            except:
                part = ("%s" % row[2])
            try:
                user_name = ("%s" % row[5]).decode('GB2312').encode('utf-8')
            except:
                user_name = '董玥'
            
            try:
                c_user_name = ("%s" % row[6]).decode('GB2312').encode('utf-8')
                
            except:
                c_user_name = '董玥'
            
            order['date_order'] = row[1]
            order['date_confirm'] = row[7]
            
            
            order['user_id'] = user_dict.get(user_name)
            order['confirmer_id'] = user_dict.get(c_user_name)
            minus = (row[9]<0)
            order['state'] = 'done'
            order['amount_total'] = float(row[8])
            
            
            if parnter_dict.get(part):
                order['partner_id'] = parnter_dict.get(part)
                
                partner_obj = self.pool.get('res.partner')
                addr = partner_obj.address_get(cr, uid, [part], ['default'])['default']
                order['partner_shipping_id'] = addr
            elif parnter_dict.get(row[2]):
                order['partner_id'] = parnter_dict.get(row[2])
                
                partner_obj = self.pool.get('res.partner')
                addr = partner_obj.address_get(cr, uid, [row[2]], ['default'])['default']
                order['partner_shipping_id'] = addr
            
            else:
                order['partner_id'] = 1
                order['partner_shipping_id'] = 1
                missed.append(row[0])
                
            
            print row[0]
            self.pool.get('fg_sale.order').create(cr, uid, order)
            
        
        print missed, 'missed'
        
        return {'type': 'ir.actions.act_window_close'}