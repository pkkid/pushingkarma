/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

pk.budget = {
  API_CATEGORIES: '/api/categories/',
  API_TRANSACTIONS: '/api/transactions/',
  BUDGET_SELECTOR: '#budget',
  KEYS: {TAB:9, ENTER:13, ESC:27, UP:38, DOWN:40},
  
  init: function(selector) {
    this.container = $(selector);
    if (!this.container.length) { return; }
    console.debug('init pk.budget on '+ selector);
    this.xhr = null;
    this.search = null;
    this.init_elements();
    this.init_triggers();
    this.init_shortcuts();
    this.update_categories();
  },

  init_elements: function() {
    this.sidepanel = this.container.find('#budget-sidepanel');
    this.searchinput = this.container.find('#budget-search');
    this.transactionsbtn = this.container.find('#budget-transactions');
    this.categorylist = this.container.find('#budget-categories');
  },

  init_triggers: function() {
    var self = this;
    // Edit category budget
    this.categorylist.on('dblclick', 'tbody input', function() {
      event.preventDefault();
      self.field_edit($(this));
    });
    this.categorylist.on('blur', 'tbody input', function() {
      event.preventDefault();
      self.field_display($(this));
    });
  },

  init_shortcuts: function() {
    var self = this;
    var KEYS = this.KEYS;
    // select noteitems via keyboard
    this.categorylist.on('keydown', 'tbody input', function(event) {
      if (event.keyCode == KEYS.ENTER) {
        console.log('Save category');
        //self.save_category($(this).parents('.category'));
        //self.select_next_budget($(this).parents('.category'));
      }
    });
  },

  add_category: function(elem) {
    console.log('add_category');
  },

  delete_category: function(elem) {
    console.log('delete_category');
  },

  field_edit: function(input) {
    if (input.hasClass('dollar0')) {
      // edit field as integer
      input.val(_.trimStart(input.val(), '$').replace(',', ''));
      
    } else if (input.hasClass('dollar2')) {
      // edit field as decimal
    }
    input.attr('readonly', false);
    input.get(0).setSelectionRange(input.val().length * 2, input.val().length * 2);
  },

  field_display: function(input) {
    input.attr('readonly', true);
    if (input.hasClass('dollar0')) {
      // display field as dollar amount
      var newval = pk.utils.round(input.val(), 0);
      newval = newval.toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, '$1,');
      input.val('$'+ newval);
    } else if (input.hasClass('dollar2')) {
      // display field as exact amount
    }
  },

  request: function(method, url, data, callback) {
    var self = this;
    //this.spinner.addClass('on');
    //var data = this.request_data();
    console.log(data);
    var xhr = $.ajax({url:url, type:method, data:data, dataType:'json'});
    xhr.done(function(data, textStatus, jqXHR) { callback(data, textStatus, jqXHR); });
    //xhr.fail(function(jqXHR, textStatus, errorThrown) { self.notify(self.MESSAGE_ERROR); });
    //xhr.always(function() { self.spinner.removeClass('on'); });
  },

  save_category: function(elem) {
    var self = this;
    var data = {
      id: elem.data('id'),
      name: elem.find('input[name=category]').val(),
      budget: elem.find('input[name=budget]').val().replace(',','').replace('$',''),
    }
    console.log(elem);
    this.request('UPDATE', this.API_CATEGORIES, data, function(data) {
      console.log(data);
    });
  },
 
  update_categories: function() {
    var self = this;
    if (this.xhr) { this.xhr.abort(); }
    this.xhr = $.ajax({url:this.API_CATEGORIES, type:'GET', dataType:'json'});
    this.xhr.done(function(data, textStatus, jqXHR) {
      var ctx = {items:data};
      var html = self.templates.listcategories(ctx);
      self.categorylist.find('tbody').html(html);
    });
  },

  validate_int: function(input) {

  },

  templates: {
    listcategories: Handlebars.compile([
      '{{#each this.items}}',
      '  <tr class="category" data-id="{{this.id}}">',
      '    <td class="category"><input name="category" type="text" value="{{this.name}}" autocomplete="off" readonly="true"></td>',
      '    <td class="trend">&nbsp;</td>',
      '    <td class="budget"><input name="budget" class="dollar0" type="integer" value="${{formatDollars this.budget}}" autocomplete="off" readonly="true"></td>',
      '  </tr>',
      '{{/each}}',
    ].join('\n')),
  },

};
