/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

pk.notebook = {
  APIROOT: '/api/notes/',
  EDITOR_SELECTOR: '#notebook-editor',
  NOTE_SELECTOR: '#note',
  KEYS: {TAB:9, ENTER:13, ESC:27, UP:38, DOWN:40},
  
  init: function(selector, editor) {
    console.debug('init pk.notebook: '+ selector);
    this.container = $(selector);
    this.editor = editor;
    this.xhr = null;
    this.search = null;
    this.init_elements();
    this.init_triggers();
    this.init_shortcuts();
    this.update_list(this.searchinput.val());
  },
  
  init_elements: function() {
    this.sidepanel = this.container.find('#notebook-sidepanel');
    this.searchinput = this.container.find('#notebook-search');
    this.addnote = this.container.find('#notebook-add');
    this.notelist = this.container.find('#notebook-list');
  },
  
  init_triggers: function() {
    var self = this;
    // search input changes
    this.searchinput.on('change paste keyup', function(event) {
      if (_.valuesIn(this.KEYS).indexOf(event.keyCode) == -1) {
        event.preventDefault();
        var search = $(this).val();
        self.update_list(search);
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
    $(window).on('keydown', function(event) {
      var noteitems = self.notelist.find('.notebook-item');
      var focused = self.searchinput.is(':focus');
      if (focused && (_.valuesIn(KEYS).indexOf(event.keyCode) > -1)) {
        event.preventDefault();
        var selected = noteitems.filter('.selected');
        if ((event.keyCode == KEYS.DOWN) || (event.keyCode == KEYS.TAB)) {
          var next = selected.next();
          next = next.length ? next : noteitems.filter(':first-child');
          noteitems.removeClass('selected');
          next.addClass('selected');
        } else if (event.keyCode == KEYS.UP) {
          var prev = selected.prev().filter('.notebook-item');
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
    this.editor.toggle_editor(true);
    this.editor.history.saved = {};
    this.editor.codemirror.setValue('');
    this.editor.title.val('');
    this.editor.tags.val('');
    window.history.replaceState('','','/n/');
  },
  
  update_list: function(search) {
    var self = this;
    if (search == this.search) { return; }
    if (this.xhr) { this.xhr.abort(); }
    var url = search ? this.APIROOT +'?search='+ encodeURIComponent(search) : this.APIROOT;
    this.xhr = $.ajax({url:url, type:'GET', dataType:'json'});
    this.xhr.done(function(data, textStatus, jqXHR) {
      var ctx = {items:data, search:encodeURIComponent(search)};
      var html = self.templates.listitems(ctx);
      self.container.find('#notebook-list').html(html);
      self.search = search;
    });
  },
  
  templates: {
    listitems: Handlebars.compile([
      '{{#each this.items}}',
      '  <a class="notebook-item" href="{{this.weburl}}{{#if ../search}}?search={{../search}}{{/if}}" data-url="{{this.url}}">',
      '    <div class="title">{{this.title}}</div>',
      '    <div class="subtext">',
      '      {{this.tags}} - {{formatDate this.created "%Y-%m-%d"}}',
      '    </div>',
      '  </a>',
      '{{/each}}',
    ].join('\n')),
  },

};
