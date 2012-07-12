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
    _defaults = {
        'server_port': lambda *args: 8069
    }
    
    def do_init_ratio(self, cr, uid, ids, model):
        """div all local lines which are un-synced. make it sync."""
        partner_obj = self.pool.get('res.parnter')
        
        partners = partner_obj.search(cr, uid, [('ratio','<', 1), ('ratio','!=', 0)])
        for p in partners:
            partner = partner_obj.read(cr, uid, [p])[0]
        
        
        pool1 = RPCProxy(server)
        
        partner_obj = pool1.get('res.partner')
        id = partner_obj.create({})
        
        
    
    def do_push(self, cr, uid, ids, model):
        pass

    def do_pull(self, cr, uid, ids, model):
        pass
    
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
        
        #
        #pool1 = RPCProxy(Config('localhost', 8069, 'FG', 'admin','zaq1@WSX'))
        #
        #user_obj = pool1.get('res.users')
        #user_ids = user_obj.search(cr, uid, [])
        #
        #
        #
        #for user in user_obj.read(cr, uid, user_ids, ['id','name']):
        #    print user
        
        
        
        return True
    
    
