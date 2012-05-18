# -*- coding: utf-8 -*-
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

    @openerpweb.jsonrequest
    def data_get(self, req, model=None, domain=[], context={}, group_by=[], view_id=False, orientation=False, stacked=False, mode="bar", **kwargs):
        obj = req.session.model(model)

        res = obj.fields_view_get(view_id, 'graph')
        fields = res['fields']
        toload = filter(lambda x: x not in fields, group_by)
        if toload:
            fields.update( obj.fields_get(toload, context) )

        tree = etree.fromstring(res['arch'])

        pos = 0
        xaxis = group_by or []
        yaxis = []
        for field in tree.iter(tag='field'):
            if (field.tag != 'field') or (not field.get('name')):
                continue
            assert field.get('name'), "This <field> tag must have a 'name' attribute."
            if (not group_by) and ((not pos) or field.get('group')):
                xaxis.append(field.get('name'))
            if pos and not field.get('group'):
                yaxis.append(field.get('name'))
            pos += 1

        assert len(xaxis), "No field for the X axis!"
        assert len(yaxis), "No field for the Y axis!"

        # Convert a field's data into a displayable string

        
        result = []
        print domain,  yaxis+[xaxis[0]], [xaxis[0]]
        res = obj.read_group(domain, yaxis+[xaxis[0]], [xaxis[0]], context=context)
        for record in res:
            result.append(record)

        res = {
            'data': result,
            
        }
        return res

