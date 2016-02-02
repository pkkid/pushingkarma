/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

pk.editor = {
  UPDATE_INTERVAL: 500,
  MESSAGE_SAVED: '<i class="icon-checkmark"></i>&nbsp;Saved',
  MESSAGE_ERROR: '<i class="icon-notification"></i>&nbsp;Error',
  MESSAGE_DELETED: '<i class="icon-checkmark"></i>&nbsp;Deleted',
  MIN_HEIGHT: 135,
  ONE_HOUR: 0.042,
  KEYS: {S:83, F2:113},
  
  init: function(selector, opts) {
    console.debug('init pk.editor2: '+ selector);
    this.container = $(selector);
    this.opts = $.extend(true, {}, this.defaults, opts);
    this.editor = this.init_editor();
    this.codemirror = this.init_codemirror();
    this.history = {updated:null, saved:null};
    this.init_elements();
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
    this.editor = $(this.templates.editor(this)).appendTo('body');
    this.set_height(Cookies.get('editor-height') || 300);
    return this.editor;
  },
  
  init_codemirror: function() {
    var textarea = this.editor.find('textarea').get(0);
    return CodeMirror.fromTextArea(textarea, this.opts.codemirror);
  },
  
  init_triggers: function() {
    var self = this;
    $('.CodeMirror-scroll').disableParentScroll();
    $('#editor .slider').on('mousedown', function(event) { event.preventDefault(); self.resize(event); });
    $('#editor .reset').on('click', function(event) { event.preventDefault(); self.reset(); });
    $('#editor .save').on('click', function(event) { event.preventDefault(); self.save(); });
    $('#editor .delete').on('dblclick', function(event) { event.preventDefault(); self.delete(); });
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
    var url = this.history.saved.url || this.opts.api_url;
    this.request('DELETE', url, function(data) {
      self.history.saved = {};
      self.codemirror.setValue('');
      self.title.val('');
      self.tags.val('');
      self.notify(self.MESSAGE_DELETED);
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
      $('body').unbind('mousemove', drag);
      $('body').unbind('mouseup', stopdrag);
    };
    $('body').bind('mousemove', drag);
    $('body').bind('mouseup', stopdrag);
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
    Cookies.set('editor-height', height, this.ONE_HOUR);
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
    enable = enable ? enable : !this.editing();
    if (enable) {
      // show the editor and set the body margin. We set the body margin early
      // so the body scrollbar displays before the animation starts.
      this.editor.show();
      $('body').css('margin-bottom', self.editor.height());
      this.editor.animatecss('bounceInUp', function() {
        self.set_height(self.editor.height());
        self.codemirror.refresh();
        self.codemirror.focus();
        Cookies.set('editing', '1', self.ONE_HOUR);
      });
    } else {
      this.editor.animatecss('bounceOutDown', function() {
        self.editor.hide();
        $('body').css('margin-bottom', 0);
        Cookies.set('editing', '');
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
      tabSize: 2,
      theme: 'blackboard',
    },
  },
  
  templates: {
    editor: Handlebars.compile([
      '<div id="editor" style="display:none;">',
      '  <div class="slider"><div class="grip"></div></div>',
      '  <div class="menu">',
      '    <span class="menutitle">Markdown Editor</span>',
      '    <span class="reset action">Reset</span>',
      '    <span class="save action">Save</span>',
      '    <span class="delete action"><i class="icon-bin"></i></span>',
      '    <span class="spinner"></span>',
      '    <span class="message"></span>',
      '  </div>',
      '  {{#if this.opts.show_title}}<input type="text" name="title" class="title" placeholder="Title" autocomplete="off" value=""/>{{/if}}',
      '  <textarea style="display:none;"></textarea>',
      '  {{#if this.opts.show_includes}}<div class="includes">Includes: </div>{{/if}}',
      '  {{#if this.opts.show_tags}}<input type="text" name="tags" class="tags" placeholder="Tags" autocomplete="off" value=""/>{{/if}}',
      '</div>',
    ].join('\n')),
  },
  
};
