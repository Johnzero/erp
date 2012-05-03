# -*- coding: utf-8 -*-

from osv import osv
import pyodbc

CONN_STR = 'DRIVER={SQL Server};SERVER=127.0.0.1;DATABASE=jt;UID=erp;PWD=erp'

class customer_import(osv.osv_memory):
    _name = "fg_sale.customer.wizard.import"
    _description = "customer importing."
    
    _columns = {
        
    }
    
    def import_customer(self, cr, uid, ids, context=None):
        
        sql = """
        SELECT
        	org.FNumber,
        	org.FName,
        	org.FContact,
        	org.FPhone,
        	org.FFax,
        	org.FAddress,
        	org.FCity,
        	org.FProvince,
        	org.FCountry,
        	item.FName AS Category,
        	item.FNumber AS Category_Number
        FROM
        	t_Organization org
        JOIN t_Item item ON item.FItemID = org.FParentID
        """
        conn = pyodbc.connect(CONN_STR)
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        
        #save category first
        cate_dict = dict()
        for row in rows:
            number = ("%s" % row[10]).decode('GB2312').encode('utf-8')
            name = ("%s" % row[9]).decode('GB2312').encode('utf-8')
            if not cate_dict.has_key(number):
                cate_dict[number] = name
            
        
        partner_cate_obj = self.pool.get('res.partner.category')
        
        
        
        
        
        return {'type': 'ir.actions.act_window_close'}


class user_import(osv.osv_memory):
    _name = "fg_sale.user.wizard.import"
    _description = "user importing."

    _columns = {

    }

    def import_user(self, cr, uid, ids, context=None):
        conn_str = 'DRIVER={SQL Server};SERVER=127.0.0.1;DATABASE=jt;UID=erp;PWD=erp'



        return {'type': 'ir.actions.act_window_close'}


class product_import(osv.osv_memory):
    _name = "fg_sale.product.wizard.import"
    _description = "product importing."

    _columns = {
        
    }

    def import_product(self, cr, uid, ids, context=None):
        conn_str = 'DRIVER={SQL Server};SERVER=127.0.0.1;DATABASE=jt;UID=erp;PWD=erp'



        return {'type': 'ir.actions.act_window_close'}

        
