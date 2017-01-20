odoo.define('pos_hn.update_company_fields', function(require){
    "use strict";
    var module = require('point_of_sale.models');
    var models = module.PosModel.prototype.models;

    for(var i=0; i<models.length; i++){
        var model = models[i];

        if(model.model == 'res.company'){
            model.fields.push('street','street2','city','state_id');
        }
    }
    module.load_models([{
        model: 'poshn.cai',
        condition: function(self){ return true; },
        fields: ['codigo_cai', 'fecha_limite_emision', 'rango_autorizado_desde', 'rango_autorizado_hasta'],
        domain: [['activo','=',true]],
        loaded: function(self, codigos_cai){
            self.config_cai = codigos_cai[0];
        }
    },
    {
        model:  'ir.sequence',
        fields: ['id', 'code','number_next','implementation','padding','regimen_aplicado','punto_emision','tipo_documento','establecimiento','rango_desde','rango_hasta'],
        domain: [['regimen_aplicado','=',true]],
        loaded: function(self,ir_sequence){
            self.dei_sequence = ir_sequence[0];

            var orders = self.db.get_orders();
            for (var i = 0; i < orders.length; i++) {
               self.dei_sequence.number_next = Math.max(self.dei_sequence.number_next, orders[i].data.sequence_number+1);
            }
        }
    }]);
});

odoo.define('pos_hn.modify_order_name', function(require){
    "use strict";
    var module = require('point_of_sale.models');

    var OrderlineCollection = Backbone.Collection.extend({
        model: module.Orderline,
    });

    var PaymentlineCollection = Backbone.Collection.extend({
        model: module.Paymentline,
    });

    module.Order.prototype.initialize = function(attributes, options){
        Backbone.Model.prototype.initialize.apply(this, arguments);
        var self = this;
        options  = options || {};

        this.init_locked = true;
        this.pos = options.pos;
        this.selected_orderline = undefined;
        this.selected_paymentline = undefined;
        this.screen_data = {};  // see Gui
        this.temporary = options.temporary || false;
        this.creation_date  = new Date();
        this.to_invoice = false;
        this.orderlines = new OrderlineCollection();
        this.paymentlines = new PaymentlineCollection();
        this.pos_session_id = this.pos.pos_session.id;
        this.finalized = false; // if true, cannot be modified.

        this.set({ client: null });

        if (options.json) {
            this.init_from_JSON(options.json);
        } else {
            this.sequence_number = this.pos.pos_session.sequence_number++;
            this.uid  = this.generate_unique_id();
            this.name = this.uid;
            this.validation_date = undefined;
            this.fiscal_position = _.find(this.pos.fiscal_positions, function(fp) {
                return fp.id === self.pos.config.default_fiscal_position_id[0];
            });
        }

        this.on('change',              function(){ this.save_to_db("order:change"); }, this);
        this.orderlines.on('change',   function(){ this.save_to_db("orderline:change"); }, this);
        this.orderlines.on('add',      function(){ this.save_to_db("orderline:add"); }, this);
        this.orderlines.on('remove',   function(){ this.save_to_db("orderline:remove"); }, this);
        this.paymentlines.on('change', function(){ this.save_to_db("paymentline:change"); }, this);
        this.paymentlines.on('add',    function(){ this.save_to_db("paymentline:add"); }, this);
        this.paymentlines.on('remove', function(){ this.save_to_db("paymentline:rem"); }, this);

        this.init_locked = false;
        this.save_to_db();

        return this;
	};

    module.Order.prototype.init_from_JSON = function(json){
        var client;
        this.sequence_number = json.sequence_number;
        this.pos.pos_session.sequence_number = Math.max(this.sequence_number+1,this.pos.pos_session.sequence_number);
        this.session_id    = json.pos_session_id;
        this.uid = json.uid;
        this.name = this.uid;
        this.validation_date = json.creation_date;

        if (json.fiscal_position_id) {
            var fiscal_position = _.find(this.pos.fiscal_positions, function (fp) {
                return fp.id === json.fiscal_position_id;
            });

            if (fiscal_position) {
                this.fiscal_position = fiscal_position;
            } else {
                console.error('ERROR: trying to load a fiscal position not available in the pos');
            }
        }

        if (json.partner_id) {
            client = this.pos.db.get_partner_by_id(json.partner_id);
            if (!client) {
                console.error('ERROR: trying to load a parner not available in the pos');
            }
        } else {
            client = null;
        }
        this.set_client(client);

        this.temporary = false;
        this.to_invoice = false;

        var orderlines = json.lines;
        for (var i = 0; i < orderlines.length; i++) {
            var orderline = orderlines[i][2];
            this.add_orderline(new exports.Orderline({}, {pos: this.pos, order: this, json: orderline}));
        }

        var paymentlines = json.statement_ids;
        for (var i = 0; i < paymentlines.length; i++) {
            var paymentline = paymentlines[i][2];
            var newpaymentline = new exports.Paymentline({},{pos: this.pos, order: this, json: paymentline});
            this.paymentlines.add(newpaymentline);

            if (i === paymentlines.length - 1) {
                this.select_paymentline(newpaymentline);
            }
        }
    };

    module.Order.prototype.generate_unique_id = function(){
        this.sequence_number = this.pos.dei_sequence.number_next++;

        function zero_pad(num,size){
            var s = ""+num;
            while (s.length < size) {
                s = "0" + s;
            }
            return s;
        }

        return this.pos.dei_sequence.punto_emision +"-"+
				   this.pos.dei_sequence.establecimiento +"-"+
				   this.pos.dei_sequence.tipo_documento +"-"+
                    zero_pad(this.sequence_number,8); 
    };
});
