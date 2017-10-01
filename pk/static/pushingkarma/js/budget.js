/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

pk.budget = {
  BUDGET_SELECTOR: '#budget',
  LOADMORE_INTERVAL: 100,
  LOADMORE_DISTANCE: 200,
  KEYS: {TAB:9, ENTER:13, ESC:27, UP:38, DOWN:40},
  
  init: function(selector) {
    this.container = $(selector);
    if (!this.container.length) { return; }
    console.debug('init pk.budget on '+ selector);
    this.xhr = null;            // main actions xhr reference
    this.xhrcat = null;         // categories xhr reference
    this.xhrtrx = null;         // transactions xhr reference
    this.trxpage = null;        // Last loaded trx page
    this.search = null;         // current search string
    this.init_elements();
    this.init_triggers();
    this.init_shortcuts();
    this.update_categories();
    this.update_transactions();
  },

  init_elements: function() {
    this.sidepanel = this.container.find('#sidepanel');
    this.searchinput = this.container.find('#search');
    this.transactionsbtn = this.container.find('#search-action');
    this.categorylist = this.container.find('#sidepanel-content');
    this.maincontent = this.container.find('#maincontent');
  },

  init_triggers: function() {
    var self = this;
    var KEYS = this.KEYS;
    // update transactions when search input changes
    this.searchinput.on('change paste keyup', function(event) {
      event.preventDefault();
      self.update_transactions();
    });
    // edit category or transaction on dblclick
    this.container.on('dblclick', 'tbody td > div', function(event) {
      event.preventDefault();
      self.td_edit($(this).closest('td'));
    });
    // save category or transaction on blur
    this.container.on('blur', 'tbody td > input', function(event) {
      event.preventDefault();
      var input = $(this);
      var td = input.closest('td');
      if (input.hasClass('nosave')) { return; }
      if (td.hasClass('delempty') && !input.val()) {
        self.td_delete(td);
      } else {
        self.td_save(td);
      }
    });
    // prevent selectall on dblclick
    this.container.on('mousedown', 'td > div', function(event) {
      event.preventDefault();
    });
    // create category when pressing enter on footer inputs
    this.categorylist.on('keydown', 'tfoot input', function(event) {
      if (event.keyCode == KEYS.ENTER) {
        var td = $(this).closest('td');
        var row = td.closest('tr');
        self.td_save(td);
        row.find('input').val('').first().focus();
      }
    });
    // drag and drop categories
    this.categorylist.find('tbody').sortable({
      axis:'y', delay:150, handle:'[data-name=trend]',
      update: function(event, ui) {
        console.log(ui.item.find('td').first());
        self.td_save(ui.item.find('td').first(), true);
      }
    });
    // load more transactions if user scrolls near bottom
    setInterval(function() {
       var bottom = $(document).height() - $(window).scrollTop() - $(window).height();
       if (bottom < self.LOADMORE_DISTANCE && self.maincontent.find('#transactions-more').length) {
          self.update_transactions(true);
       }
    }, self.LOADMORE_INTERVAL);
  },

  init_shortcuts: function() {
    var self = this;
    var KEYS = this.KEYS;
    // update budget items on enter
    this.container.on('keydown', 'tbody input', function(event) {
      var input = $(this);
      var watchedkey = _.valuesIn(KEYS).indexOf(event.keyCode) >= 0;
      if (watchedkey) {
        var td = input.closest('td');
        // enter and down select td on next row
        if (event.keyCode == KEYS.ENTER || event.keyCode == KEYS.DOWN) {
          event.preventDefault();
          var row = td.closest('tr');
          var name = td.data('name');
          var next = row.next().find('td[data-name='+name+']');
          next.length ? self.td_edit(next) : input.blur();
        // up selects input on prev row
        } else if (event.keyCode == KEYS.UP) {
          event.preventDefault();
          var row = td.closest('tr');
          var name = td.data('name');
          var next = row.prev().find('td[data-name='+name+']');
          next.length ? self.td_edit(next) : input.blur();
        // shift + tab selects previous input in full table
        } else if (event.shiftKey && event.keyCode == KEYS.TAB) {
          event.preventDefault();
          var all = td.closest('tbody').find('td:not(.readonly)');
          var index = all.index(td) - 1;
          var next = index >= 0 ? all.eq(index) : null;
          next.length ? self.td_edit(next) : input.blur();
        // tab selects next input in full table
        } else if (event.keyCode == KEYS.TAB) {
          event.preventDefault();
          var all = td.closest('tbody').find('td:not(.readonly)');
          var index = all.index(td) + 1
          var next = all.eq(index);
          next.length ? self.td_edit(next) : input.blur();
        // esc reverts back to init value and stops editing
        } else if (event.keyCode == KEYS.ESC) {
          event.preventDefault();
          input.addClass('nosave');
          return self.td_display(td, td.data('init'));
        }
      }
    });
  },

  data_category: function(row) {
    var data = {
      id: row.attr('id').replace('category-', ''),
      name: this.text_or_val(row.find('[data-name=name]')),
      budget: this.text_or_val(row.find('[data-name=budget]')),
      sortindex: row.attr('id') == 'category-add' ? null : row.index(),
    };
    data.id = data.id == 'add' ? null : data.id;
    return data;
  },

  data_transaction: function(row) {
    return {
      id: row.attr('id').replace('transaction-'),
      bankid: row.data('bankid'),
      account: this.text_or_val(row.find('[data-name=account]')),
      date: this.text_or_val(row.find('[data-name=date]')),
      payee: this.text_or_val(row.find('[data-name=payee]')),
      category: this.text_or_val(row.find('[data-name=category]')),
      amount: this.text_or_val(row.find('[data-name=amount]')),
      approved: this.text_or_val(row.find('[data-name=approved]')) == 'x',
      comment: this.text_or_val(row.find('[data-name=comment]')),
    }
  },

  text_or_val: function(td) {
    var value = null;
    var child = td.children().first();
    if (child.is('div')) {
      // Get value from a div
      var text = child.text().trim();
      switch (td.data('display')) {
        case 'int': value = pk.utils.to_int(text); break;
        case 'float': value = pk.utils.to_float(text); break;
        default: value = text; break;
      }
    } else {
      // Get value from an input
      value = child.val().trim();
      if ((value == '') && (td.data('default') !== undefined)) {
        value = td.data('default');
      }
    }
    return value;
  },

  td_delete: function(td) {
    var self = this;
    var row = td.closest('tr');
    var type = row.attr('id').split('-')[0];
    $.confirm({
      backgroundDismiss: true,
      cancelButton: 'Cancel',
      columnClass: 'col-6',
      confirmButton: 'Delete It',
      content: "Are you sure you wish to delete the "+ type +" '"+ td.data('init') +"?'",
      keyboardEnabled: true,
      title: 'Delete '+ _.startCase(type) +'?',
      confirm: function() {
        var url = row.data('url');
        self.request(td, url, 'DELETE', null, {
          done: function(data) { row.remove(); },
        });
      },
      cancel: function() {
        self.td_display(td, td.data('init'));
      }
    });
  },

  td_display: function(td, value) {
    var div = $('<div></div>');
    if (td.hasClass('error')) {
      return td.html(div.text(value));
    }
    switch (td.data('display')) {
      case 'int': div.text(pk.utils.to_amount_int(value)); break;
      case 'float': div.text(pk.utils.to_amount_float(value)); break;
      case 'bool': div.text(value ? 'x' : ''); break;
      default: div.text(value); break;
    }
    td.html(div);
  },

  td_edit: function(td) {
    if (td.hasClass('readonly')) { return; }
    // create input and format value
    var div = td.find('div');
    var input = $('<input type="text" />');
    if (td.hasClass('error')) {
      input.val(td.text());
    } else {
      switch (td.data('display')) {
        case 'int': input.val(pk.utils.to_int(div.text())); break;
        case 'float': input.val(pk.utils.to_float(div.text())); break;
        default: input.val(div.text()); break;
      }
    }
    // repalce div with input and set focus
    td.data('init', input.val()).html(input);
    input.focus();
    setTimeout(function() {
      var end = input.val().length * 2;
      var start = td.hasClass('selectall') ? 0 : end;
      input.get(0).setSelectionRange(start, end);
    }, 10);
  },

  td_save: function(td, force) {
    var self = this;
    var input = td.find('input');
    var row = td.closest('tr');
    var type = row.attr('id').split('-')[0];
    var add = row.attr('id') == 'category-add';
    // do nothing if the value is unchanged
    if (!force && td.data('init') == input.val() && !td.hasClass('error')) {
      return self.td_display(td, input.val());
    }
    // save the new value to the database
    var data = this['data_'+ type](row);
    var url = row.data('url');
    var method = data.id ? 'PUT' : 'POST';
    var xhr = self.request(td, url, method, data, {
      done: function(data, textStatus, jqXHR) {
        if (add) { return self.update_categories(); }
        self.td_display(td, data[td.data('name')]);
      },
      fail: function(jqXHR, textStatus, errorThrown) {
        if (add) { return; }
        self.td_display(td, data[td.data('name')]);
      }
    });
  },

  request: function(td, url, method, data, opts) {
    td.addClass('saving');
    var row = td.closest('tr');
    var xhr = $.ajax({url:url, type:method, data:data, dataType:'json'});
    xhr.done(function(data, textStatus, jqXHR) {
      setTimeout(function() { td.removeClass('saving'); }, 500);
      td.removeClass('error');
      row.removeData('errors');
      if (opts.done) { opts.done(data, textStatus, jqXHR); }
    });
    xhr.fail(function(jqXHR, textStatus, errorThrown) {
      td.removeClass('saving');
      td.addClass('error');
      row.data('errors', jqXHR.responseJSON);
      if (opts.fail) { opts.fail(jqXHR, textStatus, errorThrown); }
    });
    xhr.always(function() {
      if (opts.always) { opts.always(); }
    });
    return xhr;
  },
 
  update_categories: function() {
    var self = this;
    var url = '/api/categories/';
    try { this.xhrtrx.abort(); } catch(err) { }
    this.xhrcat = $.ajax({url:url, type:'GET', dataType:'json'});
    this.xhrcat.done(function(data, textStatus, jqXHR) {
      var html = self.templates.listcategories(data);
      self.categorylist.find('tbody').html(html);
    });
  },

  update_transactions: function(page) {
    var self = this;
    if (!page) {
      self.trxpage = null;
      var more = null;
      var url = '/api/transactions/';
      var search = this.searchinput.val();
      url = search ? pk.utils.update_url(url, 'search', search) : url;
    } else {
      var more = this.maincontent.find('#transactions-more');
      var url = more.data('next');
      more.addClass('on');
    }
    if (self.trxpage != url) {
      self.trxpage = url;
      try { this.xhrtrx.abort(); } catch(err) { }
      this.xhrtrx = $.ajax({url:url, type:'GET', dataType:'json'});
      this.xhrtrx.done(function(data, textStatus, jqXHR) {
        if (more) { more.remove(); }
        var html = self.templates.listtransactions(data);
        var tbody = self.maincontent.find('tbody');
        data.previous ? tbody.append(html) : tbody.html(html);
        //self.maincontent.find('tbody').append(html);
      });
    }
  },

  // data attributes that affect ttd element behavior:
  //   data-id: ID of the item being displayed.
  //   data-type: category or transaction of item being displayed.
  //   data-name: name of the model field td corresponds to.
  //   data-default: default value if left blank.
  //   data-display: int or float currency representaion.
  //   data-url: API url to use when editing item.
  //   selectall (class): Select all content when initializing edit.
  //   readonly (class): Do not allow editing this item.
  //   delempty (class): Delete category or transaction if value empty.
  templates: {
    listcategories: Handlebars.compile([
      '{{#each this.results}}',
      '  <tr id="category-{{this.id}}" data-type="category" data-url="{{this.url}}">',
      '    <td data-name="name" class="delempty"><div>{{this.name}}</div></td>',
      '    <td data-name="trend" class="readonly"><div>&nbsp;</div></td>',
      '    <td data-name="budget" data-display="int" class="right"><div>{{amountInt this.budget}}</div></td>',
      '  </tr>',
      '{{/each}}',
    ].join('\n')),

    listtransactions: Handlebars.compile([
      '{{#each this.results}}',
      '  <tr id="transaction-{{this.id}}" data-type="transaction" data-bankid="{{this.bankid}}" data-url="{{this.url}}">',
      '    <td data-name="account" class="readonly"><div>{{this.account}}</div></td>',
      '    <td data-name="date"><div>{{this.date}}</div></td>',
      '    <td data-name="payee"><div>{{this.payee}}</div></td>',
      '    <td data-name="category"><div>{{this.category.name}}</div></td>',
      '    <td data-name="amount" data-display="float" class="right"><div>{{amountFloat this.amount}}</div></td>',
      '    <td data-name="approved" data-display="bool" class="center selectall"><div>{{yesNo this.approved \'x\' \'\'}}</div></td>',
      '    <td data-name="comment"><div>{{this.comment}}</div></td>',
      '  </tr>',
      '{{/each}}',
      '{{#if this.next}}',
      '  <tr id="transactions-more" data-next="{{this.next}}">',
      '    <td colspan="100%"><span class="spinner on"></span></td>',
      '  </tr>',
      '{{/if}}',
    ].join('\n')),
  },

};