class order_import(osv.osv_memory):
    _name = "fg_sale.order.wizard.import"
    _description = "order importing."
    
    _columns = {
        
        
    }
    
    def import_order_line(self, cr, uid, ids, context=None):
        
        #take uoms out.
        uom_dict = dict()
        cr.execute("""
                   SELECT
                    "public".product_uom."id",
                    "public".product_uom."name"
                    FROM
                    "public".product_uom
                   """)
        for u in cr.fetchall():
            uom_dict[u[1].encode('utf-8')] = u[0]
        
        #take product.
        product_dict = dict()
        conn = pyodbc.connect('DRIVER={SQL Server};SERVER=192.168.209.128;DATABASE=jt;UID=erp;PWD=erp')
        #conn = pyodbc.connect('DRIVER={SQL Server};SERVER=127.0.0.1;DATABASE=AIS20101008134938;UID=bi;PWD=xixihaha')
        cursor = conn.cursor()
        cursor.execute("select FNumber,FItemID from t_ICItem;")
        rows = cursor.fetchall()
        
        
        product_obj = self.pool.get('product.product')
        

        
        for row in rows:
            product = None
            if row[0] and row[1]:
                num = ("%s" % row[0]).decode('GB2312').encode('utf-8')
                product = product_obj.search(cr, uid, [('fullnum', '=', num)], context=context )
                product_dict[num] = product[0]
    
        
        order_list = {}
        #get order id.
        cr.execute("""
                  SELECT
                           ID,
                           NAME
                   FROM
                           fg_sale_order;
                  """)
        for u in cr.fetchall():
           order_list[u[1].encode('utf-8')] = u[0]
        
        
        #get all sell entry.
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                    ic.FBillNo,
                    ics.FEntryID,
                    item.FNumber,
                    t007.FName,
                    ics.FAuxQty,
                    ics.FQty,
                    ics.FEntrySelfI0441,
                    ics.FPrice,
                    ics.FAllAmount,
                    ics.FNote
            FROM
                    ICSaleEntry ics
            INNER JOIN t_MeasureUnit t007 ON t007.FItemID = ics.FUnitID
            INNER JOIN ICSale ic ON ic.FInterID = ics.FInterID
            INNER JOIN t_IcItem item ON item.FItemID = ics.FItemID
        """)
        rows = cursor.fetchall()
        l = len(rows)
        for row in rows:
            line = {}
            line['order_id'] = order_list.get(("%s" % row[0]).decode('GB2312').encode('utf-8'))
            if not line['order_id']:
                print 'no order for ', row[0]
                break
            
            line['sequence'] = int(row[1])
            
            line['product_id'] = product_dict.get(row[2])
            if not line['product_id']:
                print 'no product for ', row[2]
                break
            
            line['product_uom'] = uom_dict.get(("%s" % row[3]).decode('GB2312').encode('utf-8').replace('（','(').replace('）',')'))
            if not line['product_uom']:
                print 'no product_uom for ', row[3]
                break
            
            line['product_uom_qty'] = int(row[4])
            line['aux_qty'] = int(row[5])
            line['unit_price'] = float(row[6])
            line['subtotal_amount'] = float(row[8])
            if row[9]:
                try:
                    line['note'] = ("%s" % row[9]).decode('GB2312').encode('utf-8')
                except:
                    line['note'] = ("%s" % row[9])
            print '%s to go' % l
            l = l - 1
            self.pool.get('fg_sale.order.line').create(cr, uid, line)
            
        return {'type': 'ir.actions.act_window_close'}
    
    def import_order(self, cr, uid, ids, context=None):
        
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
                            "public".res_partner."fullnum"
                    FROM
                            "public".res_partner
                    WHERE
                            fullnum IS NOT NULL
                   """)
        for u in cr.fetchall():
            parnter_dict[u[1].encode('utf-8')] = u[0]

        conn = pyodbc.connect('DRIVER={SQL Server};SERVER=192.168.209.128;DATABASE=jt;UID=erp;PWD=erp')
        #conn = pyodbc.connect('DRIVER={SQL Server};SERVER=127.0.0.1;DATABASE=AIS20101008134938;UID=bi;PWD=xixihaha')
        sql_1 = """
           SELECT
               FBillNo,
               FDate,
               t_Item.FNumber,
               FNote,
               tu_1.FName AS FBillerName,
               FInvoiceAmount,
               FROB,
               tu_2.FName AS FCheckerName,
               FCheckDate,
               FCancellation
           FROM ICSale
               JOIN t_Item ON FCustID = t_Item.FItemID
               JOIN t_User tu_1 ON FBillerID = tu_1.FUserID
               JOIN t_User tu_2 ON FCheckerID = tu_2.FUserID
               JOIN t_Organization t_o ON FCustID = t_o.FItemID
               
               """
        sql_2 = """
                           SELECT
                                   FBillNo,
                                   FDate,
                                   t_Item.FNumber AS FPartnerName,
                                   FNote,
                                   tu_1.FName AS FBillerName,
                                   FInvoiceAmount,
                                   FROB,
                                   FCheckerID,
                                   FCheckDate,
                                   FCancellation
                           FROM
                                   ICSale
                           JOIN t_Item ON FCustID = t_Item.FItemID
                           JOIN t_User tu_1 ON FBillerID = tu_1.FUserID
                           JOIN t_Organization t_o ON FCustID = t_o.FItemID
                           WHERE
                                   dbo.ICSale.FCheckerID IS NULL
                       """
        
        cursor = conn.cursor()
        
        #sql_1 for checked record. sql_2 for non-checked.
        cursor.execute(sql_1)

        rows = cursor.fetchall()
                
        for row in rows:
            order = {}
            order['name'] = ("%s" % row[0]).decode('GB2312').encode('utf-8')
            order['date_order'] = row[1]
            
            
            #try:
            #    part = ("%s" % row[2]).decode('GB2312').encode('utf-8')
            #except:
            #    part = ("%s" % row[2])
            
            order['note'] = "%s" % row[3].decode('GB2312').encode('utf-8')
            
            try:
                user_name = ("%s" % row[4]).decode('GB2312').encode('utf-8')
            except:
                user_name = '董玥'
            order['user_id'] = user_dict.get(user_name)
            
            order['amount_total'] = float(row[5])
            minus = (row[6]<0)
            
            if row[7]:
                try:
                    c_user_name = ("%s" % row[7]).decode('GB2312').encode('utf-8')
                    
                except:
                    c_user_name = '董玥'
                
                order['date_confirm'] = row[8]
                order['confirmer_id'] = user_dict.get(c_user_name)
                order['state'] = 'done'
            else:
                order['state'] = 'draft'

            if row[9] == 1:
                order['state'] = 'cancel'
            
            num = ("%s" % row[2]).decode('GB2312').encode('utf-8')
            
            if parnter_dict.get(num):
                order['partner_id'] = parnter_dict.get(num)
                
                partner_obj = self.pool.get('res.partner')
                addr = partner_obj.address_get(cr, uid, [order['partner_id']], ['default'])['default']
                order['partner_shipping_id'] = addr
            else:
                print 'missed', num
                break
            print row[0]
                
            self.pool.get('fg_sale.order').create(cr, uid, order)
            
        
        return {'type': 'ir.actions.act_window_close'}
        