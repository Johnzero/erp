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
        
        this.first_field = null;
        this.abscissa = null;
        this.ordinate = null;
        this.columns = [];
        this.group_field = null;
        
        this.is_loaded = $.Deferred();
        this.renderer = null;
    },
    
    start: function() {
        this._super();
        return this.rpc("/web/view/load",
                        {"model": this.dataset.model,
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
        //set chart type.
        this.chart = this.fields_view.arch.attrs.type || 'line';
        this.orientation = this.fields_view.arch.attrs.orientation || 'vertical';
        
        _.each(this.fields_view.arch.children, function (field) {
            var attrs = field.attrs;
            if (attrs.group) {
                this.group_field = attrs.name;
            } else if(!this.abscissa) {
                this.first_field = this.abscissa = attrs.name;
            } else {
                this.columns.push({
                    name: attrs.name,
                    operator: attrs.operator || '+'
                });
            }
        }, this);
        
        this.ordinate = this.columns[0].name;
        this.is_loaded.resolve();
    },
    /*
     * get data here.
    */
    do_search: function(domain, context, group_by) {
        
        this.$element.html(QWeb.render("GraphView", {
            "fields_view": this.fields_view,
            "chart": this.chart,
            'element_id': this.widget_parent.element_id
        }));
        
        //demo render.
        var d1 = [];
        for (var i = 0; i < 14; i += 0.5)
            d1.push([i, Math.sin(i)]);
    
        var d2 = [[0, 3], [4, 8], [8, 5], [9, 13]];
    
        // a null signifies separate line segments
        var d3 = [[0, 12], [7, 12], null, [7, 2.5], [12, 2.5]];
        container = this.widget_parent.element_id+"-"+this.chart+"chart",
        $.plot($("#"+container), [ d1, d2, d3 ]);
                
        //this.rpc(
        //    '/web_graph/graph/data_get',
        //    {
        //        model: this.model,
        //        domain: domain,
        //        context: context,
        //        group_by: group_by,
        //        view_id: this.view_id,
        //
        //    }, this.on_search
        //);
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