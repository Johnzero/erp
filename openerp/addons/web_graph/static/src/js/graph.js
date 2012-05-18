/*---------------------------------------------------------
 * OpenERP web_graph
 *---------------------------------------------------------*/

openerp.web_graph = function (openerp) {

var QWeb = openerp.web.qweb,
     _lt = openerp.web._lt;
openerp.web.views.add('graph', 'openerp.web_graph.GraphView');
openerp.web_graph.GraphView = openerp.web.View.extend({
    display_name: _lt('Graph'),
    
    init: function(parent, dataset, view_id, options) {
        this._super(parent);
        this.ready = $.Deferred();
        this.model = dataset.model;
        this.view_id = view_id;
        this.set_default_options(options);
        
        this.renderer = null;
    },
    
    start: function() {
        this._super();
        return this.rpc("/web/view/load",
                        {"model": this.model,
                        "view_id": this.view_id,
                        "view_type":"graph"
                        },
                    this.on_loaded);
    },
    stop: function() {
        if (this.renderer) {
            clearTimeout(this.renderer);
        }
        this._super();
    },
    
    on_loaded: function(data) {
        //console.log(data)
        this.fields_view = data;

    },
    /*
     * get data here.
    */
    do_search: function(domain, context, group_by) {
        this.rpc(
            '/web_graph/graph/data_get',
            {
                model: this.model,
                domain: domain,
                context: context,
                group_by: group_by,
                view_id: this.view_id,

            }, this.on_search
        );
    },
    
    on_search: function(result){
        console.log(result);
    },
    
    do_show: function() {
        this.do_push_state({});
        return this._super();
    }
});
};
// vim:et fdc=0 fdl=0: