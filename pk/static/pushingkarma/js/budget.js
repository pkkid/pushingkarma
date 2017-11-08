/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

pk.budget = {
  BUDGET_SELECTOR: '#budget',
  ROW:'.pkrow', EDIT:'.pkedit',
  KEYS: {TAB:9, ENTER:13, ESC:27, F3:114, UP:38, DOWN:40},
  LOADMORE_INTERVAL: 100, LOADMORE_DISTANCE: 200,
  URL_SUMMARY: window.location.origin +'/api/transactions/summary',
  URL_ACCOUNTS: window.location.origin +'/api/accounts',
  URL_CATEGORIES: window.location.origin +'/api/categories',
  URL_TRANSACTIONS: window.location.origin +'/api/transactions',
  URL_UPLOAD: window.location.origin +'/api/transactions/upload',
  
  init: function(selector) {
    this.container = $(selector);
    if (!this.container.length) { return; }
    console.debug('init pk.budget on '+ selector);
    this.xhr = null;                            // main actions xhr reference
    this.xhract = null;                         // accounts xhr reference
    this.xhrcat = null;                         // categories xhr reference
    this.xhrtrx = null;                         // transactions xhr reference
    this.trxpage = null;                        // last loaded trx page
    this.clicktimer = null;                     // detects single vs dblclick
    this.category_choices = [];                 // category name choices
    this.summary_data = null;                   // summary data response
    this.params = {side:'categories',           // URL params for current view
      view:'summary', search:''};  
    this.init_elements();                       // cache top level elements
    this.bind_search_edit();                    // update transactions on search
    this.bind_view_button();                    // show or hide the transaction list
    this.bind_row_edit();                       // handle single and dblclick events
    this.bind_save_notes();                     // Save popover notes on blur
    this.bind_category_add();                   // create new category items
    this.bind_drag_files();                     // show dropzone when uploading
    this.bind_row_highlight();                  // highlight rows on mouseover
    this.bind_infinite_scroll();                // auto-load next page of transactions
    this.init_shortcuts();                      // bind keyboard shortcuts
    // load initial display data
    var side = new URL(window.location.href).searchParams.get('side');
    var view = new URL(window.location.href).searchParams.get('view');
    side == 'accounts' ? this.update_accounts() : this.update_categories();
    view == 'transactions' ? this.update_transactions() : this.update_summary();
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
  },

  bind_search_edit: function() {
    // update transactions when search input changes
    var self = this;
    this.searchinput.on('change paste keyup', function(event) {
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
    var click_selector = 'tbody td';
    this.container.on('click', click_selector, function(event) {
      event.preventDefault();
      var td = $(this);
      if (event.detail == 1) {
        self.clicktimer = setTimeout(function() {
          // display popover on single click
          if (!td.closest(self.ROW).hasClass('popped')) {
            if (td.closest('#categories').length) {
              self.popover_display(td, 'category_popover');
            } else if (td.closest('#summary').length) {
              self.popover_display(td, 'summary_popover');
            }
          }
        }, 200);
      } else if (event.detail == 2) {
        // edit category or transaction on dblclick
        clearTimeout(self.clicktimer);
        if (td.hasClass(self.EDIT.replace('.',''))) {
          self.item_edit(td);
        }
      }    
    });
    // close the popover if clicking somewhere else
    $(document).on('click', function(event) {
      var target = $(event.target);
      if (!target.closest(self.ROW).hasClass('popped') && !target.closest('.popover').length) {
        $('.popped').removeClass('popped').popover('hide');
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

  init_shortcuts: function() {
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
          var next = row.next(self.ROW).find('[data-name='+name+']');
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

  autocomplete: function() {
    return $('.ui-autocomplete:visible').length > 0;
  },

  clean_data: function(data) {
    for (var name in data) {
      if (name == 'approved') { data[name] = data[name] == 'x'; }
    }
    return data;
  },

  popover_display: function(item, tmpl) {
    var self = this;
    var row = item.closest(self.ROW);
    var type = row.data('type');
    var url = row.data('url') +'/details';
    var xhr = $.ajax({url:url, type:'GET', dataType:'json'});
    row.removeData('bs.popover');
    xhr.done(function(data, textStatus, jqXHR) {
      var content = pk.templates[tmpl](data);
      row.popover({trigger:'manual', placement:'bottom', html:true,
        content:content}).addClass('popped').popover('show');
    });
  },

  show_accounts: function() {
    var self = this;
    self.params.side = 'accounts';
    self.categories.fadeOut('fast', function() {
      self.accounts.fadeIn('fast');
    });
    // update the url
    var url = pk.utils.update_url(null, self.params);
    window.history.replaceState(null, null, url);
  },

  show_categories: function() {
    var self = this;
    self.params.side = 'categories';
    self.accounts.fadeOut('fast', function() {
      self.categories.fadeIn('fast');
    });
    var url = pk.utils.update_url(null, self.params);
    window.history.replaceState(null, null, url);
  },

  show_summary: function() {
    var self = this;
    self.params.view = 'summary';
    self.params.search = '';
    self.viewbtn.attr('class', 'mdi mdi-format-list-bulleted');
    self.viewbtn.tooltip('hide').attr('data-original-title', 'View Transactions');
    self.transactions.fadeOut('fast', function() {
      self.summary.fadeIn('fast');
      self.sidepanel.addClass('toedge');
    });
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
      self.sidepanel.removeClass('toedge');
    });
    // update the url
    var url = pk.utils.update_url(null, self.params);
    window.history.replaceState(null, null, url);
  },

  text_or_val: function(item) {
    var child = item.children().first();
    if (child.is('div')) {
      // Get value from a div
      var value = child.text().trim();
      value = item.hasClass('int') ? pk.utils.to_int(value) : value;
      value = item.hasClass('float') ? pk.utils.to_float(value) : value;
    } else {
      // Get value from an input
      value = child.val().trim();
      if ((value == '') && (item.data('default') !== undefined)) {
        value = item.data('default');
      }
    }
    return value;
  },

  item_delete: function(item) {
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
    if (append == true) {
      var searchval = this.searchinput.val();
      var exists = searchval.toLowerCase().indexOf(query.toLowerCase()) >= 0;
      query = exists ? searchval : searchval +' '+ query;
    }
    this.searchinput.val(query);
    this.update_transactions();
  },
 
  update_accounts: function() {
    var self = this;
    self.show_accounts();
    try { this.xhract.abort(); } catch(err) { }
    this.xhract = $.ajax({url:self.URL_ACCOUNTS, type:'GET', dataType:'json'});
    this.xhract.done(function(data, textStatus, jqXHR) {
      var html = pk.templates.accounts_list(data);
      self.accounts.html(html);
    });
  },

  update_categories: function(callback) {
    var self = this;
    self.show_categories();
    try { this.xhrcat.abort(); } catch(err) { }
    this.xhrcat = $.ajax({url:self.URL_CATEGORIES, type:'GET', dataType:'json'});
    this.xhrcat.done(function(data, textStatus, jqXHR) {
      var html = pk.templates.category_list(data);
      self.categories.html(html);
      self.update_category_trends();
      self.update_category_choices(data);
      self.bind_drag_categories();
      if (callback) { callback(); }
    });
  },

  update_category_trends: function() {
    var self = this;
    // Wait for self.summary_data to be populated
    if (self.summary_data === null) {
      return setTimeout(function() { self.update_category_trends(); }, 100);
    }
    // update trend charts
    for (var i in self.summary_data.categories) {
      var summary = self.summary_data.categories[i];
      var selector = self.categories.find('tbody tr[data-id='+ summary.categoryid +'] td[data-name=trend]');
      var data = Object.values(summary.amounts).map(function(x) {
        var mult = summary.name == 'Income' ? 1 : -1;
        return Math.max(x * mult, 0);
      });
      var chart = pk.charts.budget_trend(data);
      selector.highcharts(chart);
    };
  },

  update_category_choices: function(data) {
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
    var self = this;
    self.show_summary();
    try { this.xhrtrx.abort(); } catch(err) { }
    this.xhrtrx = $.ajax({url:self.URL_SUMMARY, type:'GET', dataType:'json'});
    this.xhrtrx.done(function(data, textStatus, jqXHR) {
      self.summary_data = data;
      self.searchinfo.text('');
      var html = pk.templates.summary(data);
      self.summary.html(html);
    });
  },

  update_transactions: function(page) {
    var self = this;
    self.params.search = this.searchinput.val();
    self.show_transactions();
    if (!page) {
      self.trxpage = null;
      var more = null;
      var url = pk.utils.update_url(self.URL_TRANSACTIONS, {search:self.params.search});
    } else {
      var more = this.transactions.find('#loadmore');
      var url = more.data('next');
      more.addClass('on');
    }
    if (self.trxpage != url) {
      self.trxpage = url;
      try { this.xhrtrx.abort(); } catch(err) { }
      this.xhrtrx = $.ajax({url:url, type:'GET', dataType:'json'});
      this.xhrtrx.done(function(data, textStatus, jqXHR) {
        if (more) { more.remove(); }
        self.searchinfo.text(data.errors || data.datefilters);
        var html = pk.templates.transaction_list(data);
        if (data.previous) {
          var items = $(html).find(self.ROW);
          self.transactions.find('tbody').append(items);
        } else {
          self.transactions.html(html);
        }
      });
    }
  },

};
