# -*- coding: utf-8 -*-

from osv import osv
import pyodbc
from tools import DEFAULT_SERVER_DATETIME_FORMAT,get_initial

CONN_STR = 'DRIVER={SQL Server};SERVER=127.0.0.1;DATABASE=fg;UID=bi;PWD=xixihaha'

def clear_field(i, r=None):
    if not i:
        return ''
    e_list = {
        'FGC002.1573':'囍',
        'FGC002.575':'福州小糸大億',
        'FGC002.601':'中投证劵',
        'FGC002.945':'倪贇同学',
        'FGC002.977':'祝倪贇同学',
        '16401':'董玥',
    }
    if r:
        if e_list.has_key(r):
            return e_list.get(r) 
    try:
        s = ("%s" % i).decode('GB2312').encode('utf-8')
    except:
        s = ("%s" % i)
    return s

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
        state_sql = """
            select DISTINCT(FProvince) from t_Organization
        """
        # save state
        conn = pyodbc.connect(CONN_STR)
        cursor = conn.cursor()
        cursor.execute(state_sql)
        rows = cursor.fetchall()
        state_dict = {}
        state_obj = self.pool.get('res.country.state')
        for row in rows:
            if row:
                name = clear_field(row[0])
                id = state_obj.create(cr, uid, {'name':name, 'code':get_initial(name), 'country_id':49,})
                state_dict[clear_field(row[0])] = id
        
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()

        #save category first
        cate_dict = dict()
        partner_cate_obj = self.pool.get('res.partner.category')
        partner_obj = self.pool.get('res.partner')
        address_obj = self.pool.get('res.partner.address')
        
        for row in rows:
            number = clear_field(row[10])
            name = clear_field(row[9])
            if not cate_dict.has_key(number):
                id = partner_cate_obj.create(cr, uid, {'name':name})
                cate_dict[number] = id
            
            cate_id = cate_dict.get(number)

            partner = {
                'fullnum':clear_field(row[0]),
                'name':clear_field(row[1], clear_field(row[0])),
                'customer':True,
                'category_id':[(6, 0, [cate_id])],
            }
            partner_id = partner_obj.create(cr, uid, partner)
            
            address = {
                'partner_id': partner_id,
                'type':'default',
                'country_id':49,
                
                }
            if row[2]:
                address['name'] = clear_field(row[2])
            else:
                address['name'] = partner['name']
            if row[7]:
                address['state_id'] = state_dict.get(clear_field(row[7]))
            if row[6]:
                address['city'] = clear_field(row[6])
            if row[3]:
                address['mobile'] = clear_field(row[3])
            if row[4]:
                address['phone'] = clear_field(row[4])
            if row[5]:
                address['street'] = clear_field(row[5])
            address_obj.create(cr, uid, address)

        return {'type': 'ir.actions.act_window_close'}


class user_import(osv.osv_memory):
    _name = "fg_sale.user.wizard.import"
    _description = "user importing."

    _columns = {

    }

    def import_user(self, cr, uid, ids, context=None):
        # save user
        user_sql = """
        SELECT
            FUserID,
            FName,
            FForbidden
        FROM
            t_User
        WHERE
            FSID IS NOT NULL
        """
        conn = pyodbc.connect(CONN_STR)
        cursor = conn.cursor()
        cursor.execute(user_sql)
        rows = cursor.fetchall()
        user_obj = self.pool.get('res.users')
        for row in rows:
            name = clear_field(row[1], clear_field(row[0]))
            user_obj.create(cr, uid, {
                'login': name,
                'name': name,
                'jid':row[0],
                'password':'8751888',
                'signature': name,
                'company_id':1,
                'groups_id':[(6,0,[7])],
                'active':row[2]==0,
            })

        return {'type': 'ir.actions.act_window_close'}


class product_import(osv.osv_memory):
    _name = "fg_sale.product.wizard.import"
    _description = "product importing."

    _columns = {
        
    }

    def import_product(self, cr, uid, ids, context=None):
        cate_sql = """
        SELECT
            FNumber,
            FName
        FROM
            t_Item
        WHERE
            FItemClassID = 4
        AND FLevel = 1
        """
        uom_sql = """
        SELECT
            tmu.FNumber,
            tmu.FName,
            tmu.FCoefficient
        FROM
            t_MeasureUnit tmu;
        """
        product_sql = """
        SELECT
            icitem.FModel,
            icitem.FName,
            icitem.FNumber,
            icitem.FSalePrice,
            icitem.FNote,
            item.FName AS Category_Name,
            item.FNumber AS Category_Num,
            unit.FNumber AS Unit_Num,
            unit.FName AS Unit_Name,
            dep.FName AS Dep_Name
        FROM
            t_icitem icitem
        JOIN t_Item item ON item.FItemID = icitem.FParentID
        JOIN t_MeasureUnit unit ON unit.FItemID = icitem.FSaleUnitID
        JOIN t_Department dep ON dep.FItemID = icitem.FSource;
        """
        product_cate_obj = self.pool.get('product.category')
        product_uom_obj = self.pool.get('product.uom')
        product_obj = self.pool.get('product.product')
        cate_dict = dict()
        uom_dict = dict()
        conn = pyodbc.connect(CONN_STR)
        #category
        cursor = conn.cursor()
        cursor.execute(cate_sql)
        rows = cursor.fetchall()
        for row in rows:
            id = product_cate_obj.create(cr, uid, {'name': clear_field(row[1]), 'fullnum':clear_field(row[0])})
            cate_dict[clear_field(row[0])] = id

        #uom
        cursor = conn.cursor()
        cursor.execute(uom_sql)
        rows = cursor.fetchall()
        for row in rows:
            uom = {
                'fullnum':clear_field(row[0]),
                'name':clear_field(row[1]),
                'rounding':1,
                'factor':row[2],
                'category_id':1,
                'uom_type': (row[2] > 1) and 'bigger' or 'smaller'
            }
            id = product_uom_obj.create(cr, uid, uom)
            uom_dict[clear_field(row[0])] = id

        #product
        cursor = conn.cursor()
        cursor.execute(product_sql)
        rows = cursor.fetchall()
        for row in rows:
            if not uom_dict.has_key(clear_field(row[7])):
                print row[2], 'uom not found'
                break
            if not cate_dict.has_key(clear_field(row[6])):
                print row[2], 'category not found'
                break
            product = {
                'sale_ok':True,
                'purchase_ok':True,
                'supply_method':'produce',
                'default_code':clear_field(row[0]) or '',
                'list_price':row[3],
                'standard_price':row[3],
                'uom_id':uom_dict.get(clear_field(row[7])),
                'uom_po_id':uom_dict.get(clear_field(row[7])),
                'sale_delay':1,
                'name':clear_field(row[1]),
                'type':'product',
                'categ_id':cate_dict.get(clear_field(row[6])),
                'state':'sellable',
                'fullnum':clear_field(row[2]),
                'source':clear_field(row[9]),
                'description':clear_field(row[4]) or ''
            }
            product_obj.create(cr, uid, product)

        return {'type': 'ir.actions.act_window_close'}

        
class order_import(osv.osv_memory):
    _name = "fg_sale.order.wizard.import"
    _description = "order importing."
    
    _columns = {
        
        
    }

    def import_fg_order(self, cr, uid, ids, context=None):
        pass

    
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
        