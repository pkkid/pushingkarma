/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

pk.budget = {
  BUDGET_SELECTOR: '#budget',
  KEYS: {TAB:9, ENTER:13, ESC:27, F3:114, UP:38, DOWN:40},
  LOADMORE_INTERVAL: 100,
  LOADMORE_DISTANCE: 200,
  URL_SUMMARY: window.location.origin +'/api/transactions/summary/',
  URL_CATEGORIES: window.location.origin +'/api/categories/',
  URL_TRANSACTIONS: window.location.origin +'/api/transactions/',
  URL_UPLOAD: window.location.origin +'/api/transactions/upload/',
  
  init: function(selector) {
    this.container = $(selector);
    if (!this.container.length) { return; }
    console.debug('init pk.budget on '+ selector);
    this.xhr = null;                            // main actions xhr reference
    this.xhrcat = null;                         // categories xhr reference
    this.xhrtrx = null;                         // transactions xhr reference
    this.trxpage = null;                        // last loaded trx page
    this.clicktimer = null;                     // detects single vs dblclick
    self.autocomplete = false;                  // autocomplete select open
    this.categorynames = [];                    // category name choices
    this.params = {view:'summary', search:''};  // URL params for current view
    this.init_elements();
    this.bind_search_edit();
    this.bind_view_button();
    this.bind_row_edit();
    this.bind_category_add();
    this.bind_drag_files();
    this.bind_infinite_scroll();
    this.init_shortcuts();
    this.update_categories();
    // display summary or transactions
    var view = new URL(window.location.href).searchParams.get('view');
    view == 'transactions' ? this.update_transactions() : this.update_summary();
  },

  init_elements: function() {
    this.search = this.container.find('#search');
    this.viewbtn = this.container.find('#viewbtn');
    this.summary = this.container.find('#summary');
    this.categories = this.container.find('#categories');
    this.transactions = this.container.find('#transactions');
    this.dropzone = this.container.find('#dropzone');
  },

  bind_search_edit: function() {
    // update transactions when search input changes
    var self = this;
    this.search.on('change paste keyup', function(event) {
      event.preventDefault();
      $(this).val() ? self.update_transactions() : self.update_summary();
    });
  },

  bind_view_button: function() {
    // show or hide the transaction list
    var self = this;
    self.viewbtn.on('click', function(event) {
      if (self.params.view == 'summary') {
        self.update_transactions();
      } else {
        self.search.val('');
        self.update_summary();
      }
    });
  },

  bind_row_edit: function() {
    // handle both single and dblclick events
    var self = this;
    var selector = '#categories tbody td > div,#transactions tbody td > div';
    this.container.on('click', selector, function(event) {
      event.preventDefault();
      var td = $(this).closest('td');
      if (event.detail == 1) {
        // display popover on single click
        self.clicktimer = setTimeout(function() {
          console.log('DISPLAY POPEVER');
          //self.popover_display(td);
        }, 200);
      } else if (event.detail == 2) {
        // edit category or transaction on dblclick
        clearTimeout(self.clicktimer);
        self.td_edit(td);
      }      
    });
    // close the popover if clicking somewhere else
    $(document).on('click', function(event) {
      var trgt = $(event.target);
      if (!trgt.closest('tr').hasClass('popped') && !trgt.closest('.popover').length) {
        $('tr.popped').removeClass('popped').popover('hide');
      }
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
        self.td_save(td, false, true);
      }
    });
  },

  bind_category_add: function() {
    // create category when pressing enter on footer inputs
    var self = this;
    var KEYS = this.KEYS;
    this.categories.on('keydown', 'tfoot input', function(event) {
      if (event.keyCode == KEYS.ENTER) {
        event.preventDefault();
        console.log(event.keyCode);
        var td = $(this).closest('td');
        var row = td.closest('tr');
        self.td_save(td, false, false, function() {
          self.update_categories(function() {
            console.log(self.categories.find('#category-add input'));
            self.categories.find('#category-add input').first().focus();
          });
          self.update_summary();
        });
      }
    });
  },

  bind_drag_categories: function() {
    // drag and drop categories
    var self = this;
    this.categories.find('tbody').sortable({
      axis:'y', delay:150, handle:'.drag',
      update: function(event, ui) {
        $('#category-null').appendTo(self.categories.find('tbody'));
        if (ui.item.attr('id') != 'category-null') {
          var td = ui.item.find('td').first();
          self.td_save(td, true, true, function() {
            self.update_summary();
          });
        }
      }
    });
  },

  bind_drag_files: function() {
    // show and hide the dropzone when dragging a file
    var self = this;
    $(document).on('dragover', function(event) {
      var dt = event.originalEvent.dataTransfer;
      if (dt.types && (dt.types.indexOf ? dt.types.indexOf('Files') != -1 : dt.types.contains('Files'))) {
        event.preventDefault();
        event.stopPropagation();
        self.dropzone.fadeIn('fast');
      }
    });
    $(document).on('dragleave', function(event) {
      event.preventDefault();
      event.stopPropagation();
      if (event.originalEvent.pageX != 0 && event.originalEvent.pageY != 0) { return; }
      self.dropzone.fadeOut('fast');
    });
    // handle file drag and drop event
    $(document).on('drop', function(event) {
      event.preventDefault();
      event.stopPropagation();
      self.dropzone.fadeOut('fast');
      var formdata = new FormData();
      $.each(event.originalEvent.dataTransfer.files, function(i, file) {
        formdata.append(file.name, file);
      });
      var xhr = $.ajax({url:'/api/transactions/upload/', type:'PUT', data:formdata,
        cache:false, contentType:false, processData:false});
      xhr.done(function(data, textStatus, jqXHR) {
        console.log('SUCCESS?');
        console.log(data);
      });
      xhr.fail(function(jqXHR, textStatus, errorThrown) {
        console.log('FAILED UPLOAD');
      });
    });
  },

  bind_infinite_scroll: function() {
    // load more transactions if user scrolls near bottom
    var self = this;
    setInterval(function() {
      if (self.params.view == 'transactions') {
        var bottom = $(document).height() - $(window).scrollTop() - $(window).height();
        if (bottom < self.LOADMORE_DISTANCE && self.transactions.find('#transactions-more').length) {
          self.update_transactions(true);
        }
      }
    }, self.LOADMORE_INTERVAL);
  },

  init_shortcuts: function() {
    var self = this;
    var KEYS = this.KEYS;
    // f3 puts focus on search input
    $(document).on('keydown', function(event) {
      if (event.keyCode == KEYS.F3) {
        event.preventDefault();
        event.stopPropagation();
        self.search.focus();
      }
    });
    // update budget items on enter
    this.container.on('keydown', 'tbody input', function(event) {
      var input = $(this);
      var watchedkey = _.valuesIn(KEYS).indexOf(event.keyCode) >= 0;
      if (watchedkey) {
        var td = input.closest('td');
        // enter and down select td on next row
        if ((event.keyCode == KEYS.ENTER || event.keyCode == KEYS.DOWN) && !self.autocomplete) {
          event.preventDefault();
          var row = td.closest('tr');
          var name = td.data('name');
          var next = row.next(':not(.readonly)').find('td[data-name='+name+']');
          next.length ? self.td_edit(next) : input.blur();
        // up selects input on prev row
        } else if ((event.keyCode == KEYS.UP) && !self.autocomplete) {
          event.preventDefault();
          var row = td.closest('tr');
          var name = td.data('name');
          var next = row.prev(':not(.readonly)').find('td[data-name='+name+']');
          next.length ? self.td_edit(next) : input.blur();
        // shift + tab selects previous input in full table
        } else if (event.shiftKey && event.keyCode == KEYS.TAB) {
          event.preventDefault();
          var all = td.closest('tbody').find('td:not(.readonly)');
          var index = all.index(td) - 1;
          var next = index >= 0 ? all.eq(index) : null;
          if (!next) { return; }
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
      account: this.text_or_val(row.find('[data-name=account]')),
      accountfid: row.data('accountfid'),
      trxid: row.data('trxid'),
      date: this.text_or_val(row.find('[data-name=date]')),
      payee: this.text_or_val(row.find('[data-name=payee]')),
      category: this.text_or_val(row.find('[data-name=category]')),
      amount: this.text_or_val(row.find('[data-name=amount]')),
      approved: this.text_or_val(row.find('[data-name=approved]')) == 'x',
      comment: this.text_or_val(row.find('[data-name=comment]')),
    }
  },

  popover_display: function(td) {
    var row = td.closest('tr');
    row.popover({trigger:'manual', placement:'bottom', html:true,
      content: function() {
        var html = $('<div style="padding:5px 10px;">This is the plan!</div>');
        return html;
      },
    }).addClass('popped').popover('show');
  },

  show_summary: function() {
    var self = this;
    self.params.view = 'summary';
    self.params.search = '';
    self.viewbtn.attr('class', 'mdi mdi-format-list-bulleted');
    self.viewbtn.tooltip('hide').attr('data-original-title', 'View Transactions');
    self.transactions.fadeOut('fast', function() {
      self.summary.fadeIn('fast');
    });
    // update the url
    var url = pk.utils.update_url(null, self.params);
    window.history.replaceState(null, null, url);
  },

  show_transactions: function() {
    var self = this;
    self.params.view = 'transactions';
    self.viewbtn.attr('class', 'mdi mdi-close-circle-outline');
    self.viewbtn.tooltip('hide').attr('data-original-title', 'View Summary');
    self.summary.fadeOut('fast', function() {
      self.transactions.fadeIn('fast');
    });
    // update the url
    var url = pk.utils.update_url(null, self.params);
    window.history.replaceState(null, null, url);
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
          done: function(data) { row.remove(); self.update_summary(); },
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
    var self = this;
    if (td.hasClass('readonly')) { return; }
    if (td.closest('tr').attr('id') == 'category-null') { return; }
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
    // bind autocomplete to category inputs
    if (td.data('name') == 'category') {
      input.on('keydown', function(event) {
        var watchedkey = _.valuesIn(self.KEYS).indexOf(event.keyCode) >= 0;
        if (watchedkey) { self.autocomplete = $('.ui-autocomplete:visible').length > 0; }
      });
      input.autocomplete({
        source: self.categorynames,
        autoFocus: true,
        change: function (event, ui) { if (!ui.item) { $(event.target).val(''); }}, 
        focus: function (event, ui) { return false; }
      });
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

  td_save: function(td, force, display, callback) {
    var self = this;
    var input = td.find('input');
    var row = td.closest('tr');
    var type = row.attr('id').split('-')[0];
    display = display === undefined ? false : display;
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
        if (display) { self.td_display(td, data[td.data('name')]); }
        if (callback) { callback(); }
      },
      fail: function(jqXHR, textStatus, errorThrown) {
        if (display) { self.td_display(td, data[td.data('name')]); }
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
 
  update_categories: function(callback) {
    var self = this;
    var url = '/api/categories/';
    try { this.xhrcat.abort(); } catch(err) { }
    this.xhrcat = $.ajax({url:url, type:'GET', dataType:'json'});
    this.xhrcat.done(function(data, textStatus, jqXHR) {
      var html = self.templates.listcategories(data);
      self.categories.html(html);
      self.update_categorynames(data);
      self.bind_drag_categories();
      if (callback) { callback(); }
    });
  },

  update_categorynames: function(data) {
    var categorynames = [];
    for (var i in data.results) {
      if (data.results[i].name != 'Uncategorized') {
        categorynames.push(data.results[i].name);
      }
    }
    this.categorynames = categorynames.sort();
  },

  update_summary: function() {
    var self = this;
    self.show_summary();
    try { this.xhrtrx.abort(); } catch(err) { }
    this.xhrtrx = $.ajax({url:self.URL_SUMMARY, type:'GET', dataType:'json'});
    this.xhrtrx.done(function(data, textStatus, jqXHR) {
      var html = self.templates.summary(data);
      self.summary.html(html);
    });
  },

  update_transactions: function(page) {
    var self = this;
    self.params.search = this.search.val();
    self.show_transactions();
    if (!page) {
      self.trxpage = null;
      var more = null;
      var url = pk.utils.update_url(self.URL_TRANSACTIONS, {search:self.params.search});
    } else {
      var more = this.transactions.find('#transactions-more');
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
        if (data.previous) {
          var items = $(html).find('tbody tr');
          self.transactions.find('tbody').append(items);
        } else {
          self.transactions.html(html);
        }
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

    summary: Handlebars.compile([
      '<h2>Summary</h2>',
      '<table cellpadding="0" cellspacing="0">',
      '  <thead><tr>',
      '    <th class="average">Average</th>',
      '    {{#each this.categories.0.amounts}}',
      '      <th>{{formatDate @key "%b"}}</th>',
      '    {{/each}}',
      '  </tr></thead>',
      '  <tbody>',
      '    {{#each this.categories}}',
      '      <tr>',
      '        <td class="average"><div>{{amountInt this.average}}</div></td>',
      '        {{#each this.amounts}}',
      '          <td class="{{yesNo this \'\' \'zero\'}}"><div>',
      '            {{amountInt this}}',
      '          </div></td>',
      '        {{/each}}',
      '      </tr>',
      '    {{/each}}',
      '  </tbody>',
      '  <tfoot><tr>',
      '    <td class="average"><div>{{amountInt this.avg_total}}</div></td>',
      '    {{#each this.total}}',
      '      <td class="{{yesNo this \'\' \'zero\'}}"><div>',
      '        {{amountInt this}}',
      '      </div></td>',
      '    {{/each}}',
      '  </tr></tfoot>',
      '</table>',
    ].join('\n')),

    listcategories: Handlebars.compile([
      '<table cellpadding="0" cellspacing="0">',
      '  <thead><tr>',
      '    <th data-name="name">Category</th>',
      '    <th data-name="trend" class="center">Trend</th>',
      '    <th data-name="budget" class="right">Budget</th>',
      '  </tr></thead>',
      '  <tbody>',
      '    {{#each this.results}}',
      '      <tr id="category-{{this.id}}" data-type="category" data-url="{{this.url}}" class="{{#if_eq this.id "null"}}readonly{{/if_eq}}">',
      '        <td data-name="name" class="delempty"><div>{{this.name}}</div></td>',
      '        <td data-name="trend" class="readonly drag"><div>&nbsp;</div></td>',
      '        <td data-name="budget" data-display="int" class="right selectall"><div>{{amountInt this.budget}}</div></td>',
      '      </tr>',
      '    {{/each}}',
      '  </tbody>',
      '  <tfoot>',
      '    <tr id="category-total" data-type="category">',
      '      <td data-name="name" class="readonly"><div>Total</div></td>',
      '      <td data-name="trend" class="readonly"><div>&nbsp;</div></td>',
      '      <td data-name="budget" data-display="int" class="readonly right"><div>{{amountInt this.total}}</div></td>',
      '    </tr>',
      '    <tr id="category-add" data-add="true" data-url="/api/categories/">',
      '      <td data-name="name"><input name="name" type="text" placeholder="New Category" autocomplete="off"></td>',
      '      <td data-name="trend" class="center">&nbsp;</td>',
      '      <td data-name="budget" class="right" data-default="0"><input name="budget" type="integer" placeholder="$0" autocomplete="off"></td>',
      '    </tr>',
      '  </tfoot>',
      '</table>'
    ].join('\n')),

    listtransactions: Handlebars.compile([
      '<h2>Transactions</h2>',
      '<table cellpadding="0" cellspacing="0">',
      '  <thead><tr>',
      '    <th data-name="account">Bank</th>',
      '    <th data-name="date">Date</th>',
      '    <th data-name="payee">Payee</th>',
      '    <th data-name="category">Category</th>',
      '    <th data-name="amount" class="right">Amount</th>',
      '    <th data-name="approved" class="center">X</th>',
      '    <th data-name="comment">Comment</th>',
      '  </tr></thead>',
      '  <tbody>',
      '   {{#each this.results}}',
      '     <tr id="transaction-{{this.id}}" data-type="transaction" data-accountfid="{{this.accountfid}}" data-trxid="{{this.trxid}}" data-url="{{this.url}}">',
      '       <td data-name="account" class="readonly"><div>{{this.account}}</div></td>',
      '       <td data-name="date"><div>{{this.date}}</div></td>',
      '       <td data-name="payee" class="selectall"><div>{{this.payee}}</div></td>',
      '       <td data-name="category" class="selectall"><div>{{this.category}}</div></td>',
      '       <td data-name="amount" data-display="float" class="right"><div>{{amountFloat this.amount}}</div></td>',
      '       <td data-name="approved" data-display="bool" class="center selectall"><div>{{yesNo this.approved \'x\' \'\'}}</div></td>',
      '       <td data-name="comment"><div>{{this.comment}}</div></td>',
      '     </tr>',
      '   {{/each}}',
      '   {{#if this.next}}',
      '     <tr id="transactions-more" data-next="{{this.next}}">',
      '       <td colspan="100%"><span class="spinner on"></span></td>',
      '     </tr>',
      '   {{/if}}',
      '  </tbody>',
      '</table>',
    ].join('\n')),
  },

};
