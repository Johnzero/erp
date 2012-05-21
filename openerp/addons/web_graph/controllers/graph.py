# -*- coding: utf-8 -*-

import tools

try:
    # embedded
    import openerp.addons.web.common.http as openerpweb
    from openerp.addons.web.controllers.main import View
except ImportError:
    # standalone
    import web.common.http as openerpweb
    from web.controllers.main import View

from lxml import etree

class GraphView(View):
    _cp_path = '/web_graph/graph'
    
    @tools.cache(timeout=3600)
    def from_db(self, obj, graph_config, domain, group_by, context):
        ##
        ##{'axe_x': 'stamp', 'label': 'source', 'type': 'lines', 'stack': 'True', 'axe_y':'amount'}
        ##
        result = {}
        
        label = graph_config['label']
        axe_x = graph_config['axe_x']
        axe_y = graph_config['axe_y']

        ids = obj.search([])
        if ids:
            records = obj.read(ids)
            dataset = {}
            for r in records:
                if dataset.has_key(r[label]):
                    dataset.get(r[label])['data'].append([r[axe_x], r[axe_y]])
                else:
                    dataset[r[label]] = {'label':r[label], 'data':[]}
        return [ dataset[k] for k in dataset]
    
    @openerpweb.jsonrequest
    def data_get(self, req, model=None, domain=[], group_by=[], view_id=False, context={}, **kwargs):
        obj = req.session.model(model)
        xml = obj.fields_view_get(view_id, 'graph')
        graph_xml = etree.fromstring(xml['arch'])
        
        graph_config = {}
        
        
        graph_config['type'] = graph_xml.attrib.get('type') or 'lines'
        graph_config['stack'] = graph_xml.attrib.get('stack') or False
        for element in graph_xml.iter():
            key = element.tag
            value = element.attrib.get('name')
            if value:
                graph_config[key] = value
        
        data = self.from_db(obj, graph_config, domain, group_by, context)

        result = {
            'data': data,
            'config': graph_config
        }
        return result

