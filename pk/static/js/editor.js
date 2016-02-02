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


// pk.editor = {
//   UPDATE_INTERVAL: 500,
//   MESSAGE_SAVED: '<i class="icon-checkmark"></i>&nbsp;Saved',
//   MESSAGE_ERROR: '<i class="icon-notification"></i>&nbsp;Error',
//   MESSAGE_DELETED: '<i class="icon-checkmark"></i>&nbsp;Deleted',
//   KEYS: {S:83, F2:113},
// 
//   init: function(selector, opts) {
//     this.container = $(selector);
//     this.opts = $.extend(true, {}, this.defaults, opts);
//     if (this.container.length === 0) { return; }
//     console.debug('init pk.editor: '+ selector);
//     this.menu = this.container.find('.editor-menu');
//     this.footer = this.container.find('.editor-footer');
//     this.spinner = this.container.find('.editor-spinner');
//     this.message = this.container.find('.editor-message');
//     this.includes = this.container.find('.editor-includes');
//     this.codemirror = this.init_codemirror();
//     this.title = this.container.find('[name=title]');
//     this.tags = this.container.find('[name=tags]');
//     this.last_updated_data = this.data();
//     this.last_saved_data = this.last_updated_data;
//     this.init_triggers();
//     this.init_shortcuts();
//     this.resize_editor();
//   },
// 
//   init_codemirror: function() {
//     var textarea = this.container.find('textarea').get(0);
//     var opts = $.extend({}, this.defaults.codemirror, this.opts.codemirror);
//     return CodeMirror.fromTextArea(textarea, this.opts.codemirror);
//   },
// 
//   init_triggers: function() {
//     var self = this;
//     // toggle editing mode
//     $('.editor-toggle').on('click', function(event) {
//       event.preventDefault();
//       self.toggle_editor();
//     });
//     // reset to last saved state
//     this.menu.find('.editor-reset').on('click', function(event) {
//       event.preventDefault();
//       self.reset();
//     });
//     // save current text
//     this.menu.find('.editor-save').on('click', function(event) {
//       event.preventDefault();
//       self.save();
//     });
//     // delete current entry
//     this.menu.find('.editor-delete').on('click', function(event) {
//       event.preventDefault();
//       self.delete();
//     });
//     // update content timer
//     if (this.opts.output) {
//       setInterval(function() { self.update(); }, this.UPDATE_INTERVAL);
//     }
//     // window resize
//     $(window).on('resize', function(event) {
//       self.resize_editor();
//     });
//   },
// 
//   init_shortcuts: function() {
//     var self = this;
//     var KEYS = this.KEYS;
//     $(document).on('keydown', function(event) {
//       var ctrl = navigator.platform.match('Mac') ? event.metaKey : event.ctrlKey;
//       if (ctrl && event.keyCode == KEYS.S && self.editing()) {
//         event.preventDefault();
//         self.save();
//       } else if (event.keyCode == KEYS.F2) {
//         event.preventDefault();
//         self.toggle_editor();
//       }
//     });
//   },
// 
//   data: function() {
//     return {
//       'id': this.opts.id,
//       'title': this.title.val(),
//       'slug': _.trim(window.location.pathname, '/').split('/').reverse()[0] || 'root',
//       'body': this.codemirror.getValue(),
//       'tags': this.tags.val(),
//     };
//   },
//   
//   delete: function() {
//     var self = this;
//     this.spinner.addClass('on');
//     var url = this.opts.id ? this.opts.apiroot + this.opts.id +'/' : this.opts.apiroot;
//     var xhr = $.ajax({url:url, type:'DELETE', dataType:'json'});
//     xhr.done(function(data, textStatus, jqXHR) {
//       self.opts.id = '';
//       self.codemirror.setValue('');
//       self.title.val('');
//       self.tags.val('');
//       self.show_message(self.MESSAGE_DELETED);
//     });
//     xhr.fail(function(jqXHR, textStatus, errorThrown) {
//       self.show_message(self.MESSAGE_ERROR);
//     });
//     xhr.always(function() {
//       self.spinner.removeClass('on');
//     });
//   },
// 
//   editing: function() {
//     return $('body').hasClass('editing');
//   },
// 
//   reset: function() {
//     this.codemirror.setValue(this.last_saved_data.body);
//     this.title.val(this.last_saved_data.title);
//     this.tags.val(this.last_saved_data.tags);
//   },
// 
//   resize_editor: function() {
//     return;
//   },
// 
//   save: function() {
//     var self = this;
//     this.spinner.addClass('on');
//     var data = this.data();
//     var method = this.opts.id ? 'PUT' : 'POST';
//     var url = this.opts.id ? this.opts.apiroot + this.opts.id +'/' : this.opts.apiroot;
//     var xhr = $.ajax({url:url, type:method, data:data, dataType:'json'});
//     xhr.done(function(data, textStatus, jqXHR) {
//       self.opts.id = data.id || '';
//       self.last_saved_data = data;
//       window.history.replaceState('','',data.weburl);
//       self.show_message(self.MESSAGE_SAVED);
//     });
//     xhr.fail(function(jqXHR, textStatus, errorThrown) {
//       self.show_message(self.MESSAGE_ERROR);
//     });
//     xhr.always(function() {
//       self.spinner.removeClass('on');
//     });
//   },
// 
//   show_message: function(msg) {
//     var self = this;
//     this.message.html(msg);
//     this.message.css('opacity', 1);
//     setTimeout(function() { self.message.css('opacity', 0); }, 5000);
//   },
// 
//   toggle_editor: function(enable) {
//     var self = this;
//     if (enable === false || (enable === undefined && self.editing())) {
//       $('body').removeClass('editing');
//       Cookies.set('editing', '');
//     } else {
//       $('body').addClass('editing');
//       setTimeout(function() { self.codemirror.refresh(); }, 100);
//       setTimeout(function() { self.codemirror.refresh(); }, 600);
//       Cookies.set('editing', '1');
//     }
//     self.resize_editor();
//   },
// 
//   update: function() {
//     var self = this;
//     var data = this.data();
//     if (!self.editing() || _.isEqual(data, this.last_updated_data)) {
//       return null;  // nothing to update
//     }
//     var xhr = $.ajax({url:'/markdown/', data:data, type:'POST', dataType:'json'});
//     xhr.done(function(data, textStatus, jqXHR) {
//       if ((self.opts.output) && (self.opts.scrollbottom)) {
//         var pxtobottom = $(window).scrollBottom();
//         $(self.opts.output).html(data.html);
//         pk.utils.highlightjs();
//         $(window).scrollBottom(pxtobottom);
//       } else if (self.opts.output) {
//         $(self.opts.output).html(data.html);
//       }
//       self.update_includes(data.includes);
//       self.resize_editor();
//     });
//     xhr.always(function() {
//       self.last_updated_data = data;
//     });
//   },
// 
//   update_includes: function(includes) {
//     if (includes === undefined) { return; }
//     var html = [];
//     $.each(includes, function(i, slug) {
//       html.push('<a href="/p/'+ slug +'">'+ slug +'</a>');
//     });
//     if (html.length) { this.includes.html('Includes: '+ html.join(', ')); }
//     else { this.includes.html(''); }
//   },
// 
//   defaults: {
//     id: null,                   // (required) current object id
//     apiroot: null,              // (required) pages or notes
//     output: null,               // (required) selector for markdown output
//     callback_resize: null,      // callback to resize editor
//     scrollbottom: false,        // Set true when update is above editor
//     codemirror: {               // default codemirror opts
//       extraKeys: {'Enter': 'newlineAndIndentContinueMarkdownList'},
//       htmlMode: true,
//       keyMap: 'sublime',
//       lineNumbers: false,
//       lineWrapping: false,
//       matchBrackets: true,
//       mode: 'gfm',
//       scrollbarStyle: 'simple',
//       tabSize: 2,
//       theme: 'blackboard',
//     },
//   },
// };
