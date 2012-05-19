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
        this.dataset = dataset;
        this.view_id = view_id;
        this.set_default_options(options);
        this.fields_view = {};
        
        this.model = dataset.model;
        this.chart_id = Math.floor((Math.random()*100)+1);
    },
    
    start: function() {
        this._super();
        
        this.$element.html(QWeb.render("GraphView", {
            "chart_id": this.chart_id,
            'element_id': this.widget_parent.element_id
        }));
    },
    stop: function() {
        this._super();
    },
    
    /*
     * get data here.
    */
    do_search: function(domain, context, group_by) {
        //this.on_search(null);
        
        this.rpc(
                   '/web_graph/graph/data_get',
                   {
                       'model': this.model,
                       'domain': domain,
                       'context': context,
                       'group_by': group_by,
                       'view_id': this.view_id
                
                   }, this.on_search
                );

    },
    
    on_search: function(result){
        var d1 = [];
        for (var i = 0; i < 14; i += 0.5)
            d1.push([i, Math.sin(i)]);
    
        var d2 = [[0, 3], [4, 8], [8, 5], [9, 13]];
    
        // a null signifies separate line segments
        var d3 = [[0, 12], [7, 12], null, [7, 2.5], [12, 2.5]];
        container = this.widget_parent.element_id+"-chart-"+this.chart_id,
        $.plot($("#"+container), [ d1, d2, d3 ]);
    },
    
    do_show: function() {
        this.do_push_state({});
        return this._super();
    }
});
};
// vim:et fdc=0 fdl=0: