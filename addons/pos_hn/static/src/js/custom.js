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
        loaded: function(self, ir_sequence){
						
			for(var i=0; i<ir_sequence.length; i++){
				if(ir_sequence[i].id === self.config.sequence_id[0]){
					self.dei_sequence = ir_sequence[i];
				}
			}
			
            var orders = self.db.get_orders();
            for (var i = 0; i < orders.length; i++) {
               self.dei_sequence.number_next = Math.max(self.dei_sequence.number_next, orders[i].data.sequence_number+1);
            }
        }
    },
	{
		model: 'stock.quant',
		fields: ['id','lot_id','product_id','location_id'],
		domain: function(self){return [['lot_id','!=',false], ['location_id','=', self.shop.id]];},
		loaded: function(self, quants){
			self.available_lots_ids = quants.map(function (quant) { 
				return quant.lot_id[0];
			});
		}
	},
	{
		model: 'stock.production.lot',
		fields: ['id','product_id','name', 'quant_ids'],
		domain: function(self){return [['id','in', self.available_lots_ids]];},
		loaded: function(self, product_lots){
			self.product_lots = product_lots;
		}
	}]);
});

odoo.define('pos_hn.modify_order_name', function(require){
    "use strict";
	var gui = require('point_of_sale.gui');
	var popup = require('point_of_sale.popups');
	var core = require('web.core');
	
	var _t = core._t;
	
	gui.Gui.prototype.close = function(){
		var self = this;
        var pending = this.pos.db.get_orders().length;
		var unpaid = this.pos.db.get_unpaid_orders().length;
		
		if(!unpaid){
			this.pos.add_new_order();
		}
		
        if (!pending) {
            this._close();
        } else {
            this.pos.push_order().always(function() {
                var pending = self.pos.db.get_orders().length;
                if (!pending) {
                    self._close();
                } else {
                    var reason = self.pos.get('failed') ? 
                                 'configuration errors' : 
                                 'internet connection issues';  

                    self.show_popup('confirm', {
                        'title': _t('Offline Orders'),
                        'body':  _t(['Some orders could not be submitted to',
                                     'the server due to ' + reason + '.',
                                     'You can exit the Point of Sale, but do',
                                     'not close the session before the issue',
                                     'has been resolved.'].join(' ')),
                        'confirm': function() {
                            self._close();
                        },
                    });
                }
            });
        }
	};

	
    var module = require('point_of_sale.models');
	
    var OrderlineCollection = Backbone.Collection.extend({
        model: module.Orderline,
    });

    var PaymentlineCollection = Backbone.Collection.extend({
        model: module.Paymentline,
    });
	
	module.PosModel.prototype.add_new_order = function(with_increment){
		with_increment = with_increment || 'yes';
		
		var order = new module.Order({with_increment:with_increment},{pos:this});
		var client_id = this.config.default_client[0];
		var client = this.db.get_partner_by_id(client_id);
		order.set_client(client);
        this.get('orders').add(order);
        this.set('selectedOrder', order);
        return order;
	};
	
	module.PosModel.prototype.set_start_order = function(){
		var orders = this.get('orders').models;
        
        if (orders.length && !this.get('selectedOrder')) {
            this.set('selectedOrder',orders[0]);
        } else {
			if(orders.length === 0){
				this.add_new_order('yes');
			}
        }
	};
	
	module.PosModel.prototype.on_removed_order = function(removed_order, index, reason){
		
		var order_list = this.get_order_list();
        if( (reason === 'abandon' || removed_order.temporary) && order_list.length > 0){
            this.set_order(order_list[index] || order_list[order_list.length -1]);
        }
		else{
			if(reason === 'abandon')
			{
				this.add_new_order('no');
			}
			else{
				if(order_list.length === 0){
					
					this.add_new_order();
				}
				this.set_order(order_list[0] || order_list[order_list.length -1]);
				//this.gui.show_screen(this.gui.startup_screen);
			}
        }
	};
	
	module.PosModel.prototype.load_orders = function(){
		var jsons = this.db.get_unpaid_orders();
        var orders = [];
        var not_loaded_count = 0; 

        for (var i = 0; i < jsons.length; i++) {
            var json = jsons[i];
			
			orders.push(new module.Order({order_index:i, unpaid_orders_qty: jsons.length},{
				pos:  this,
				json: json,
			}));
			
        }

        if (not_loaded_count) {
            console.info('There are '+not_loaded_count+' locally saved unpaid orders belonging to another session');
        }
        
        orders = orders.sort(function(a,b){
            return a.sequence_number - b.sequence_number;
        });

        if (orders.length) {
            this.get('orders').add(orders);
        }
	};
	
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
            this.init_from_JSON(options.json, attributes);
        } else {
			
			attributes  = attributes || {};
			var step = 1;
			
			if(attributes.with_increment){
				if(attributes.with_increment === 'no'){
					step = 0;
				}
			}
			
            this.sequence_number = Math.max(this.pos.pos_session.sequence_number, this.pos.dei_sequence.number_next);
            this.pos.pos_session.sequence_number = this.sequence_number + step;
			
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

    module.Order.prototype.init_from_JSON = function(json, attributes){
		
		attributes  = attributes || {};

        var client;
        this.sequence_number = Math.max(json.sequence_number, this.pos.pos_session.sequence_number);
        this.pos.pos_session.sequence_number = this.sequence_number + 1;
        this.session_id = json.pos_session_id;
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
            this.add_orderline(new module.Orderline({}, {pos: this.pos, order: this, json: orderline}));
        }

        var paymentlines = json.statement_ids;
        for (var i = 0; i < paymentlines.length; i++) {
            var paymentline = paymentlines[i][2];
            var newpaymentline = new module.Paymentline({},{pos: this.pos, order: this, json: paymentline});
            this.paymentlines.add(newpaymentline);

            if (i === paymentlines.length - 1) {
                this.select_paymentline(newpaymentline);
            }
        }
    };

    module.Order.prototype.generate_unique_id = function(){
		//this.sequence_number = Math.max(this.pos.dei_sequence.number_next+1, this.pos.pos_session.sequence_number);
		
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
		
	module.Order.prototype.get_amount_in_words = function(){

		function Unidades(num){
			switch(num){
				case 1: return "UN";
				case 2: return "DOS";
				case 3: return "TRES";
				case 4: return "CUATRO";
				case 5: return "CINCO";
				case 6: return "SEIS";
				case 7: return "SIETE";
				case 8: return "OCHO";
				case 9: return "NUEVE";
			}
			return "";
		}

		function Decenas(num){
			var decena = Math.floor(num/10);
			var unidad = num-(decena * 10);

			switch(decena)
			{
				case 1:
					switch(unidad){
						case 0: return "DIEZ";
						case 1: return "ONCE";
						case 2: return "DOCE";
						case 3: return "TRECE";
						case 4: return "CATORCE";
						case 5: return "QUINCE";
						default: return "DIECI" + Unidades(unidad);
					}
				case 2:
					switch(unidad){
						case 0: return "VEINTE";
						default: return "VEINTI" + Unidades(unidad);
					}
				case 3: return DecenasY("TREINTA", unidad);
				case 4: return DecenasY("CUARENTA", unidad);
				case 5: return DecenasY("CINCUENTA", unidad);
				case 6: return DecenasY("SESENTA", unidad);
				case 7: return DecenasY("SETENTA", unidad);
				case 8: return DecenasY("OCHENTA", unidad);
				case 9: return DecenasY("NOVENTA", unidad);
				case 0: return Unidades(unidad);
			}
		}
		
		function DecenasY(strSin, numUnidades){
			if (numUnidades > 0)
				return strSin + " Y " + Unidades(numUnidades)
			return strSin;
		}

		function Centenas(num){
			var centenas = Math.floor(num / 100);
			var decenas = num-(centenas * 100);

			switch(centenas){
				case 1:
					if (decenas > 0)
						return "CIENTO " + Decenas(decenas);
					return "CIEN";
				case 2: return "DOSCIENTOS " + Decenas(decenas);
				case 3: return "TRESCIENTOS " + Decenas(decenas);
				case 4: return "CUATROCIENTOS " + Decenas(decenas);
				case 5: return "QUINIENTOS " + Decenas(decenas);
				case 6: return "SEISCIENTOS " + Decenas(decenas);
				case 7: return "SETECIENTOS " + Decenas(decenas);
				case 8: return "OCHOCIENTOS " + Decenas(decenas);
				case 9: return "NOVECIENTOS " + Decenas(decenas);
			}

			return Decenas(decenas);
		}

		function Seccion(num, divisor, strSingular, strPlural){
			var cientos = Math.floor(num / divisor)
			var resto = num-(cientos * divisor)

			var letras = "";

			if (cientos > 0)
				if (cientos > 1)
					letras = Centenas(cientos) + " " + strPlural;
				else
					letras = strSingular;

			if (resto > 0)
				letras += "";

			return letras;
		}

		function Miles(num){
			var divisor = 1000;
			var cientos = Math.floor(num / divisor)
			var resto = num-(cientos * divisor)

			var strMiles = Seccion(num, divisor, "UN MIL", "MIL");
			var strCentenas = Centenas(resto);

			if(strMiles == "")
				return strCentenas;

			return strMiles + " " + strCentenas;
		}

		function Millones(num){
			var divisor = 1000000;
			var cientos = Math.floor(num / divisor)
			var resto = num-(cientos * divisor)

			var strMillones = Seccion(num, divisor, "UN MILLON DE", "MILLONES DE");
			var strMiles = Miles(resto);

			if(strMillones == "")
				return strMiles;

			return strMillones + " " + strMiles;
		}

		function NumeroALetras(num){
			var data = {
				numero: num,
				enteros: Math.floor(num),
				centavos: (((Math.round(num * 100))-(Math.floor(num) * 100))),
				letrasCentavos: "",
				letrasMonedaPlural: 'LEMPIRAS',//"PESOS", 'Dólares', 'Bolívares', 'etcs'
				letrasMonedaSingular: 'LEMPIRA', //"PESO", 'Dólar', 'Bolivar', 'etc'

				letrasMonedaCentavoPlural: "CENTAVOS",
				letrasMonedaCentavoSingular: "CENTAVO"
			};

			if (data.centavos > 0) {
				data.letrasCentavos = "CON " + (function (){
					if (data.centavos == 1)
						return Millones(data.centavos) + " " + data.letrasMonedaCentavoSingular;
					else
						return Millones(data.centavos) + " " + data.letrasMonedaCentavoPlural;
					})();
			};

			if(data.enteros == 0)
				return "CERO " + data.letrasMonedaPlural + " " + data.letrasCentavos;
			if (data.enteros == 1)
				return Millones(data.enteros) + " " + data.letrasMonedaSingular + " " + data.letrasCentavos;
			else
				return Millones(data.enteros) + " " + data.letrasMonedaPlural + " " + data.letrasCentavos;
		}
		
		var amount = this.get_total_with_tax();
		return NumeroALetras(amount);
	};

	module.Order.prototype.display_lot_popup = function(){
		var order_line = this.get_selected_orderline();
        if (order_line){
            var pack_lot_lines =  order_line.compute_lot_lines();

			var product_id = pack_lot_lines.order_line.product.id;
			var product_available_serial_numbers = this.pos.product_lots.filter(function (lot) {
				if(lot.product_id[0] == product_id)
				{
					return lot;
				}
			});
			
            this.pos.gui.show_popup('packlotline-select', {
                'title': _t('Lot/Serial Number(s) Required'),
                'pack_lot_lines': pack_lot_lines,
                'order': this,
				'product_available_serial_numbers': product_available_serial_numbers
            });
        }
	};
	
	var PackLotLinePopupWidgetSelect = popup.extend({
		template: 'PackLotLinePopupWidget',
		events: _.extend({}, popup.prototype.events, {
			'click .remove-lot': 'remove_lot',
			'blur .serial-lot-select': 'lose_input_focus',
			'change .serial-lot-select': 'add_lot'
		}),

		show: function(options){
			this._super(options);
			this.focus();
		},

		click_confirm: function(){
			var pack_lot_lines = this.options.pack_lot_lines;
			this.$('.serial-lot-select').each(function(index, el){
				var cid = $(el).attr('cid');
				var lot_name = $(el).find("option:selected").text();
				var pack_line = pack_lot_lines.get({cid: cid});
				pack_line.set_lot_name(lot_name);
			});
			pack_lot_lines.remove_empty_model();
			pack_lot_lines.set_quantity_by_lot();
			this.options.order.save_to_db();
			this.gui.close_popup();
		},

		add_lot: function(ev) {	
			var pack_lot_lines = this.options.pack_lot_lines;
			var $input = $(ev.target);
			var cid = $input.attr('cid');
			var lot_name = $(ev.target).find("option:selected").text();
			
			var lot_model = pack_lot_lines.get({cid: cid});
			lot_model.set_lot_name(lot_name); 
			if(!pack_lot_lines.get_empty_model()){
				var new_lot_model = lot_model.add();
				this.focus_model = new_lot_model;
			}
			pack_lot_lines.set_quantity_by_lot();
			
			this.renderElement();
			this.focus();
		},

		remove_lot: function(ev){
			var pack_lot_lines = this.options.pack_lot_lines,
				$input = $(ev.target).prev(),
				cid = $input.attr('cid');
			var lot_model = pack_lot_lines.get({cid: cid});
			lot_model.remove();
			pack_lot_lines.set_quantity_by_lot();
			this.renderElement();
		},

		lose_input_focus: function(ev){
			var $input = $(ev.target);
			var cid = $input.attr('cid');
			var lot_model = this.options.pack_lot_lines.get({cid: cid});
			lot_model.set_lot_name($input.find("option:selected").text());
		},

		focus: function(){
			this.$("select[autofocus]").focus();
			this.focus_model = false;   // after focus clear focus_model on widget
		}
	});
	gui.define_popup({name:'packlotline-select', widget:PackLotLinePopupWidgetSelect});

});


