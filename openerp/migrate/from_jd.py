# -*- coding: utf-8 -*-

import pymssql
import xmlrpclib

class RPCProxyOne(object):
    def __init__(self,ressource):
        self.host = 'localhost'
        self.port = 8070
        self.db = 'FG'
        self.user = 'admin'
        self.password = 'admin'
        
        local_url = 'http://%s:%d/xmlrpc/common'%(self.host, self.port)
        rpc = xmlrpclib.ServerProxy(local_url)
        self.uid = rpc.login(self.db, self.user, self.password)
        local_url = 'http://%s:%d/xmlrpc/object'%(self.host, self.port)
        self.rpc = xmlrpclib.ServerProxy(local_url)
        self.ressource = ressource
        
    def __getattr__(self, name):
        return lambda cr, uid, *args, **kwargs: self.rpc.execute(self.db, self.uid, self.password, self.ressource, name, *args)

class RPCProxy(object):

    def get(self, ressource):
        return RPCProxyOne(ressource)


def get_data_from_os():
    pool = RPCProxy()


def get_data_from_mssql():
    conn = pymssql.connect(host='192.168.209.128', user='erp', password='erp', database='jt')
    cursor = conn.cursor()
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
            
    for row in cursor:
        print row