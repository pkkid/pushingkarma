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
    this.xhr = null;          // Main actions xhr reference
    this.xhrcat = null;       // Categories xhr reference
    this.xhrtrx = null;       // Transactions xhr reference
    this.search = null;
    this.init_elements();
    this.init_triggers();
    this.init_shortcuts();
    this.update_categories();
    this.update_transactions();
  },

  init_elements: function() {
    this.spinner = $('#budget-notify .spinner');
    this.message = $('#budget-notify .message');
    this.sidepanel = this.container.find('.sidepanel');
    this.searchinput = this.container.find('.search');
    this.transactionsbtn = this.container.find('.search-action');
    this.categorylist = this.container.find('.sidepanel-content');
    this.maincontent = this.container.find('.maincontent');
  },

  init_triggers: function() {
    var self = this;
    // Edit category budget
    this.categorylist.on('focus', 'tbody input', function() {
      event.preventDefault();
      self.input_edit($(this));
    });
    this.categorylist.on('blur', 'tbody input', function() {
      event.preventDefault();
      self.input_display($(this));
    });
    this.categorylist.find('tbody').sortable({axis:'y', delay:150, handle:'.trend',
      update: function(event, ui) {
        self.save_category(ui.item, ui.item.index());
      }
    });
  },

  init_shortcuts: function() {
    var self = this;
    var KEYS = this.KEYS;
    // Update budget items on enter
    this.categorylist.on('keydown', 'tbody input,tfoot input', function(event) {
      if (event.keyCode == KEYS.ENTER) {
        self.save_category($(this).parents('.category'));
      }
    });
  },

  add_category: function(elem) {
    console.log('add_category');
  },

  category_data: function(category, sortindex) {
    return {
      id: category.data('id'),
      name: category.find('input[name=name]').val(),
      budget: pk.utils.to_float(category.find('input[name=budget]').val()),
      sortindex: sortindex === undefined ? null : sortindex,
      origname: category.data('origname'),
    };
  },

  delete_category: function(category) {
    var self = this;
    var data = this.category_data(category);
    var origname = data.origname;
    $.confirm({
      backgroundDismiss: true,
      cancelButton: 'Cancel',
      columnClass: 'col-md-6 col-md-offset-3',
      confirmButton: 'Delete It',
      content: "Are you sure you wish to delete the category '"+ origname +"?'",
      keyboardEnabled: true,
      title: 'Delete Category?',
      confirm: function() {
        var url = self.API_CATEGORIES + data.id + '/';
        self.request('DELETE', url, {}, function(data) {
          self.notify('Deleted category '+ origname +'.');
          self.update_categories();
        });
      }
    });
  },

  input_edit: function(input) {
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

  input_display: function(input) {
    if (input.hasClass('int') && pk.utils.is_int(input.val())) {
      input.removeClass('error');
      return input.val(pk.utils.to_amount_int(input.val()));
    } else if (input.hasClass('float') && pk.utils.is_float(input.val())) {
      input.removeClass('error');
      return input.val(pk.utils.to_amount_float(input.val()));
    } else if (input.hasClass('text')) {
      return input.removeClass('error');
    }
    input.addClass('error');
  },

  notify: function(msg) {
    var self = this;
    this.message.html(msg).css('opacity', 1);
    setTimeout(function() { self.message.css('opacity', 0); }, 5000);
  },

  request: function(method, url, data, callback) {
    var self = this;
    this.spinner.addClass('on');
    var xhr = $.ajax({url:url, type:method, data:data, dataType:'json'});
    xhr.done(function(data, textStatus, jqXHR) { callback(data, textStatus, jqXHR); });
    xhr.fail(function(jqXHR, textStatus, errorThrown) { self.notify(self.MESSAGE_ERROR); });
    xhr.always(function() { self.spinner.removeClass('on'); });
  },

  save_category: function(category, sortindex) {
    var self = this;
    var data = self.category_data(category, sortindex);
    if (!data.name) { return self.delete_category(category); }
    var method = data.id ? 'PUT' : 'POST';
    var url = data.id ? this.API_CATEGORIES + data.id + '/' : this.API_CATEGORIES;
    url = sortindex === undefined ? url : url +'sortindex/';
    this.request(method, url, data, function(data) {
      self.notify('Saved category '+ data.name +'.');
      self.categorylist.find('tfoot input').val('');
      self.update_categories();
      if (method == 'POST') {
        self.categorylist.find('tfoot .name input').focus(); }
    });
  },
 
  update_categories: function() {
    var self = this;
    if (this.xhrcat) { this.xhrcat.abort(); }
    this.xhrcat = $.ajax({url:this.API_CATEGORIES, type:'GET', dataType:'json'});
    this.xhrcat.done(function(data, textStatus, jqXHR) {
      var ctx = {items:data};
      var html = self.templates.listcategories(ctx);
      self.categorylist.find('tbody').html(html);
    });
  },

  update_transactions: function() {
    var self = this;
    if (this.xhrtrx) { this.xhrtrx.abort(); }
    this.xhrtrx = $.ajax({url:this.API_TRANSACTIONS, type:'GET', dataType:'json'});
    this.xhrtrx.done(function(data, textStatus, jqXHR) {
      var ctx = {items:data};
      var html = self.templates.listtransactions(ctx);
      self.maincontent.find('tbody').html(html);
    });
  },

  templates: {
    listcategories: Handlebars.compile([
      '{{#each this.items}}',
      '  <tr class="category" data-id="{{this.id}}" data-origname="{{this.name}}">',
      '    <td class="name"><input name="name" class="text" type="text" value="{{this.name}}" autocomplete="off"></td>',
      '    <td class="trend">&nbsp;</td>',
      '    <td class="budget right"><input name="budget" class="int" type="text" value="{{amountInt this.budget}}" autocomplete="off"></td>',
      '  </tr>',
      '{{/each}}',
    ].join('\n')),

    listtransactions: Handlebars.compile([
      '{{#each this.items}}',
      '  <tr class="transaction" data-id="{{this.id}}" data-bankid="{{this.bankid}}">',
      '    <td class="account">{{this.account}}</td>',
      '    <td class="date"><input name="date" type="text" value="{{this.date}}" autocomplete="off"></td>',
      '    <td class="payee"><input name="payee" type="text" value="{{this.payee}}" autocomplete="off"></td>',
      '    <td class="category"><input name="name" type="text" value="{{this.category.name}}" autocomplete="off"></td>',
      '    <td class="amount right"><input name="budget" type="text" value="{{amountFloat this.amount}}" autocomplete="off"></td>',
      '    <td class="approved center"><input name="approved" type="text" value="x" autocomplete="off"></td>',
      '    <td class="comment"><input name="comment" type="text" value="{{this.comment}}" autocomplete="off"></td>',
      '  </tr>',
      '{{/each}}',
    ].join('\n')),
  },

};
