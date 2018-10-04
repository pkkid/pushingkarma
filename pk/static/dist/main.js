// Encoding: UTF-8
'use strict';

// pk namespace and constants
var pk = {  // jshint ignore:line
  ANIMATIONEND: 'webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend',
};

$(function() {
  // Handlebars templates
  pk.templates = [];
  $.each($('script[type="text/x-handlebars-template"]'), function() {
    var id = this.getAttribute('id');
    pk.templates[id] = Handlebars.compile(this.innerText);
    if ($(this).hasClass('partial')) {
      Handlebars.registerPartial(id, pk.templates[id]);
    }
  });

  // Core website functions
  pk.utils.enable_animations();
  pk.utils.copycode();
  pk.utils.highlightjs();
  pk.utils.init_tooltips();
  pk.login.init();
  pk.magnets.init('#magnets');
});



// Encoding: UTF-8
'use strict';

pk.budget = {
  BUDGET_SELECTOR: '#budget',
  ROW:'.pkrow', EDIT:'.pkedit',
  KEYS: {TAB:9, ENTER:13, ESC:27, F3:114, UP:38, DOWN:40},
  LOADMORE_INTERVAL: 200, LOADMORE_DISTANCE: 200,
  URL_ACCOUNTS: window.location.origin +'/api/accounts',
  URL_CATEGORIES: window.location.origin +'/api/categories/summary',
  URL_TRANSACTIONS: window.location.origin +'/api/transactions',
  URL_UPLOAD: window.location.origin +'/api/transactions/upload',
  
  init: function(selector, opts) {
    this.container = $(selector);
    if (!this.container.length) { return; }
    var _params = new URL(window.location.href).searchParams;
    console.debug('init pk.budget on '+ selector);
    this.xhr = null;                               // main actions xhr reference
    this.xhract = null;                            // accounts xhr reference
    this.xhrcat = null;                            // categories xhr reference
    this.xhrtrx = null;                            // transactions xhr reference
    this.trxpage = null;                           // last loaded trx page
    this.clicktimer = null;                        // detects single vs dblclick
    this.category_choices = [];                    // category name choices
    this.summary_data = null;                      // summary data response
    this.params = {                                // URL params for current view
      panel:_params.get('panel') || 'categories',  // * Sidepanel: categories, accounts
      view:_params.get('view') || 'summary',       // * Main View: summary, transactions
      search:_params.get('search',''),             // * Search: current search string
      demo:_params.get('demo','')};                // * DemoMode: true, false
    this.init_elements();                          // cache top level elements
    this.init_keyboard_shortcuts();                // bind keyboard shortcuts
    this.bind_search_edit();                       // update transactions on search
    this.bind_view_button();                       // show or hide the transaction list
    this.bind_row_edit();                          // handle single and dblclick events
    this.bind_save_notes();                        // Save popover notes on blur
    this.bind_category_add();                      // create new category items
    this.bind_drag_files();                        // show dropzone when uploading
    this.bind_row_highlight();                     // highlight rows on mouseover
    this.bind_infinite_scroll();                   // auto-load next page of transactions
    // load initial display data
    this.update_categories();
    if (this.params.panel == 'accounts') { this.update_accounts(); }
    if (this.params.view == 'summary') { this.update_summary(); }
    if (this.params.view == 'transactions') { this.update_transactions(); }
  },

  init_elements: function() {
    // cache top level elements
    this.accounts = this.container.find('#accounts');
    this.categories = this.container.find('#categories');
    this.dropzone = this.container.find('#dropzone');
    this.searchinfo = this.container.find('#searchwrap .subtext');
    this.searchinput = this.container.find('#search');
    this.sidepanel = this.container.find('#sidepanel-content');
    this.summary = this.container.find('#summary');
    this.transactions = this.container.find('#transactions');
    this.viewbtn = this.container.find('#viewbtn');
    this.panelbtn = this.container.find('#panelbtn');
  },

  init_keyboard_shortcuts: function() {
    // initialize keyboard shortcuts
    var self = this;
    var KEYS = this.KEYS;
    // f3 puts focus on search input
    $(document).on('keydown', function(event) {
      if (event.keyCode == KEYS.F3) {
        event.preventDefault();
        event.stopPropagation();
        self.searchinput.focus();
      }
    });
    // update budget items on enter
    var selector = pk.utils.format('{0} {1} input', self.ROW, self.EDIT);
    this.container.on('keydown', selector, function(event) {
      var input = $(this);
      var watchedkey = _.valuesIn(KEYS).indexOf(event.keyCode) >= 0;
      if (watchedkey) {
        var rowitem = input.closest(self.EDIT);
        // enter and down select item on next row
        if ((event.keyCode == KEYS.ENTER || event.keyCode == KEYS.DOWN) && !self.autocomplete()) {
          event.preventDefault();
          var row = rowitem.closest(self.ROW);
          var name = rowitem.data('name');
          var next = row.next(self.ROW).find(self.EDIT +'[data-name='+name+']');
          next.length ? self.item_edit(next) : input.blur();
        // up selects input on prev row
        } else if ((event.keyCode == KEYS.UP) && !self.autocomplete()) {
          event.preventDefault();
          var row = rowitem.closest(self.ROW);
          var name = rowitem.data('name');
          var next = row.prev(self.ROW).find('[data-name='+name+']');
          next.length ? self.item_edit(next) : input.blur();
        // shift + tab selects previous input in full table
        } else if (event.shiftKey && event.keyCode == KEYS.TAB) {
          event.preventDefault();
          var all = rowitem.closest('tbody').find(self.EDIT);
          var index = all.index(rowitem) - 1;
          var next = index >= 0 ? all.eq(index) : null;
          if (!next) { return; }
          next.length ? self.item_edit(next) : input.blur();
        // tab selects next input in full table
        } else if (event.keyCode == KEYS.TAB) {
          event.preventDefault();
          var all = rowitem.closest('tbody').find(self.EDIT);
          var index = all.index(rowitem) + 1;
          var next = all.eq(index);
          next.length ? self.item_edit(next) : input.blur();
        // esc reverts back to init value and stops editing
        } else if (event.keyCode == KEYS.ESC) {
          event.preventDefault();
          input.addClass('nosave');
          return self.item_display(rowitem, rowitem.data('init'));
        }
      }
    });
  },

  bind_search_edit: function() {
    // update transactions when search input changes
    var self = this;
    this.searchinput.on('input', function(event) {
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
        self.searchinput.val('');
        self.update_summary();
      }
    });
  },

  bind_row_edit: function() {
    // handle single and dblclick events
    var self = this;
    var click_selector = '#budget tbody td';
    $(document).on('click', function(event) {
      var target = $(event.target);
      var td = target.closest('#budget tbody td');
      if (event.detail == 1) {
        self.clicktimer = setTimeout(function() {
          // hide or display popover on single click
          if (td.find('input').length) { return null; }
          var row = target.closest('#budget .pkrow');
          var pop = target.closest('.popover');
          var popped = $('.popped').length >= 1;
          if (popped && !pop.length) {
            event.preventDefault();
            $('.popped').removeClass('popped').popover('hide');
          } else if (td.closest('#categories').length) {
            event.preventDefault();
            var item = td.closest(self.ROW);
            self.popover_display(item, 'category_popover');
          } else if (td.closest('#summary').length) {
            event.preventDefault();
            self.popover_display(td, 'summary_popover');
          }
        }, 200);
      } else if (event.detail == 2) {
        // edit category or transaction on dblclick
        clearTimeout(self.clicktimer);
        $('.popped').removeClass('popped').popover('hide');
        if (td.hasClass(self.EDIT.replace('.',''))) {
          self.item_edit(td);
        }
      }    
    });
    // save category or transaction on blur
    var blur_selector = pk.utils.format('{0} {1} > input', self.ROW, self.EDIT);
    this.container.on('blur', blur_selector, function(event) {
      event.preventDefault();
      var input = $(this);
      var item = input.closest(self.EDIT);
      if (input.hasClass('nosave')) { return; }
      if (item.hasClass('delempty') && !input.val()) {
        self.item_delete(item);
      } else {
        self.item_save(item, 'PATCH', {}, false, true);
      }
    });
  },

  bind_save_notes: function() {
    // saves notes on blur
    var self = this;
    $(document).on('focus', '.popover textarea', function(event) {
      $(this).data('init', $(this).val());
    }).on('blur', '.popover textarea', function(event) {
      if ($(this).val() != $(this).data('init')) {
        var item = $(this).closest(self.EDIT);
        self.item_save(item, 'PATCH', {}, false, false);
      }
    });
  },

  bind_category_add: function() {
    // create category when pressing enter on footer inputs
    var self = this;
    var KEYS = this.KEYS;
    this.categories.on('keydown', '#category-add input', function(event) {
      if (event.keyCode == KEYS.ENTER) {
        event.preventDefault();
        var item = $(this).closest('td');
        var row = item.closest(self.ROW);
        var data = {name:row.find('input[name=name]').val(), budget:row.find('input[name=budget]').val()}
        self.item_save(item, 'POST', data, true, false, function() {
          self.update_categories(function() {
            self.categories.find('#category-add input').first().focus();
          });
          self.update_summary();
        });
      }
    });
    // Display row when any input is in focus
    this.categories.on('focus', '#category-add input', function(event) {
      $(this).closest(self.ROW).addClass('focus');
    }).on('blur', '#category-add input', function(event) {
      $(this).closest(self.ROW).removeClass('focus');
    });
  },

  bind_drag_categories: function() {
    // drag and drop categories
    var self = this;
    this.categories.find('tbody').sortable({
      axis:'y', delay:150, handle:'.drag', items:'tr:not(:last-child)',
      update: function(event, ui) {
        $('#null').appendTo(self.categories.find('tbody'));
        if (ui.item.attr('id') != 'null') {
          var item = ui.item.find(self.EDIT).first();
          var data = {sortindex: item.closest(self.ROW).index()};
          self.item_save(item, 'PATCH', data, true, true, function() {
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
      var xhr = $.ajax({url:self.URL_UPLOAD, type:'PUT', data:formdata,
        cache:false, contentType:false, processData:false});
      xhr.done(function(data, textStatus, jqXHR) {
        var err = '<b>Error During Import</b><br/>';
        var ok = '<b>Imported '+ data.files +' QFX Files</b><br/>';
        var text = data.status.toLowerCase().indexOf('error') >= 0 ? err : ok;
        text += data.status.replace('\n', '<br/>')
        $.toast({text:text, hideAfter:10000, loader:false});
        self.update_transactions();
      });
    });
  },

  bind_row_highlight: function() {
    // highlight the current row on mouseover (this highlights both
    // the summary and category tables together).
    var self = this;
    // mouse over summary row
    self.summary.on('mouseenter', '.pklight', function(event) {
      if (self.container.find('.popped').length >= 1) { return; }
      self.categories.find('[data-id='+ $(this).data('categoryid') +']').add($(this)).addClass('hover');
    }).on('mouseleave', 'tbody tr', function(event) {
      self.categories.find('[data-id='+ $(this).data('categoryid') +']').add($(this)).removeClass('hover');
    });
    // mouse over category row
    self.categories.on('mouseenter', '.pklight', function(event) {
      if (self.container.find('.popped').length >= 1) { return; }
      self.summary.find('[data-categoryid='+ $(this).data('id') +']').add($(this)).addClass('hover');
    }).on('mouseleave', self.ROW, function(event) {
      self.summary.find('[data-categoryid='+ $(this).data('id') +']').add($(this)).removeClass('hover');
    });
    // mouse over transaction row
    self.transactions.on('mouseenter', '.pklight', function(event) {
      if (self.container.find('.popped').length >= 1) { return; }
      $(this).addClass('hover');
    }).on('mouseleave', self.ROW, function(event) {
      $(this).removeClass('hover');
    });
  },

  bind_infinite_scroll: function() {
    // auto-load next page of transactions
    var self = this;
    setInterval(function() {
      if (self.params.view == 'transactions') {
        var bottom = $(document).height() - $(window).scrollTop() - $(window).height();
        if (bottom < self.LOADMORE_DISTANCE && self.transactions.find('#loadmore').length) {
          self.update_transactions(true);
        }
      }
    }, self.LOADMORE_INTERVAL);
  },

  autocomplete: function() {
    // return true if autocomplete is visisble on the page.
    return $('.ui-autocomplete:visible').length > 0;
  },

  clean_data: function(data) {
    // clean data before sending it home to server.
    for (var name in data) {
      if (name == 'approved') { data[name] = data[name] == 'x'; }
    }
    return data;
  },

  popover_display: function(item, tmpl) {
    // display popover content.
    // check we are not already popped first
    if (item.hasClass('popped')) { return; }
    var self = this;
    var url = item.data('details');
    var xhr = $.ajax({url:url, type:'GET', dataType:'json'});
    item.removeData('bs.popover');
    xhr.done(function(data, textStatus, jqXHR) {
      var content = $(pk.templates[tmpl](data));
      pk.utils.autosize_textarea($(content).find('textarea'), 4, 15);
      item.popover({trigger:'manual', placement:'bottom', html:true,
        content:content}).addClass('popped').popover('show');
    });
  },

  toggle_panel() {
    // toggle panel content between categories and accounts.
    var categories = this.params.panel == 'categories';
    categories ? this.update_accounts() : this.update_categories();
  },

  text_or_val: function(item) {
    // get value of a cell from input or div based on current edit mode.
    // Remember we replace div with input on the fly when editing content.
    var child = item.children().first();
    if (child.is('div')) {
      // get value from a div
      var value = child.text().trim();
      value = item.hasClass('int') ? pk.utils.to_int(value) : value;
      value = item.hasClass('float') ? pk.utils.to_float(value) : value;
    } else {
      // get value from an input
      value = child.val().trim();
      if ((value == '') && (item.data('default') !== undefined)) {
        value = item.data('default');
      }
    }
    return value;
  },

  item_delete: function(item) {
    // display popup making sure we want to delete an item; then
    // perform the requested action.
    var self = this;
    var row = item.closest(self.ROW);
    var type = row.data('type');
    $.confirm({
      backgroundDismiss: true,
      cancelButton: 'Cancel',
      columnClass: 'col-6',
      confirmButton: 'Delete It',
      content: "Are you sure you wish to delete the "+ type +" '"+ item.data('init') +"?'",
      keyboardEnabled: true,
      title: 'Delete '+ _.startCase(type) +'?',
      confirm: function() {
        var url = row.data('url');
        self.request(item, url, 'DELETE', null, {
          done: function(data) { row.remove(); self.update_summary(); },
        });
      },
      cancel: function() {
        self.item_display(item, item.data('init'));
      }
    });
  },

  item_display: function(item, value) {
    // update table cell for display.
    var div = $('<div></div>');
    value = value === null ? '' : value.name || value;
    if (item.hasClass('error')) {
      return item.html(div.text(value));
    }
    value = item.hasClass('int') ? pk.utils.to_amount_int(value) : value;
    value = item.hasClass('float') ? pk.utils.to_amount_float(value) : value;
    value = item.hasClass('bool') ? (value ? 'x' : '') : value;
    item.html(div.text(value));
  },

  item_edit: function(item) {
    // update table cell for editing.
    var self = this;
    var row = item.closest(self.ROW);
    if (item.hasClass('readonly')) { return; }
    if (!row.data('url')) { return; }
    // create input and format value
    var div = item.find('div');
    var input = $('<input type="text" />');
    if (item.hasClass('error')) {
      input.val(item.text());
    } else {
      var value = div.text();
      value = item.hasClass('int') ? pk.utils.to_int(value) : value;
      value = item.hasClass('float') ? pk.utils.to_float(value) : value;
      input.val(value);
    }
    // bind autocomplete to category inputs
    if (item.data('name') == 'category') {
      input.autocomplete({
        autoFocus: true,
        delay: 100,
        source: self.category_choices,
        change: function (event, ui) { if (!ui.item) { $(event.target).val(''); }}, 
        focus: function (event, ui) { return false; },
      });
    }
    // repalce div with input and set focus+
    item.data('init', input.val()).html(input);
    input.focus();
    setTimeout(function() {
      var end = input.val().length * 2;
      var start = item.hasClass('selectall') ? 0 : end;
      input.get(0).setSelectionRange(start, end);
    }, 10);
  },

  item_save: function(item, method, data, force, display, callback) {
    // save the current contents of the table cell.
    data = data || {};
    force = force || false;
    display = display || false;
    var self = this;
    var input = item.find('input,textarea');
    var name = item.data('name');
    var row = item.closest(self.ROW);
    // do nothing if the value is unchanged
    if (!force && item.data('init') == input.val() && !item.hasClass('error')) {
      return self.item_display(item, input.val());
    }
    // save the new value to the database
    data[name] = input.val();
    data = self.clean_data(data);
    var url = row.data('url');
    var xhr = self.request(item, url, method, data, {
      done: function(data, textStatus, jqXHR) {
        if (display) { self.item_display(item, data[name]); }
        if (callback) { callback(); }
      },
      fail: function(jqXHR, textStatus, errorThrown) {
        if (display) { self.item_display(item, data[name]); }
      }
    });
  },

  request: function(item, url, method, data, opts) {
    // helper function to send a request to the server.
    item.addClass('saving');
    var row = item.closest(self.ROW);
    var xhr = $.ajax({url:url, type:method, data:data, dataType:'json'});
    xhr.done(function(data, textStatus, jqXHR) {
      setTimeout(function() { item.removeClass('saving'); }, 500);
      item.removeClass('error');
      row.removeData('errors');
      if (opts.done) { opts.done(data, textStatus, jqXHR); }
    });
    xhr.fail(function(jqXHR, textStatus, errorThrown) {
      item.removeClass('saving');
      item.addClass('error');
      row.data('errors', jqXHR.responseJSON);
      if (opts.fail) { opts.fail(jqXHR, textStatus, errorThrown); }
    });
    xhr.always(function() {
      if (opts.always) { opts.always(); }
    });
    return xhr;
  },

  search: function(query, append) {
    // update search input and display matching transactions
    if (append == true) {
      var searchval = this.searchinput.val();
      var exists = searchval.toLowerCase().indexOf(query.toLowerCase()) >= 0;
      query = exists ? searchval : searchval +' '+ query;
    }
    $('.popped').removeClass('popped').popover('hide');
    this.searchinput.val(query.toLowerCase());
    this.update_transactions();
  },
 
  update_accounts: function() {
    // updates and displays accounts in the side panel.
    var self = this;
    self.update_url('panel', 'accounts');
    self.panelbtn.text('View Categories');
    self.categories.fadeOut('fast', function() {
      self.accounts.fadeIn('fast');
    });
    try { this.xhract.abort(); } catch(err) { }
    this.xhract = $.ajax({url:self.URL_ACCOUNTS, type:'GET', dataType:'json'});
    this.xhract.done(function(data, textStatus, jqXHR) {
      var html = pk.templates.accounts_list(data);
      self.accounts.html(html);
    });
  },

  update_categories: function(callback) {
    // updates and displays categories in the side panel.
    var self = this;
    self.update_url('panel', 'categories');
    self.panelbtn.text('View Accounts');
    self.accounts.fadeOut('fast', function() {
      self.categories.fadeIn('fast');
    });
    try { self.xhrcat.abort(); } catch(err) { }
    self.xhrcat = $.ajax({url:self.URL_CATEGORIES, type:'GET', dataType:'json'});
    self.xhrcat.done(function(data, textStatus, jqXHR) {
      self.categories.html(pk.templates.category_list(data));
      self.update_category_trends(data);
      self.update_category_choices(data);
      self.bind_drag_categories();
      if (self.params.view == 'summary') {
        self.searchinfo.text('');
        self.summary.html(pk.templates.summary(data));
      }
      if (callback) { callback(); }
    });
  },

  update_category_trends: function(data, i) {
    // loop through each category to generate a trand column
    // chart of the last 12 months spend.
    var self = this;
    var index = 0;
    var _update_trend = function() {
      var category = data.results[index];
      var selector = self.categories.find('tbody tr[data-id='+ category.id +'] td[data-name=trend]');
      var mult = category.name == 'Income' ? 1 : -1;
      var cdata = category.summary.months.map(x => Math.max(mult * x.amount, 0));
      selector.highcharts(pk.charts.budget_trend(cdata));
      selector.find('.highcharts-container').fadeIn('fast');
      if (index < data.results.length-1) { index += 1; setTimeout(_update_trend, 0); }
    }
    setTimeout(_update_trend, 0);
  },

  update_category_choices: function(data) {
    // updates the category choices used when editing a transaction.
    var category_choices = [];
    for (var i in data.results) {
      var category = data.results[i];
      if (category.name != 'Uncategorized') {
        category_choices.push(category.name);
      }
    }
    this.category_choices = category_choices.sort();
  },

  update_summary: function() {
    // updates and displays summary overview in the main container.
    var self = this;
    self.update_url('view', 'summary');
    self.update_url('search', '');
    self.viewbtn.attr('class', 'mdi mdi-format-list-bulleted');
    self.viewbtn.tooltip('hide').attr('data-original-title', 'View Transactions');
    self.transactions.fadeOut('fast', function() {
      self.summary.fadeIn('fast');
      self.sidepanel.addClass('toedge');
    });
    self.update_categories();
  },

  update_transactions: function(page) {
    // updates and displays transactions overview in the main container.
    var self = this;
    self.update_url('view', 'transactions');
    self.update_url('search', self.searchinput.val());
    self.viewbtn.attr('class', 'mdi mdi-close-circle-outline');
    self.viewbtn.tooltip('hide').attr('data-original-title', 'View Summary');
    self.summary.fadeOut('fast', function() {
      self.transactions.fadeIn('fast');
      self.sidepanel.removeClass('toedge');
    });
    // load the initial or 'more' transactions.
    var initurl = pk.utils.update_url(self.URL_TRANSACTIONS, {search:self.params.search})
    var more = page ? this.transactions.find('#loadmore') : null;
    var url = page ? more.data('next') : initurl;
    if (self.trxpage != url) {
      self.trxpage = url;
      try { this.xhrtrx.abort(); } catch(err) { }
      this.xhrtrx = $.ajax({url:url, type:'GET', dataType:'json'});
      this.xhrtrx.done(function(data, textStatus, jqXHR) {
        if (more) { more.remove(); }
        self.searchinfo.text(data.errors || data.datefilters);
        var html = pk.templates.transaction_list(data);
        if (data.previous) {
          var items = $(html).find(self.ROW +',#loadmore');
          self.transactions.find('tbody').append(items);
        } else {
          self.transactions.html(html);
        }
      });
    }
  },

  update_url: function(key, value) {
    // update the browser URL to reflect current params
    this.params[key] = value;
    var url = pk.utils.update_url(null, this.params);
    window.history.replaceState(null, null, url);
  },

};


//-------------------------
// Handlebar Helpers
//-------------------------
pk.budget.helpers = {
  budgetFlags: function(category, month) {
    var flags = [];
    var _flags = function() { return flags.join(' '); }
    if (month.amount == 0) { flags.push('zero'); }
    if (month.amount > 10) { flags.push('income'); }
    if (category.name == 'Ignored') { flags.push('zero'); }
    if (category.budget < -10 && month.amount < 10 &&
       (month.amount <= category.budget * 1.2)) { flags.push('over'); }
    return _flags();
  },

  remaining: function(num1, num2) {
    return pk.utils.to_amount_int(num1 - num2);
  },

  budgetMath: function(budget, spent) {
    var mult = budget > 0 ? 1 : -1;
    var value = budget - spent;
    var over = budget > 0 ? value < -1 : value > 1;
    var cls = over ? 'over' : 'ok';
    return new helperutils.safeString(
        '<span class="'+cls+'">'+pk.utils.to_amount_int(value * mult)+'</span>'
      );
  },
};


for (var helper in pk.budget.helpers) {
  if (pk.budget.helpers.hasOwnProperty(helper)) {
    Handlebars.registerHelper(helper, pk.budget.helpers[helper]);
  }
}



// Encoding: UTF-8
'use strict';

pk.charts = {

  budget_trend: function(data) {
    // https://api.highcharts.com/highstock/plotOptions.column
    var chart = {};
    pk.utils.rset(chart, 'chart.backgroundColor', '#0000000a');
    pk.utils.rset(chart, 'chart.height', 18);
    pk.utils.rset(chart, 'chart.width', 53);
    pk.utils.rset(chart, 'chart.margin', [0, 2, 0, 2]);
    pk.utils.rset(chart, 'chart.spacing', 0);
    pk.utils.rset(chart, 'chart.type', 'column');
    pk.utils.rset(chart, 'credits.enabled', false);
    pk.utils.rset(chart, 'exporting.enabled', null);
    pk.utils.rset(chart, 'legend.enabled', false);
    pk.utils.rset(chart, 'plotOptions.column.animation.duration', 0);
    pk.utils.rset(chart, 'plotOptions.column.borderWidth', 0);
    pk.utils.rset(chart, 'plotOptions.column.color', '#777b');
    pk.utils.rset(chart, 'plotOptions.column.enableMouseTracking', false);
    pk.utils.rset(chart, 'plotOptions.column.minPointLength', 2);
    pk.utils.rset(chart, 'plotOptions.column.pointPadding', 0.02);
    pk.utils.rset(chart, 'plotOptions.column.pointWidth', 3);
    pk.utils.rset(chart, 'title.text', null);
    pk.utils.rset(chart, 'xAxis.labels.enabled', false);
    pk.utils.rset(chart, 'xAxis.lineWidth', 0);
    pk.utils.rset(chart, 'xAxis.tickLength', 0);
    pk.utils.rset(chart, 'yAxis.endOnTick', false);
    pk.utils.rset(chart, 'yAxis.gridLineWidth', 0);
    pk.utils.rset(chart, 'yAxis.labals.enabled', false);
    pk.utils.rset(chart, 'yAxis.title.enabled', false);
    chart.series = [{data: data}];
    // highlight max values
    // var max = Math.max(...data);
    // for (var i=0; i<data.length; i++) {
    //     if (data[i] == max) { data[i] = {y:data[i], color:'#955b'}; }
    // }
    return chart;
  },

};



// Encoding: UTF-8
'use strict';

pk.editor = {
  UPDATE_INTERVAL: 500,
  MESSAGE_SAVED: '<span style="color:rgba(40,200,40,0.9)"><i class="mdi mdi-check"></i>&nbsp;Saved</span>',
  MESSAGE_ERROR: '<span style="color:rgba(200,40,40,0.9)"><i class="mdi mdi-minus-circle-outline"></i>&nbsp;Error</span>',
  MESSAGE_DELETED: '<span style="color:rgba(40,200,40,0.9)"><i class="mdi mdi-check"></i>&nbsp;Deleted</span>',
  MIN_HEIGHT: 135,
  KEYS: {S:83, F2:113, ESC:27},
  
  init: function(selector, opts) {
    this.container = $(selector);
    if (!this.container.length) { return; }
    console.debug('init pk.editor on '+ selector);
    this.opts = $.extend(true, {}, this.defaults, opts);
    this.editor = this.init_editor();
    this.codemirror = this.init_codemirror();
    this.history = {updated:null, saved:null};
    this.init_elements();
    this.init_edit_buttons();
    this.init_triggers();
    this.init_shortcuts();
    this.init_data(this.opts.init_data);
    if (Cookies.get('editing'))
      this.toggle_editor();
  },
  
  init_elements: function() {
    this.menu = this.editor.find('.menu');
    this.spinner = this.menu.find('.spinner');
    this.message = this.menu.find('.message');
    this.title = this.editor.find('.title');
    this.tags = this.editor.find('.tags');
    this.includes = this.editor.find('.includes');
  },
  
  init_editor: function() {
    this.editor = $(pk.templates.editor(this)).appendTo('body');
    this.set_height(Cookies.get('editor-height') || 300);
    return this.editor;
  },
  
  init_codemirror: function() {
    var textarea = this.editor.find('textarea').get(0);
    return CodeMirror.fromTextArea(textarea, this.opts.codemirror);
  },
  
  init_edit_buttons: function() {
    var h2s = this.container.find('h2');
    h2s.append('<i class="toggle mdi mdi-pencil"></i>');
    h2s.wrapInner('<span></span>');
  },
  
  init_triggers: function() {
    var self = this;
    $('.CodeMirror-scroll').disableParentScroll();
    $('#editor .slider').on('mousedown', function(event) { event.preventDefault(); self.resize(event); });
    $('#editor .reset').on('click', function(event) { event.preventDefault(); self.reset(); });
    $('#editor .save').on('click', function(event) { event.preventDefault(); self.save(); });
    $('#editor .delete').on('click', function(event) { event.preventDefault(); self.delete(); });
    $('#editor .toggle').on('click', function(event) { event.preventDefault(); self.toggle_editor(); });
    this.container.on('click', '.toggle', function(event) { event.preventDefault(); self.toggle_editor(); });
    setInterval(function() { self.update(); }, this.UPDATE_INTERVAL);
  },
  
  init_shortcuts: function() {
    var self = this;
    var KEYS = this.KEYS;
    $(document).on('keydown', function(event) {
      var ctrl = navigator.platform.match('Mac') ? event.metaKey : event.ctrlKey;
      if (ctrl && event.keyCode == KEYS.S && self.editing()) {
        event.preventDefault();
        self.save();
      } else if (event.keyCode == KEYS.F2) {
        event.preventDefault();
        self.toggle_editor();
      } else if (event.keyCode == KEYS.ESC && $('.jconfirm-box-container').length === 0) {
        event.preventDefault();
        self.toggle_editor(false);
      }
    });
  },
  
  init_data: function(data) {
    this.history.saved = data;
    if (this.opts.show_title) { this.title.val(data.title); }
    this.codemirror.setValue(data.body);
    if (this.opts.show_tags) { this.tags.val(data.tags); }
  },
  
  delete: function() {
    var self = this;
    var data = this.request_data();
    var title = data.title ? data.title : data.slug;
    $.confirm({
      backgroundDismiss: true,
      cancelButton: 'Cancel',
      columnClass: 'col-6',
      confirmButton: 'Delete It',
      content: "Are you sure you wish to delete the entry '"+ title +"?'",
      keyboardEnabled: true,
      title: 'Delete Entry?',
      confirm: function() {
          var url = self.history.saved.url || self.opts.api_url;
          self.request('DELETE', url, function(data) {
            self.history.saved = {};
            self.codemirror.setValue('');
            self.title.val('');
            self.tags.val('');
            self.notify(self.MESSAGE_DELETED);
          });
      }
    });
  },
  
  editing: function() {
    return this.editor.is(':visible');
  },
  
  notify: function(msg) {
    var self = this;
    this.message.html(msg).css('opacity', 1);
    setTimeout(function() { self.message.css('opacity', 0); }, 5000);
  },
  
  request_data: function() {
    return {
      'id': this.history.saved.id,
      'slug': this.history.saved.slug,
      'title': this.title.val(),
      'body': this.codemirror.getValue(),
      'tags': this.tags.val(),
    };
  },
  
  request: function(method, url, callback) {
    var self = this;
    this.spinner.addClass('on');
    var data = this.request_data();
    var xhr = $.ajax({url:url, type:method, data:data, dataType:'json'});
    xhr.done(function(data, textStatus, jqXHR) { callback(data, textStatus, jqXHR); });
    xhr.fail(function(jqXHR, textStatus, errorThrown) { self.notify(self.MESSAGE_ERROR); });
    xhr.always(function() { self.spinner.removeClass('on'); });
  },
  
  reset: function() {
    this.codemirror.setValue(this.history.saved.body);
    this.title.val(this.history.saved.title);
    this.tags.val(this.history.saved.tags);
  },
  
  resize: function(event) {
    var self = this;
    var window_height = $(window).height();
    var drag = function(event) {
      event.preventDefault();
      self.set_height(window_height - event.clientY + 6);
      self.codemirror.refresh();
    };
    var stopdrag = function(event) {
      event.preventDefault();
      $(document).unbind('mousemove', drag);
      $(document).unbind('mouseup', stopdrag);
    };
    $(document).bind('mousemove', drag);
    $(document).bind('mouseup', stopdrag);
  },
  
  save: function() {
    var self = this;
    var method = this.history.saved.id ? 'PUT' : 'POST';
    var url = this.history.saved.url || this.opts.api_url;
    this.request(method, url, function(data) {
      self.history.saved = data;
      window.history.replaceState('', '', data.weburl);
      self.notify(self.MESSAGE_SAVED);
    });
  },
  
  set_height: function(height) {
    var max_height = $(window).height() - 200;
    height = Math.max(this.MIN_HEIGHT, Math.min(max_height, height));
    this.editor.height(height);
    Cookies.set('editor-height', height, {expires:14});
    if (this.editing()) {
      // resize codemirror
      var cmheight = height - 38;  // slider and menu
      if (this.opts.show_title) { cmheight -= 31; }
      if (this.opts.show_includes) { cmheight -= 35; }
      if (this.opts.show_tags) { cmheight -= 35; }
      $(this.codemirror.getWrapperElement()).height(cmheight);
      // set the body margin
      $('body').css('margin-bottom', height);
    }
  },
  
  set_includes: function(includes) {
    if (!this.opts.show_includes) { return; }
    var html = [];
    if (includes && includes.length) {
      $.each(includes, function(i, slug) {
        html.push(pk.utils.format('<a href="/p/{0}" target="{0}">{0}</a>', slug));
      });
    }
    html = html.length ? 'Includes: '+ html.join(', ') : '';
    this.includes.html(html);
  },
  
  toggle_editor: function(enable) {
    var self = this;
    enable = enable !== undefined ? enable : !this.editing();
    if (enable && !self.editing()) {
      // show the editor and set the body margin. We set the body margin early
      // so the body scrollbar displays before the animation starts.
      this.editor.show();
      $('body').css('margin-bottom', self.editor.height());
      this.editor.animatecss('bounceInUp', function() {
        self.set_height(self.editor.height());
        self.codemirror.refresh();
        self.codemirror.focus();
        Cookies.set('editing', '1', {expires:0.042});
      });
    } else if (!enable && self.editing()) {
      this.editor.animatecss('bounceOutDown', function() {
        self.editor.hide();
        $('body').css('margin-bottom', 0);
        Cookies.remove('editing');
      });
    }
  },
  
  update: function() {
    var self = this;
    var data = this.request_data();
    if (!this.editing() || _.isEqual(data, this.history.updated))
      return null;
    this.history.updated = data;
    this.request('POST', this.opts.markdown_url, function(data) {
        self.container.html(data.html);
        self.set_includes(data.includes);
        pk.utils.highlightjs();
        self.init_edit_buttons();
    });
  },

  defaults: {
    api_url: null,              // (required) url to save entry
    markdown_url: null,         // (required) url to convert markdown to html
    show_title: false,          // show the title input
    show_includes: false,       // show the includes footer
    show_tags: false,           // show the tags footer
    codemirror: {               // default codemirror opts
      extraKeys: {'Enter': 'newlineAndIndentContinueMarkdownList'},
      htmlMode: true,
      keyMap: 'sublime',
      lineNumbers: false,
      lineWrapping: false,
      matchBrackets: true,
      mode: 'gfm',
      scrollbarStyle: 'simple',
      smartIndent: false,
      tabSize: 2,
      theme: 'blackboard',
    },
  },

};



// Encoding: UTF-8
// Collection of handlebar helpers from the following git
// repo formatted for use on the web.
// SOURCE: https://github.com/assemble/handlebars-helpers
// LICENSE: https://github.com/assemble/handlebars-helpers/blob/master/LICENSE-MIT
'use strict';


// -----------------------------
// General Utils
// https://github.com/assemble/handlebars-helpers/blob/master/lib/utils/utils.js
// https://github.com/assemble/handlebars-helpers/blob/master/lib/utils/dates.js
// -----------------------------
var helperutils = {
  date_formats: /%(a|A|b|B|c|C|d|D|e|F|h|H|I|j|k|l|L|m|M|n|p|P|r|R|s|S|t|T|u|U|v|V|W|w|x|X|y|Y|z)/g,
  dates_abbreviatedWeekdays: ['Sun', 'Mon', 'Tue', 'Wed', 'Thur', 'Fri', 'Sat'],
  dates_fullWeekdays: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
  dates_abbreviatedMonths: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
  dates_fullMonths: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
  
  isFunction: function(obj) {
    return typeof obj === 'function';
  },
   
  isUndefined: function(value) {
    return typeof value === 'undefined' || this.toString.call(value) === '[object Function]' || (value.hash !== null);
  },
  
  result: function(value) {
    return this.isFunction(value) ? value() : value;
  },
  
  safeString: function(str) {
    return new Handlebars.SafeString(str);
  },
  
  toString: function(val) {
    return val === null ? '' : val.toString();
  },
  
  padNumber: function(num, count, padCharacter) {
    if (typeof padCharacter === 'undefined') {
      padCharacter = '0';
    }
    var lenDiff = count - String(num).length;
    var padding = '';
    if (lenDiff > 0) {
      while (lenDiff--) {
        padding += padCharacter;
      }
    }
    return padding + num;
  },

  dayOfYear: function(date) {
    var oneJan = new Date(date.getFullYear(), 0, 1);
    return Math.ceil((date - oneJan) / 86400000);
  },

  weekOfYear: function(date) {
    var oneJan = new Date(date.getFullYear(), 0, 1);
    return Math.ceil((((date - oneJan) / 86400000) + oneJan.getDay() + 1) / 7);
  },

  isoWeekOfYear: function(date) {
    var target = new Date(date.valueOf());
    var dayNr = (date.getDay() + 6) % 7;
    target.setDate(target.getDate() - dayNr + 3);
    var jan4 = new Date(target.getFullYear(), 0, 4);
    var dayDiff = (target - jan4) / 86400000;
    return 1 + Math.ceil(dayDiff / 7);
  },

  tweleveHour: function(date) {
    return date.getHours() > 12 ? date.getHours() - 12 : date.getHours();
  },

  timeZoneOffset: function(date) {
    var hoursDiff = -date.getTimezoneOffset() / 60;
    var result = this.padNumber(Math.abs(hoursDiff), 4);
    return (hoursDiff > 0 ? '+' : '-') + result;
  },

  format: function(date, format) {
    var self = this;
    var match = null;
    return format.replace(this.date_formats, function(m, p) {
      switch (p) {
        case 'a': return self.dates_abbreviatedWeekdays[date.getDay()];
        case 'A': return self.dates_fullWeekdays[date.getDay()];
        case 'b': return self.dates_abbreviatedMonths[date.getMonth()];
        case 'B': return self.dates_fullMonths[date.getMonth()];
        case 'c': return date.toLocaleString();
        case 'C': return Math.round(date.getFullYear() / 100);
        case 'd': return self.padNumber(date.getDate(), 2);
        case 'D': return self.format(date, '%m/%d/%y');
        case 'e': return self.padNumber(date.getDate(), 2, ' ');
        case 'F': return self.format(date, '%Y-%m-%d');
        case 'h': return self.format(date, '%b');
        case 'H': return self.padNumber(date.getHours(), 2);
        case 'I': return self.padNumber(self.tweleveHour(date), 2);
        case 'j': return self.padNumber(self.dayOfYear(date), 3);
        case 'k': return self.padNumber(date.getHours(), 2, ' ');
        case 'l': return self.padNumber(self.tweleveHour(date), 2, ' ');
        case 'L': return self.padNumber(date.getMilliseconds(), 3);
        case 'm': return self.padNumber(date.getMonth() + 1, 2);
        case 'M': return self.padNumber(date.getMinutes(), 2);
        case 'n': return '\n';
        case 'p': return date.getHours() > 11 ? 'PM' : 'AM';
        case 'P': return self.format(date, '%p').toLowerCase();
        case 'r': return self.format(date, '%I:%M:%S %p');
        case 'R': return self.format(date, '%H:%M');
        case 's': return date.getTime() / 1000;
        case 'S': return self.padNumber(date.getSeconds(), 2);
        case 't': return '\t';
        case 'T': return self.format(date, '%H:%M:%S');
        case 'u': return date.getDay() === 0 ? 7 : date.getDay();
        case 'U': return self.padNumber(self.weekOfYear(date), 2);
        case 'v': return self.format(date, '%e-%b-%Y');
        case 'V': return self.padNumber(self.isoWeekOfYear(date), 2);
        case 'W': return self.padNumber(self.weekOfYear(date), 2);
        case 'w': return self.padNumber(date.getDay(), 2);
        case 'x': return date.toLocaleDateString();
        case 'X': return date.toLocaleTimeString();
        case 'y': return String(date.getFullYear()).substring(2);
        case 'Y': return date.getFullYear();
        case 'z': return self.timeZoneOffset(date);
        default: return match;
      }
    });
  },
};


// -----------------------------
// Collection Helpers
// https://github.com/assemble/handlebars-helpers/blob/master/lib/helpers/helpers-collections.js
// -----------------------------

var helpers = {

  any: function(array, options) {
    if (array.length > 0) {
      return options.fn(this);
    } else {
      return options.inverse(this);
    }
  },

  /**
   * Returns all of the items in the collection after the specified count.
   * @param  {Array}  array Collection
   * @param  {Number} count Number of items to exclude
   * @return {Array}        Array excluding the number of items specified
   */
  after: function(array, count) {
    return array.slice(count);
  },

  /**
   * Use all of the items in the collection after the specified count
   * inside a block.
   */
  withAfter: function(array, count, options) {
    array = array.slice(count);
    var result = '';
    for (var item in array) {
      result += options.fn(array[item]);
    }
    return result;
  },

  /**
   * Converts a string such as "foo, bar, baz" to an ES Array of strings.
   * @credit: http://bit.ly/1840DsB
   */
  arrayify: function(str) {
    return str.split(',').map(function(tag) {
      return "\"" + tag + "\"";
    });
  },

  /**
   * Returns all of the items in the collection before the specified
   * count. Opposite of {{after}}.
   */
  before: function(array, count) {
    return array.slice(0, -count);
  },

  /**
   * Use all of the items in the collection before the specified count
   * inside a block. Opposite of {{withAfter}}
   */
  withBefore: function(array, count, options) {
    array = array.slice(0, -count);
    var result = '';
    for (var item in array) {
      result += options.fn(array[item]);
    }
    return result;
  },

  /**
   * Returns the first item in a collection.
   */
  first: function(array, count) {
    if (helperutils.isUndefined(count)) {
      return array[0];
    } else {
      return array.slice(0, count);
    }
  },

  /**
   * Use the first item in a collection inside a block.
   */
  withFirst: function(array, count, options) {
    if (!helperutils.isUndefined(array)) {
      array = helperutils.result(array);
      if (!helperutils.isUndefined(count)) {
        count = parseFloat(helperutils.result(count));
      }
      if (helperutils.isUndefined(count)) {
        options = count;
        return options.fn(array[0]);
      } else {
        array = array.slice(0, count);
        var result = '';
        for (var item in array) {
          result += options.fn(array[item]);
        }
        return result;
      }
    } else {
      return console.error('{{withFirst}} takes at least one argument (array).');
    }
  },

  /**
   * Returns the last item in a collection. Opposite of `first`.
   */
  last: function(array, count) {
    if (helperutils.isUndefined(count)) {
      return array[array.length - 1];
    } else {
      return array.slice(-count);
    }
  },

  /**
   * Use the last item in a collection inside a block.
   * Opposite of {{withFirst}}.
   */
  withLast: function(array, count, options) {
    if (helperutils.isUndefined(count)) {
      options = count;
      return options.fn(array[array.length - 1]);
    } else {
      array = array.slice(-count);
      var result = '';
      for (var item in array) {
        result += options.fn(array[item]);
      }
      return result;
    }
  },

  /**
   * Joins all elements of a collection into a string
   * using a separator if specified.
   */
  join: function(array, separator) {
    return array.join(helperutils.isUndefined(separator) ? ' ' : separator);
  },

  /**
   * Handlebars "joinAny" block helper that supports
   * arrays of objects or strings. implementation found here:
   * https://github.com/wycats/handlebars.js/issues/133
   *
   * If "delimiter" is not speficified, then it defaults to ",".
   * You can use "start", and "end" to do a "slice" of the array.
   * @example:
   *   Use with objects:
   *   {{#join people delimiter=" and "}}{{name}}, {{age}}{{/join}}
   * @example:
   *   Use with arrays:
   *   {{join jobs delimiter=", " start="1" end="2"}}
   *
   */
  joinAny: function(items, block) {
    var delimiter = block.hash.delimiter || ",";
    var start = block.hash.start || 0;
    var len = (items ? items.length : 0);
    var end = block.hash.end || len;
    var out = '';
    if (end > len) {
      end = len;
    }
    if ('function' === typeof block) {
      var i = start;
      while (i < end) {
        if (i > start) {
          out += delimiter;
        }
        if ('string' === typeof items[i]) {
          out += items[i];
        } else {
          out += block(items[i]);
        }
        i++;
      }
      return out;
    } else {
      return [].concat(items).slice(start, end).join(delimiter);
    }
  },

  sort: function(array, field) {
    if (helperutils.isUndefined(field)) {
      return array.sort();
    } else {
      return array.sort(function(a, b) {
        return a[field] > b[field];
      });
    }
  },

  withSort: function(array, field, options) {
    array = _.cloneDeep(array);
    var getDescendantProp = function(obj, desc) {
      var arr = desc.split('.');
      while (arr.length && (obj = obj[arr.shift()])) {
        continue;
      }
      return obj;
    };
    var result = '';
    var item;
    var i;
    var len;
    if (helperutils.isUndefined(field)) {
      options = field;
      array = array.sort();
      if (options.hash && options.hash.dir === 'desc') {
        array = array.reverse();
      }
      for (i = 0, len = array.length; i < len; i++) {
        item = array[i];
        result += options.fn(item);
      }
    } else {
      array = array.sort(function(a, b) {
        var aProp = getDescendantProp(a, field);
        var bProp = getDescendantProp(b, field);
        if (aProp > bProp) {
          return 1;
        } else {
          if (aProp < bProp) {
            return -1;
          }
        }
        return 0;
      });
      if (options.hash && options.hash.dir === 'desc') {
        array = array.reverse();
      }
      for (item in array) {
        result += options.fn(array[item]);
      }
    }
    return result;
  },

  length: function(array) {
    return (!array) ? 0 : array.length;
  },

  lengthEqual: function(array, length, options) {
    if (array.length === length) {
      return options.fn(this);
    } else {
      return options.inverse(this);
    }
  },

  empty: function(array, options) {
    if (array.length <= 0) {
      return options.fn(this);
    } else {
      return options.inverse(this);
    }
  },

  inArray: function(array, value, options) {
    var _indexOf = require('../utils/lib/indexOf');
    if (_indexOf.call(array, value) >= 0) {
      return options.fn(this);
    } else {
      return options.inverse(this);
    }
  },

  filter: function(array, value, options) {
    var data = void 0;
    var content = '';
    var results = [];
    if (options.data) {
      data = Handlebars.createFrame(options.data);
    }
    // filtering on a specific property
    if (options.hash && options.hash.property) {
      var search = {};
      search[options.hash.property] = value;
      results = _.filter(array, search);
    } else {
      // filtering on a string value
      results = _.filter(array, function(v, k) {
        return value === v;
      });
    }
    if (results && results.length > 0) {
      for(var i=0; i < results.length; i++){
        content += options.fn(results[i], {data: data});
      }
    } else {
      content = options.inverse(this);
    }
    return content;
  },

  /**
   * Similar to {{#each}} helper, but treats array-like objects
   * as arrays (e.g. objects with a `.length` property that
   * is a number) rather than objects. This lets us iterate
   * over our collections items.
   */
  iterate: function(context, options) {
    var fn = options.fn;
    var inverse = options.inverse;
    var i = 0;
    var ret = "";
    var data = void 0;
    if (options.data) {
      data = Handlebars.createFrame(options.data);
    }
    if (context && typeof context === 'object') {
      if (typeof context.length === 'number') {
        var j = context.length;
        while (i < j) {
          if (data) {data.index = i;}
          ret = ret + fn(context[i], {data: data});
          i++;
        }
      } else {
        for (var key in context) {
          if (context.hasOwnProperty(key)) {
            if (data) {data.key = key;}
            ret = ret + fn(context[key], {data: data});
            i++;
          }
        }
      }
    }
    if (i === 0) {ret = inverse(this);}
    return ret;
  },

  /**
   * Credit: http://bit.ly/14HLaDR
   * @example:
   *   var accounts = [
   *     {'name': 'John', 'email': 'john@example.com'},
   *     {'name': 'Malcolm', 'email': 'malcolm@example.com'},
   *     {'name': 'David', 'email': 'david@example.com'}
   *   ];
   *
   *   {{#forEach accounts}}
   *     <a href="mailto:{{ email }}" title="Send an email to {{ name }}">
   *       {{ name }}
   *     </a>{{#unless isLast}}, {{/unless}}
   *   {{/forEach}}
   */
  forEach: function(array, fn) {
    var total = array.length;
    var buffer = "";
    // Better performance: http://jsperf.com/for-vs-forEach/2
    var i = 0;
    var j = total;
    while (i < j) {
      // stick an index property onto the item, starting
      // with 1, may make configurable later
      var item = array[i];
      item.index = i + 1;
      item._total = total;
      item.isFirst = i === 0;
      item.isLast = i === (total - 1);
      // show the inside of the block
      buffer += fn.fn(item);
      i++;
    }
    // return the finished buffer
    return buffer;
  },

  /**
   * Handlebars block helper to enumerate
   * the properties in an object
   */
  eachProperty: function(context, options) {
    var content = (function() {
      var results = [];
      for (var key in context) {
        var value = context[key];
        results.push(options.fn({
          key: key,
          value: value
        }));
      }
      return results;
    })();
    return content.join('');
  },

  /**
   * {{#eachIndex collection}}
   *   {{item}} is {{index}}
   * {{/eachIndex}}
   */
  eachIndex: function(array, options) {
    var i;
    var len;
    var result = '';
    var index;
    for (index = i = 0, len = array.length; i < len; index = ++i) {
      var value = array[index];
      result += options.fn({
        item: value,
        index: index
      });
    }
    return result;
  },

  // -----------------------------
  // Comparison Helpers
  // https://github.com/assemble/handlebars-helpers/blob/master/lib/helpers/helpers-comparisons.js
  // -----------------------------

  contains: function(str, pattern, options) {
    if (str.indexOf(pattern) !== -1) {
      return options.fn(this);
    }
    return options.inverse(this);
  },

  and: function(a, b, options) {
    if (a && b) {
      return options.fn(this);
    }
    return options.inverse(this);
  },

  icontains: function(str, pattern, options) {
    str = str.toLowerCase();
    pattern = pattern.toLowerCase();
    if (str.indexOf(pattern) !== -1) {
      return options.fn(this);
    }
    return options.inverse(this);
  },

  is: function(value, test, options) {
    if (value === test) {
      return options.fn(this);
    }
    return options.inverse(this);
  },

  isnt: function(value, test, options) {
    if (value !== test) {
      return options.fn(this);
    }
    return options.inverse(this);
  },

  or: function(a, b, options) {
    if (a || b) {
      return options.fn(this);
    }
    return options.inverse(this);
  },

  if_nth: function(nr, v, options) {
    v = v+1;
    if (v % nr === 0) {
      return options.fn(this);
    }
    return options.inverse(this);
  },

  if_eq: function(value, other, options) {
    if (value === other) {
      return options.fn(this);
    }
    return options.inverse(this);
  },

  unless_eq: function(value, other, options) {
    if (value === other) {
      return options.inverse(this);
    }
    return options.fn(this);
  },

  if_gt: function(value, other, options) {
    if (value > other) {
      return options.fn(this);
    }
    return options.inverse(this);
  },

  unless_gt: function(value, other, options) {
    if (value > other) {
      return options.inverse(this);
    }
    return options.fn(this);
  },

  if_lt: function(value, other, options) {
    if (value < other) {
      return options.fn(this);
    }
    return options.inverse(this);
  },

  unless_lt: function(value, other, options) {
    if (value < other) {
      return options.inverse(this);
    }
    return options.fn(this);
  },

  if_gte: function(value, other, options) {
    if (value >= other) {
      return options.fn(this);
    }
    return options.inverse(this);
  },

  unless_gte: function(value, other, options) {
    if (value >= other) {
      return options.inverse(this);
    }
    return options.fn(this);
  },

  if_lte: function(value, other, options) {
    if (value <= other) {
      return options.fn(this);
    }
    return options.inverse(this);
  },

  unless_lte: function(value, other, options) {
    if (value <= other) {
      return options.inverse(this);
    }
    return options.fn(this);
  },

  /**
   * Similar to {{#if}} block helper but accepts multiple arguments.
   * @author: Dan Harper <http://github.com/danharper>
   * @example: {{ifAny this that}}
   */
  ifAny: function() {
    var argLength = arguments.length - 1;
    var content = arguments[argLength];
    var success = true;
    var i = 0;
    while (i < argLength) {
      if (!arguments[i]) {
        success = false;
        break;
      }
      i += 1;
    }
    if (success) {
      return content.fn(this);
    }
    return content.inverse(this);
  },

  /**
   * Determine whether or not the @index is an even number or not
   * @author: Stack Overflow Answer <http://stackoverflow.com/questions/18976274/odd-and-even-number-comparison-helper-for-handlebars/18993156#18993156>
   * @author: Michael Sheedy <http://github.com/sheedy> (found code and added to repo)
   * @example: {{ifEven @index}}
   */
  ifEven: function(conditional, options) {
    if ((conditional % 2) === 0) {
      return options.fn(this);
    } else {
      return options.inverse(this);
    }
  },

  // -----------------------------
  // Date Helpers
  // https://github.com/assemble/handlebars-helpers/blob/master/lib/helpers/helpers-dates.js
  // -----------------------------

  /**
   * Port of formatDate-js library (http://bit.ly/18eo2xw)
   */
  formatDate: function(datestr, format) {
    var date = moment(datestr).toDate();
    return helperutils.format(date, format);
  },

  now: function(format) {
    var date = new Date();
    if (helperutils.isUndefined(format)) {
      return date;
    }
    return helperutils.format(date, format);
  },

  /**
   * Modified version of http://bit.ly/18WwJYf
   */
  timeAgo: function(date) {
    date = new Date(date);
    var seconds = Math.floor((new Date() - date) / 1000);
    var interval = Math.floor(seconds / 31536000);
    if (interval > 1) { return "" + interval + " years ago"; }
    interval = Math.floor(seconds / 2592000);
    if (interval > 1) { return "" + interval + " months ago"; }
    interval = Math.floor(seconds / 86400);
    if (interval > 1) { return "" + interval + " days ago"; }
    interval = Math.floor(seconds / 3600);
    if (interval > 1) { return "" + interval + " hours ago"; }
    interval = Math.floor(seconds / 60);
    if (interval > 1) { return "" + interval + " minutes ago"; }
    if (Math.floor(seconds) === 0) {
      return 'Just now';
    } else {
      return Math.floor(seconds) + ' seconds ago';
    }
  },
  
  // -----------------------------
  // Logging Helpers
  // https://github.com/assemble/handlebars-helpers/blob/master/lib/helpers/helpers-logging.js
  // -----------------------------
  
  log: function(value) {
    return console.log(value);
  },
  
  // -----------------------------
  // Math Helpers
  // https://github.com/assemble/handlebars-helpers/blob/master/lib/helpers/helpers-math.js
  // -----------------------------
  
  abs: function(value) {
    return Math.abs(value);
  },

  add: function(value, addition) {
    return value + addition;
  },

  subtract: function(value, substraction) {
    return value - substraction;
  },

  divide: function(value, divisor) {
    return value / divisor;
  },

  multiply: function(value, multiplier) {
    return value * multiplier;
  },

  floor: function(value) {
    return Math.floor(value);
  },

  ceil: function(value) {
    return Math.ceil(value);
  },

  round: function(value) {
    return Math.round(value);
  },

  sum: function() {
    var args = _.flatten(arguments);
    var sum = 0;
    var i = args.length - 1;
    while (i--) {
      sum +=  _.parseInt(args[i]) || 0;
    }
    return Number(sum);
  },
  
  // -----------------------------
  // Miscellaneous Helpers
  // https://github.com/assemble/handlebars-helpers/blob/master/lib/helpers/helpers-miscellaneous.js
  // -----------------------------
  
  default: function(value, defaultValue) {
    return value !== null ? value : defaultValue;
  },

  /**
   * http://handlebarsjs.com/block_helpers.html
   * @param  {[type]} options [description]
   * @return {[type]}         [description]
   */
  noop: function(options) {
    return options.fn(this);
  },

  /**
   * Build context from the attributes hash
   * @author Vladimir Kuznetsov <https://github.com/mistakster>
   */
  withHash: function(options) {
    return options.fn(options.hash || {});
  },
  
  // -----------------------------
  // Number Helpers
  // https://github.com/assemble/handlebars-helpers/blob/master/lib/helpers/helpers-numbers.js
  // -----------------------------
  
  /**
   * Add commas to numbers
   */
  addCommas: function(number) {
    return number.toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
  },

  /**
   * Round to the nearest int value and add commas to numbers
   */
  amountInt: function(amount) {
    return pk.utils.to_amount_int(amount);
  },

  amountIntAbs: function(amount) {
    return pk.utils.to_amount_int(Math.abs(amount));
  },

  /**
   * Round to the nearest 2 decimals and add commas to numbers
   */
  amountFloat: function(amount) {
    return pk.utils.to_amount_float(amount);
  },

 /**
  * Output a formatted phone number (800) 555-1212
  * @author: http://bit.ly/QlPmPr
  */
  formatPhoneNumber: function(num) {
    num = num.toString();
    return "(" + num.substr(0, 3) + ") " + num.substr(3, 3) + "-" + num.substr(6, 4);
  },

  /**
   * Generate a random number between two values
   * @author Tim Douglas <https://github.com/timdouglas>
   */
  random: function(min, max) {
    return _.random(min, max);
  },

  /**
   * Abbreviate numbers
   */
  toAbbr: function(number, digits) {
    if (helperutils.isUndefined(digits)) {
      digits = 2;
    }
    // @default: 2 decimal places => 100, 3 => 1000, etc.
    digits = Math.pow(10, digits);
    var abbr = ["k", "m", "b", "t"];
    var i = abbr.length - 1;
    while (i >= 0) {
      var size = Math.pow(10, (i + 1) * 3);
      if (size <= number) {
        number = Math.round(number * digits / size) / digits;
        // Special case where we round up to the next abbreviation
        if ((number === 1000) && (i < abbr.length - 1)) {
          number = 1;
          i++;
        }
        number += abbr[i];
        break;
      }
      i--;
    }
    return number;
  },

  toExponential: function(number, fractions) {
    if (helperutils.isUndefined(fractions)) {
      fractions = 0;
    }
    return number.toExponential(fractions);
  },

  toFixed: function(number, digits) {
    if (helperutils.isUndefined(digits)) {
      digits = 0;
    }
    return number.toFixed(digits);
  },

  toFloat: function(number) {
    return parseFloat(number);
  },

  toInt: function(number) {
    return parseInt(number, 10);
  },

  toPrecision: function(number, precision) {
    if (helperutils.isUndefined(precision)) {
      precision = 1;
    }
    return number.toPrecision(precision);
  },
  
  // -----------------------------
  // String Helpers
  // https://github.com/assemble/handlebars-helpers/blob/master/lib/helpers/helpers-strings.js
  // -----------------------------
  
  /**
   * Capitalize first word in a sentence
   */
  capitalizeFirst: function(str) {
    if (str && typeof str === "string") {
      return str.charAt(0).toUpperCase() + str.slice(1);
    }
  },

  /**
   * Capitalize each word in a sentence
   */
  capitalizeEach: function(str) {
    if (str && typeof str === "string") {
      return str.replace(/\w\S*/g, function(word) {
        return word.charAt(0).toUpperCase() + word.substr(1);
      });
    }
  },

  /**
   * Center a string using non-breaking spaces
   */
  center: function(str, spaces) {
    if (str && typeof str === "string") {
      var space = '';
      var i = 0;
      while (i < spaces) {
        space += '&nbsp;';
        i++;
      }
      return "" + space + str + space;
    }
  },

  /**
   * Replace periods in string with hyphens.
   */
  dashify: function(str) {
    if (str && typeof str === "string") {
      return str.split(".").join("-");
    }
  },

  /**
   * Replace spaces in string with hyphens.
   */
  hyphenate: function(str) {
    if (str && typeof str === "string") {
      return str.split(" ").join("-");
    }
  },

  /**
   * Make all letters in the string lowercase
   */
  lowercase: function(str) {
    if (str && typeof str === "string") {
      return str.toLowerCase();
    }
  },
  
  /**
   * Replace spaces in string with pluses.
   * @author: Stephen Way <https://github.com/stephenway>
   */
  plusify: function(str) {
    if (str && typeof str === "string") {
      return str.split(" ").join("+");
    }
  },

  /**
   * Output a Handlebars safeString
   */
  safeString: function(str) {
    if (str && typeof str === "string") {
      return new helperutils.safeString(str);
    }
  },

  /**
   * Sentence case
   */
  sentence: function(str) {
    if (str && typeof str === "string") {
      return str.replace(/((?:\S[^\.\?\!]*)[\.\?\!]*)/g, function(txt) {
        return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
      });
    }
  },

  /**
   * Title case. "This is Title Case"
   */
  titleize: function(str) {
    if (str && typeof str === "string") {
      var title = str.replace(/[ \-_]+/g, ' ');
      var words = title.match(/\w+/g);
      var capitalize = function(word) {
        return word.charAt(0).toUpperCase() + word.slice(1);
      };
      return ((function() {
        var i, len, results;
        results = [];
        for (i = 0, len = words.length; i < len; i++) {
          var word = words[i];
          results.push(capitalize(word));
        }
        return results;
      })()).join(' ');
    }
  },

  uppercase: function(options) {
    if (options && typeof options === "string") {
      return options.toUpperCase();
    } else if (options && typeof options === "object") {
      return options.fn(this).toUpperCase();
    }
  },

  reverse: function(str) {
    if (str && typeof str === "string") {
      return str.split('').reverse().join('');
    }
  },

  /**
   * Return the number of occurrances of a string, within a string
   * @author: Jon Schlinkert <http://github.com/jonschlinkert>
   * @param  {String} str       The haystack
   * @param  {String} substring The needle
   * @return {Number}           The number of times the needle is found in the haystack.
   */
  count: function(str, substring) {
    if (str && typeof str === "string") {
      var n = 0;
      var pos = 0;
      var l = substring.length;
      while (true) {
        pos = str.indexOf(substring, pos);
        if (pos > -1) {
          n++;
          pos += l;
        } else {
          break;
        }
      }
      return n;
    }
  },

  /**
   * Replace occurrences of string "A" with string "B"
   * @author: Jon Schlinkert <http://github.com/jonschlinkert>
   */
  replace: function(str, a, b) {
    if (str && typeof str === "string") {
      return str.split(a).join(b);
    }
  },

  /**
   * Truncate the input string and removes all HTML tags
   * @author: Jon Schlinkert <http://github.com/jonschlinkert>
   * @param  {String} str      The input string.
   * @param  {Number} limit    The number of characters to limit the string.
   * @param  {String} append   The string to append if charaters are omitted.
   * @return {String}          The truncated string.
   */
  ellipsis: function(str, limit, append) {
    if (helperutils.isUndefined(append)) {
      append = '';
    }
    var sanitized = str.replace(/(<([^>]+)>)/g, '');
    if (sanitized.length > limit) {
      return sanitized.substr(0, limit - append.length) + append;
    }
    return sanitized;
  },

  /**
   * Truncates a string given a specified `length`,
   * providing a custom string to denote an `omission`.
   */
  truncate: function(str, limit, omission) {
    if (helperutils.isUndefined(omission)) {
      omission = '';
    }
    if (str.length > limit) {
      return str.substring(0, limit - omission.length) + omission;
    }
    return str;
  },

  /**
   * Tests whether a string begins with the given prefix.
   * Behaves sensibly if the string is null.
   * @author: Dan Fox <http://github.com/iamdanfox>
   *
   * @example:
   *   {{#startsWith "Goodbye" "Hello, world!"}}
   *     Whoops
   *   {{else}}
   *     Bro, do you even hello world?
   *   {{/startsWith}}
   */
  startsWith: function(prefix, str, options) {
    if ((str !== null ? str.indexOf(prefix) : void 0) === 0) {
      return options.fn(this);
    }
    return options.inverse(this);
  },
  
  // -----------------------------
  // URL Helpers
  // https://github.com/assemble/handlebars-helpers/blob/master/lib/helpers/helpers-url.js
  // -----------------------------
  
  stripQuerystring: function(url) {
    return url.split("?")[0];
  },

  /**
   * Encodes a Uniform Resource Identifier (URI) component
   * by replacing each instance of certain characters by
   * one, two, three, or four escape sequences representing
   * the UTF-8 encoding of the character.
   * @author: Jon Schlinkert <http://github.com/jonschlinkert>
   */
  encodeURI: function(uri) {
    return encodeURIComponent(uri);
  },

  /**
   * Decodes a Uniform Resource Identifier (URI) component
   * previously created by encodeURIComponent or by a
   * similar routine.
   * @author: Jon Schlinkert <http://github.com/jonschlinkert>
   */
  decodeURI: function(encodedURI) {
    return decodeURIComponent(encodedURI);
  },

  /**
   * Return yes or no based on the test
   */
  yesNo: function(test, yes, no) {
    return test ? yes : no;
  },

};

for (var helper in helpers) {
  if (helpers.hasOwnProperty(helper)) {
    Handlebars.registerHelper(helper, helpers[helper]);
  }
}



// Encoding: UTF-8
// Guath Docs: https://developers.google.com/identity/sign-in/web/server-side-flow
'use strict';

pk.login = {
  LOGIN_URL: '/api/user/login',
  GAUTH_CLIENTID: '910136763601-nm3knsgkf5pbt4n6drlnsfea7ibf2mfm.apps.googleusercontent.com',
  KEYS: {F2:113},

  init: function() {
    this.container = $('#logo');
    this.form = $('#logo form');
    console.debug('init pk.login on #'+ this.container.attr('id'));
    this.init_gauth();
    this.init_triggers();
    this.init_shortcuts();
  },

  init_gauth: function() {
    var self = this;
    gapi.load('auth2', function() {
      self.gauth = gapi.auth2.init({client_id:self.GAUTH_CLIENTID});
    });
  },

  init_triggers: function() {
      var self = this;
      // Display login form
      this.container.on('click', function(event) {
        event.stopPropagation();
        self.show_form();
      }).children().on('click', function(event) {
        event.stopPropagation();
      });
      // Hide login form
      $('header').on('click', function(event) {
        event.preventDefault();
        self.hide_form();
      });
      // Submit login form
      self.form.on('submit', function(event) {
        event.preventDefault();
        event.stopPropagation();
        self.login();
      });
      // Sign in to Google
      $('#gauth').on('click', function() {
        self.gauth.grantOfflineAccess().then(function(data) {
          if (data['code']) { self.login(data); }
        });
      });
  },

  init_shortcuts: function() {
    var self = this;
    var KEYS = this.KEYS;
    $(document).on('keydown', function(event) {
      if ((event.keyCode == KEYS.F2) && (!$('body').hasClass('authenticated'))) {
        event.preventDefault();
        event.stopPropagation();
        self.show_form();
      }
    });
  },

  show_form: function() {
    if (this.container.hasClass('enabled')) {
      return null;
    }
    this.container.addClass('enabled');
    this.form.find('input[name=email]').val('').focus();
    this.form.find('input[name=password]').val('');
  },

  hide_form: function() {
    this.container.removeClass('enabled');
    this.form.removeClass('error');
  },

  login: function(data) {
    var self = this;
    var data = data || self.form.serializeArray();
    var xhr = $.ajax({url:self.LOGIN_URL, data:data, type:'POST', dataType:'json'});
    self.form.removeClass('error');
    xhr.done(function(data, textStatus, jqXHR) {
      self.form.animatecss('rubberBand', function() {
        location.reload();
      });
    });
    xhr.fail(function(jqXHR, textStatus, errorThrown) {
      self.form.animatecss('shake');
      self.form.addClass('error');
    });
  },

};



// Encoding: UTF-8
'use strict';

pk.magnets = {
  ACTIONS: {ADD:'add', UPDATE:'update', REMOVE:'remove', META:'meta'},
  DRAGGING: 'dragging',
  FRAMES_PER_SEC: 20,
  MAX_ROTATION: 7,
  KEYS: {ENTER:13},

  init: function(selector, opts) {
    this.container = $(selector);
    if (!this.container.length) { return; }
    console.debug('init pk.magnets on '+ selector);
    this.newword = this.container.find('#addword');
    this.canvas = this.container.find('#canvas');
    this.uri = pk.utils.url({
      protocol: window.location.protocol == 'https:' ? 'wss:' : 'ws:',
      pathname: '/ws/magnets?subscribe-broadcast&publish-broadcast',
    });
    this.ws = this.init_websocket(this.uri);
    this.init_triggers();
    this.init_shortcuts();
  },
  
  init_triggers: function() {
    var self = this;
    this.container.on('mousedown', '.word', function(event) {
      event.preventDefault();
      self.drag($(this), event);
    });
  },
  
  init_shortcuts: function() {
    var self = this;
    // add word
    this.newword.keyup(function(event) {
      if (event.keyCode == self.KEYS.ENTER) {
        event.preventDefault();
        $.map($(this).val().split(' '), function(w) { 
          self.add_word(w);
        });
        $(this).val('');
      }
    });
  },
  
  init_websocket: function(uri) {
    var self = this;
    return new Redsocket({uri:uri, heartbeat_msg:'heartbeat',
        receive_message: function(data) { self.receive_message(data); },
        receive_heartbeat: function(latency) { self.receive_heartbeat(latency); },
        connected: function(data) { self.connected(data); },
    });
  },
  
  add_word: function(data) {
    // Check input data is a simple string and generate new data
    if (typeof(data) == 'string') {
      data = {
        word: data,
        cls: '',
        id: 'w'+ pk.utils.hash(data + Date.now()),
        x: parseInt(Math.random() * (this.canvas.width() - 100)) + 20,
        y: parseInt(Math.random() * (this.canvas.height() - 50)) + 20,
        r: this.choose_rotation(),
      };
      this.send_message(this.ACTIONS.ADD, data);
    }
    // Build the DOM object and add it to canvas
    if (!this.canvas.find('#'+ data.id).length) {
      var elem = $(pk.utils.format('<div id="{0}" class="word">{1}</div>', data.id, data.word));
      this.update_word(data, elem);
      this.canvas.append(elem);
    }
  },
  
  choose_rotation: function() {
    return parseInt((Math.random() * (this.MAX_ROTATION * 2)) - this.MAX_ROTATION);
  },
  
  drag: function(elem, event) {
    var self = this;
    var h = elem.outerHeight();
    var w = elem.outerWidth();
    var y = elem.position().top + h - event.pageY;
    var x = elem.position().left + w - event.pageX;
    // drag word
    var move = function(event) {
      event.preventDefault();
      var newdata = {
        cls: self.DRAGGING,
        x: parseInt(event.pageX + x - w),
        y: parseInt(event.pageY + y - h),
      };
      self.update_word(newdata, elem);
    };
    // update (using fps)
    var timer = setInterval(function() {
      self.send_message(self.ACTIONS.UPDATE, elem.data('data'));
    }, 1000 / this.FRAMES_PER_SEC);
    // stop dragging
    var stop = function(event) {
      event.preventDefault();
      clearTimeout(timer);
      $(document).unbind('mousemove', move);
      $(document).unbind('mouseup', stop);
      elem.removeClass(self.DRAGGING);
      if (!self.is_inbounds(elem)) {
        self.send_message(self.ACTIONS.REMOVE, elem.data('data'));
        return self.remove_word(elem.data('data'));
      }
      var data = self.update_word({cls:'', r:self.choose_rotation()}, elem);
      self.send_message(self.ACTIONS.UPDATE, data);
    };
    // init
    $(document).bind('mousemove', move);
    $(document).bind('mouseup', stop);
  },
  
  is_inbounds: function(elem) {
    var x1 = parseInt(elem.position().left);
    var y1 = parseInt(elem.position().top);
    var x2 = parseInt(x1 + elem.width());
    var y2 = parseInt(y1 + elem.height());
    return !((x1 < -5) || (y1 < -5) || (x2 > this.canvas.width() + 5) || (y2 > this.canvas.height() + 5));
  },
  
  remove_word: function(data) {
    this.canvas.find('#'+data.id).remove();
  },
  
  update_word: function(newdata, elem) {
    elem = elem !== undefined ? elem : this.canvas.find('#'+newdata.id);   
    var data = $.extend({}, elem.data('data'), newdata);
    if ('cls' in newdata) { elem.attr('class', 'word '+ data.cls); }
    if ('x' in newdata) { elem.css('left', data.x +'px'); }
    if ('y' in newdata) { elem.css('top', data.y +'px'); }
    if ('r' in newdata) { elem.css('transform', 'rotate('+ data.r +'deg)'); }
    elem.data('data', data);
    return data;
  },
  
  connected: function() {
    console.debug('connected: '+ this.uri);
  },
  
  receive_message: function(datastr) {
    var data = JSON.parse(datastr);
    if (data.action == this.ACTIONS.ADD) { this.add_word(data); }
    else if (data.action == this.ACTIONS.UPDATE) { this.update_word(data); }
    else if (data.action == this.ACTIONS.REMOVE) { this.remove_word(data); }
    else if (data.action == this.ACTIONS.META) { $('#clients').text(data.clients); }
  },
  
  receive_heartbeat: function(latency) {
    $('#latency').text(latency);
  },
  
  send_message: function(action, data) {
    var datastr = JSON.stringify($.extend({}, data, {action:action}));
    this.ws.send_message(datastr);
  },
  
};



// Encoding: UTF-8
'use strict';

pk.notes = {
  KEYS: {TAB:9, ENTER:13, ESC:27, F3:114, UP:38, DOWN:40},
  URL_NOTES: '/api/notes',

  init: function(selector, opts) {
    this.container = $(selector);
    if (!this.container.length) { return; }
    console.debug('init pk.notes on '+ selector);
    this.opts = $.extend(true, {}, this.defaults, opts);
    this.xhr = null;
    this.search = null;
    this.init_elements();
    this.init_triggers();
    this.init_shortcuts();
    this.update_list(this.searchinput.val(), this.opts.init_noteid);
  },
  
  init_elements: function() {
    this.sidepanel = this.container.find('#sidepanel');
    this.searchinput = this.container.find('#search');
    this.addnote = this.container.find('#search-action');
    this.notelist = this.container.find('#sidepanel-content');
  },
  
  init_triggers: function() {
    var self = this;
    // search input changes
    this.searchinput.on('change paste keyup', function(event) {
      if (_.valuesIn(this.KEYS).indexOf(event.keyCode) == -1) {
        event.preventDefault();
        var url = pk.utils.update_url(null, {search:$(this).val()})
        window.history.replaceState(null, null, url);
        self.update_list($(this).val());
      }
    });
    // start a new note
    this.addnote.on('click', function() {
      event.preventDefault();
      self.new_note();
    });
  },
  
  init_shortcuts: function() {
    var self = this;
    var KEYS = this.KEYS;
    // select noteitems via keyboard
    $(document).on('keydown', function(event) {
      var noteitems = self.notelist.find('.notes-item');
      var focused = self.searchinput.is(':focus');
      if (event.keyCode == KEYS.F3) {
        event.preventDefault();
        event.stopPropagation();
        self.searchinput.focus();
      } else if (focused && (_.valuesIn(KEYS).indexOf(event.keyCode) > -1)) {
        event.preventDefault();
        var selected = noteitems.filter('.selected');
        if ((event.keyCode == KEYS.DOWN) || (event.keyCode == KEYS.TAB)) {
          var next = selected.next();
          next = next.length ? next : noteitems.filter(':first-child');
          noteitems.removeClass('selected');
          next.addClass('selected');
        } else if (event.keyCode == KEYS.UP) {
          var prev = selected.prev().filter('.notes-item');
          prev = prev.length ? prev : noteitems.filter(':last-child');
          noteitems.removeClass('selected');
          prev.addClass('selected');
        } else if ((event.keyCode == KEYS.ENTER) && (selected.length)) {
          window.top.location = selected.attr('href');
        } else if (event.keyCode == KEYS.ESC) {
          noteitems.removeClass('selected');
        }
      }
    });
  },
  
  new_note: function() {
    pk.editor.toggle_editor(true);
    pk.editor.history.saved = {};
    pk.editor.codemirror.setValue('');
    pk.editor.title.val('');
    pk.editor.tags.val('');
    window.history.replaceState('','','/n/');
  },
  
  update_list: function(search, noteid) {
    var self = this;
    if (search == this.search) { return; }
    try { this.xhr.abort(); } catch(err) { }
    var url = search ? this.URL_NOTES +'?search='+ encodeURIComponent(search) : this.URL_NOTES;
    this.xhr = $.ajax({url:url, type:'GET', dataType:'json'});
    this.xhr.done(function(data, textStatus, jqXHR) {
      var ctx = {notes:data.results, search:encodeURIComponent(search), noteid:noteid};
      var html = pk.templates.note_items(ctx);
      self.notelist.html(html);
      self.search = search;
    });
  },

  defaults: {
    editor: null,         // (required) reference to pk.editor object
    init_noteid: null,    // initial noteid to highlight
  },

};



// Encoding: UTF-8
'use strict';

// Animate a jquery object
// https://daneden.github.io/animate.css/
$.fn.animatecss = function(effect, callback) {
  $(this).addClass('animated '+effect).one(pk.ANIMATIONEND, function() {
    $(this).removeClass('animated '+effect);
    if (callback !== undefined) {
      callback();
    }
  });
};


// Disable parent scroll (side effect: forces scroll to 30px)
// http://stackoverflow.com/questions/25125560/prevent-parent-scroll-when-in-child-div
$.fn.disableParentScroll = function() {
  $(this).on('mousewheel', function(event) {
    var e = event.originalEvent;
    var d = e.wheelDelta || -e.detail;
    this.scrollTop += (d < 0 ? 1 : -1) * 30;
    event.preventDefault();
  });
};


// ScrollBottom (similar to scrolltop, but use bottom as the root)
// see: http://stackoverflow.com/questions/4188903/opposite-of-scrolltop-in-jquery
$.fn.scrollBottom = function(val) { 
  if (val !== undefined) {
    return this.scrollTop($(document).height() - val - this.height());
  }
  return $(document).height() - this.scrollTop() - this.height();
};


// Always send CSRF token with ajax requests
// https://docs.djangoproject.com/en/1.8/ref/csrf/#ajax
function csrfSafeMethod(method) {
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({beforeSend: function(xhr, settings) {
  if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
    var csrftoken = Cookies.get('csrftoken');
    xhr.setRequestHeader('X-CSRFToken', csrftoken);
  }
}});



// Encoding: UTF-8
'use strict';

pk.utils = {

  add_commas: function(value) {
    var parts = value.toString().split('.');
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    return parts.join('.');
  },

  ajax: function(url, data, type) {
    type = type ? type : 'POST';
    var xhr = $.ajax({url:url, data:data, type:type, dataType:'json'});
    return xhr.then(function(data, textStatus, jqXHR) {
      var deferred = new $.Deferred();
      if (!data.success) 
        return deferred.reject(jqXHR, textStatus, data);
      return deferred.resolve(data, textStatus, jqXHR);
    });
  },

  autosize_textarea: function(jqtext, padding, lineheight, minlines) {
    // padding and line-height must be set for this to work.
    minlines = minlines || 2;
    jqtext.on('input keyup', function(event) {
      var nlines = jqtext.val().split('\n').length
      var lines = Math.max(minlines, nlines);
      $(this).css('height', (lines * lineheight) + padding);
    }).trigger('input');
  },

  basename: function(path) {
    return path.split('/').reverse()[0];
  },

  copycode: function(selector) {
    // initilize the clipboard plugin
    var clippy = new Clipboard('article pre .copycode', {
      text: function(trigger) {
        return _.trimEnd($(trigger).parents('pre').text());
      }
    });
    clippy.on('success', function(event) {
      $(event.trigger).animatecss('bounce');
    });
    // append copy button to each code block
    selector = this.set_default(selector, 'article pre code');
    $(selector).each(function(i, block) {
      var btn = $('<span class="copycode mdi mdi-content-duplicate"></span>');
      $(block).prepend(btn);
    });
  },
  
  enable_animations: function() {
    setTimeout(function() {
      $('body').removeClass('preload');
    }, 500);
  },
  
  format: function() {
    var result = arguments[0];
    for (var i=0; i<arguments.length-1; i++) {
        var regexp = new RegExp('\\{'+i+'\\}', 'gi');
        result = result.replace(regexp, arguments[i+1]);
    }
    return result;
  },

  hash: function(str) {
    var hash = 0, i, chr, len;
    if (str.length === 0) return hash;
    for (i = 0, len = str.length; i < len; i++) {
      chr = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + chr;
      hash |= 0; // Convert to 32bit integer
    }
    return Math.abs(hash).toString(16);
  },
  
  highlightjs: function(selector) {
    selector = this.set_default(selector, 'article pre code');
    $(selector).each(function(i, block) {
      hljs.highlightBlock(block);
    });
  },

  init_tooltips: function(selector) {
    selector = this.set_default(selector, '[data-toggle="tooltip"]');
    console.debug('init tooltips on '+ selector);
    $(selector).tooltip({delay:{show:200, hide:50}});
  },

  rset: function(object, property, value) {
    var parts = property.split('.');
    var current = parts.shift();
    var pointer = object;
    while (parts.length > 0) {
      if (pointer[current] === undefined)
        pointer[current] = {};
      pointer = pointer[current];
      current = parts.shift();
    }
    pointer[current] = value;
  },

  rget: function(object, property, delim) {
    delim = delim === undefined ? '.' : delim;
    var parts = property.split(delim);
    var current = parts.shift();
    if (object[current] !== undefined) {
      if (parts.length >= 1)
        return getProperty(object[current], parts.join(delim), delim);
      return object[current];
    }
    return undefined;
  },

  round: function(number, precision) {
    var factor = Math.pow(10, precision);
    var tempNumber = number * factor;
    var roundedTempNumber = Math.round(tempNumber);
    return roundedTempNumber / factor;
  },

  set_default: function(input, default_value) {
    return typeof input !== 'undefined' ? input : default_value;
  },

  url: function(opts) {
    var protocol = opts.protocol || window.location.protocol || '';
    var hostname = opts.hostname || window.location.hostname || '';
    var port = opts.port || window.location.port || '';
    var pathname = opts.pathname || window.location.pathname || '';
    var search = opts.search || window.location.search || '';
    if (port) { port = ':'+ port; }
    return pk.utils.format('{0}//{1}{2}{3}{4}', protocol, hostname, port, pathname, search);
  },

  update_url: function(url, params) {
    url = url === null ? new URL(window.location.href) : new URL(url);
    for (var key in params) {
      var value = params[key];
      if (value == '' || value == null) { url.searchParams.delete(key); }
      else { url.searchParams.set(key, value); }
    }
    return url.toString();
  },

  //--------------------
  // Budget Functions
  // validate and convert int to amount
  is_int: function(value) {
    return !!value.match(/^-?\d+$/);
  },

  is_float: function(value) {
    return !!value.match(/^-?\d+\.\d{2}$/) || !!value.match(/^-?\d+$/);
  },

  to_int: function(value) {
    value = value.replace('$', '').replace(',', '');
    return pk.utils.round(value, 0);
  },

  to_float: function(value) {
    value = value.replace('$', '').replace(',', '');
    return pk.utils.round(value, 2).toFixed(2);
  },

  to_amount_int: function(value) {
    var negative = value < 0;
    value = Math.round(Math.abs(value));
    if (negative) { return '-$'+ pk.utils.add_commas(value); }
    return '$'+ pk.utils.add_commas(value);
  },

  to_amount_float: function(value) {
    var result;
    var negative = value < 0;
    value = Math.abs(value);
    if (negative) { result = '-$'+ pk.utils.add_commas(value); }
    else { result = '$'+ pk.utils.add_commas(value); }
    if (result.match(/\.\d{1}$/)) { return result +'0'; }
    if (!result.match(/\./)) { return result +'.00'; }
    return result;
  },

};
