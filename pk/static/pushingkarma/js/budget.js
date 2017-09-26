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
    this.xhr = null;            // main actions xhr reference
    this.xhrcat = null;         // categories xhr reference
    this.xhrtrx = null;         // transactions xhr reference
    this.search = null;         // current search string
    this.init_elements();
    this.init_triggers();
    this.init_shortcuts();
    this.update_categories();
    this.update_transactions();
  },

  init_elements: function() {
    this.sidepanel = this.container.find('.sidepanel');
    this.searchinput = this.container.find('.search');
    this.transactionsbtn = this.container.find('.search-action');
    this.categorylist = this.container.find('.sidepanel-content');
    this.maincontent = this.container.find('.maincontent');
  },

  init_triggers: function() {
    var self = this;
    // search input changes
    this.searchinput.on('change paste keyup', function(event) {
      if (_.valuesIn(this.KEYS).indexOf(event.keyCode) == -1) {
        event.preventDefault();
        self.update_transactions($(this).val());
      }
    });
    // edit category or transaction
    this.container.on('dblclick', 'tbody input', function() {
      event.preventDefault();
      self.input_edit($(this));
    });
    // this.container.on('blur', 'tbody input', function() {
    //   event.preventDefault();
    //   self.input_save($(this));
    // });
    // drag and drop categories
    // this.categorylist.find('tbody').sortable({axis:'y', delay:150, handle:'.trend',
    //   update: function(event, ui) {
    //     self.save_category(ui.item);
    //   }
    // });
  },

  init_shortcuts: function() {
    var self = this;
    var KEYS = this.KEYS;
    // update budget items on enter
    this.container.on('keydown', 'tbody input', function(event) {
      if (event.keyCode == KEYS.ENTER) {
        event.preventDefault();
        self.input_save($(this));
        self.input_nextdown($(this));
      }
    });
  },

  data_category: function(row, sortindex) {
    return {
      id: row.data('id'),
      name: row.find('input[name=name]').val(),
      budget: pk.utils.to_float(row.find('input[name=budget]').val()),
      sortindex: row.index(),
      origname: row.data('origname'),
    };
  },

  data_transaction: function(row) {

  },

  // delete_category: function(category) {
  //   var self = this;
  //   var data = this.data_category(category);
  //   var origname = data.origname;
  //   $.confirm({
  //     backgroundDismiss: true,
  //     cancelButton: 'Cancel',
  //     columnClass: 'col-6',
  //     confirmButton: 'Delete It',
  //     content: "Are you sure you wish to delete the category '"+ origname +"?'",
  //     keyboardEnabled: true,
  //     title: 'Delete Category?',
  //     confirm: function() {
  //       var url = self.API_CATEGORIES + data.id + '/';
  //       self.request('DELETE', url, {}, function(data) {
  //         self.notify('Deleted category '+ origname +'.');
  //         self.update_categories();
  //       });
  //     }
  //   });
  // },

  input_display: function(input, value) {
      input.attr('readonly', true);
      switch(input.data('display')) {
        case 'int': input.val(pk.utils.to_amount_int(value)); break;
        case 'float': input.val(pk.utils.to_amount_float(value)); break;
        default: input.val(value); break;
      }
  },

  input_edit: function(input) {
    input.attr('readonly', false);
    if (input.hasClass('int') && !input.hasClass('error')) {
      input.val(pk.utils.to_int(input.val()));
    } else if (input.hasClass('float') && !input.hasClass('error')) {
      input.val(pk.utils.to_float(input.val()));
    }
    setTimeout(function() {
      var len = input.val().length * 2;
      input.get(0).setSelectionRange(len, len)
    }, 10);
  },

  input_save: function(input) {
    var self = this;
    input.addClass('saving');
    input.removeClass('error');
    var row = input.parents('tr');
    var type = row.data('type');
    switch(type) {
      case 'category':
        var url = this.API_CATEGORIES;
        var data = this.data_category(row);
        break;
      case 'transaction':
        var url = this.API_TRANSACTIONS;
        var data = this.data_transaction(row);
        break;
    }
    var method = data.id ? 'PUT' : 'POST';
    url += data.id ? data.id+'/' : '';
    var xhr = $.ajax({url:url, type:method, data:data, dataType:'json'});
    xhr.always(function() {
      setTimeout(function() { input.removeClass('saving'); }, 500);
    });
    xhr.done(function(data, textStatus, jqXHR) {
      self.input_display(input, data[input.attr('name')]);
    });
    xhr.fail(function(jqXHR, textStatus, errorThrown) {
      input.removeClass('error');
    });
  },

  // request: function(method, url, data, callback) {
  //   var self = this;
  //   var xhr = $.ajax({url:url, type:method, data:data, dataType:'json'});
  //   xhr.done(function(data, textStatus, jqXHR) { callback(data, textStatus, jqXHR); });
  //   xhr.done(function(data, textStatus, jqXHR) { callback(data, textStatus, jqXHR); });
  // },

  // save_category: function(category, input) {
  //   var self = this;
  //   var data = self.data_category(category);
  //   if (!data.name) { return self.delete_category(category); }
  //   var method = data.id ? 'PUT' : 'POST';
  //   var url = data.id ? this.API_CATEGORIES + data.id + '/' : this.API_CATEGORIES;
  //   url = sortindex === undefined ? url : url +'sortindex/';
  //   this.request(method, url, data, function(data) {
  //     self.categorylist.find('tfoot input').val('');
  //     self.update_categories();
  //     if (method == 'POST') {
  //       self.categorylist.find('tfoot .name input').focus();
  //     }
  //   });
  // },
 
  update_categories: function() {
    var self = this;
    if (this.xhrcat) { this.xhrcat.abort(); }
    this.xhrcat = $.ajax({url:this.API_CATEGORIES, type:'GET', dataType:'json'});
    this.xhrcat.done(function(data, textStatus, jqXHR) {
      var ctx = {categories:data.results};
      var html = self.templates.listcategories(ctx);
      self.categorylist.find('tbody').html(html);
    });
  },

  update_transactions: function(search) {
    var self = this;
    //if (search == this.search) { return; }
    if (this.xhrtrx) { this.xhrtrx.abort(); }
    var url = search ? this.API_TRANSACTIONS +'?search='+ encodeURIComponent(search) : this.API_TRANSACTIONS;
    this.xhrtrx = $.ajax({url:url, type:'GET', dataType:'json'});
    this.xhrtrx.done(function(data, textStatus, jqXHR) {
      var ctx = {items:data.results};
      var html = self.templates.listtransactions(ctx);
      self.maincontent.find('tbody').html(html);
    });
  },

  templates: {
    listcategories: Handlebars.compile([
      '{{#each this.categories}}',
      '  <tr data-id="{{this.id}}" data-type="category" data-origname="{{this.name}}">',
      '    <td class="name"><input name="name" type="text" value="{{this.name}}" autocomplete="off" readonly="readonly"></td>',
      '    <td class="trend">&nbsp;</td>',
      '    <td class="budget right"><input name="budget" data-display="int" type="text" value="{{amountInt this.budget}}" autocomplete="off" readonly="readonly"></td>',
      '  </tr>',
      '{{/each}}',
    ].join('\n')),

    listtransactions: Handlebars.compile([
      '{{#each this.items}}',
      '  <tr id="{{this.id}}" data-type="transaction" data-bankid="{{this.bankid}}">',
      '    <td class="account">{{this.account}}</td>',
      '    <td class="date"><input name="date" type="text" value="{{this.date}}" autocomplete="off" readonly="readonly"></td>',
      '    <td class="payee"><input name="payee" type="text" value="{{this.payee}}" autocomplete="off" readonly="readonly"></td>',
      '    <td class="category"><input name="name" type="text" value="{{this.category.name}}" autocomplete="off" readonly="readonly"></td>',
      '    <td class="amount right"><input name="budget" data-display="float" type="text" value="{{amountFloat this.amount}}" autocomplete="off" readonly="readonly"></td>',
      '    <td class="approved center"><input name="approved" type="text" value="x" autocomplete="off" readonly="readonly"></td>',
      '    <td class="comment"><input name="comment" type="text" value="{{this.comment}}" autocomplete="off" readonly="readonly"></td>',
      '  </tr>',
      '{{/each}}',
    ].join('\n')),
  },

};
