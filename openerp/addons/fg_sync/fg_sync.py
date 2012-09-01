# -*- encoding: utf-8 -*-

from osv import osv
from osv import fields
import time
import xmlrpclib, pooler

class RPCProxyOne(object):
    def __init__(self, server, ressource):
        self.server = server
        local_url = 'http://%s:%d/xmlrpc/common'%(server.server_url,server.server_port)
        rpc = xmlrpclib.ServerProxy(local_url)
        self.uid = rpc.login(server.server_db, server.login, server.password)
        local_url = 'http://%s:%d/xmlrpc/object'%(server.server_url,server.server_port)
        self.rpc = xmlrpclib.ServerProxy(local_url)
        self.ressource = ressource
    def __getattr__(self, name):
        return lambda cr, uid, *args, **kwargs: self.rpc.execute(self.server.server_db, self.uid, self.server.password, self.ressource, name, *args)

class RPCProxy(object):
    def __init__(self, server):
        self.server = server
    def get(self, ressource):
        return RPCProxyOne(self.server, ressource)
        

class Config(object):
    def __init__(self, su, sp, sd, lo, ps):
        self.server_url = su
        self.server_port = sp
        self.server_db = sd
        self.login = lo
        self.password = ps


class fg_sync_scheduler(osv.osv):
    _name = "fg_sync.scheduler"
    _description = "order importing."
    
    _columns = {

    }
    
    
    def do_run_scheduler(self, cr, uid, ids=None, context=None):
        """Scheduler for event reminder
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of whatever’s IDs.
        @param context: A standard dictionary for contextual values
        """
        if context is None:
            context = {}
        
        
        pool1 = RPCProxy(Config('localhost', 8068, 'BAK', 'admin','zaq1@WSX'))
        target_order_obj = pool1.get('fg_sale.order')
        target_order_line_obj = pool1.get('fg_sale.order.line')
        
        source_order_obj = self.pool.get('fg_sale.order')
        source_order_line_obj = self.pool.get('fg_sale.order.line')
        
        def do_pull():
            pass
        
        def do_push():
            # get all that's not sync-ed
            print 'do push......................'
            for order_id in source_order_obj.search(cr, uid, [('sync','=',False),('state','=','done')]):
                print order_id
                #order = source_order_obj.copy_data(cr, uid, order_id)
                ##save order first. get id
                #id = target_order_obj.create(cr, uid, order)
                #print id,'id'
                ## interate lines. create, don't forget ratio.
                #source_order_obj.write(cr, uid, [order_id], {'sync':True})
                ## set both sync-ed
        
        try:
            do_push()
        except:
            print 'network error.......'
        
        return True
    
    
