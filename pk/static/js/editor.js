/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

pk.editor = {
    UPDATE_INTERVAL: 1500,
    
    init: function(selector, opts) {
        this.container = $(selector);
        this.opts = $.extend({}, this.defaults, opts);
        if (this.container.length === 0) { return; }
        console.debug('init pk.editor: '+ selector);
        this.menu = this.container.find('.editor-menu');
        this.footer = this.container.find('.editor-footer');
        this.spinner = this.container.find('.editor-spinner');
        this.message = this.container.find('.editor-message');
        this.includes = this.container.find('.editor-includes');
        this.codemirror = this.init_codemirror();
        this.last_updated_text = this.codemirror.getValue();
        this.last_saved_text = this.last_updated_text;
        this.init_triggers();
        this.init_shortcuts();
        this.resize_editor();
    },

    init_codemirror: function() {
        var textarea = this.container.find('textarea').get(0);
        var opts = $.extend({}, this.defaults.codemirror, this.opts.codemirror);
        return CodeMirror.fromTextArea(textarea, this.opts.codemirror);
    },

    init_triggers: function() {
        var self = this;
        // toggle editing mode
        this.container.find('.editor-toggle').on('click', function(event) {
            event.preventDefault();
            self.toggle_editor();
        });
        // reset to last saved state
        this.menu.find('.editor-reset').on('click', function(event) {
            event.preventDefault();
            self.reset();
        });
        // save current text
        this.menu.find('.editor-save').on('click', function(event) {
            event.preventDefault();
            self.save();
        });
        // update content timer
        setInterval(function() {
            self.update();
        }, this.UPDATE_INTERVAL);
        // window resize
        $(window).on('resize', function(event) {
            self.resize_editor();
        });
    },

    init_shortcuts: function() {
        var self = this;
        document.addEventListener('keydown', function(event) {
            var ctrl = navigator.platform.match('Mac') ? event.metaKey : event.ctrlKey;
            var s = event.keyCode == 83;
            var f2 = event.keyCode == 113;
            if (ctrl && s && self.editing()) {
                event.preventDefault();
                self.save();
            } else if (f2) {
                event.preventDefault();
                self.toggle_editor();
            }
        }, false);
    },

    editing: function() {
        return $('body').hasClass('editing');
    },

    reset: function() {
        this.codemirror.setValue(this.last_saved_text);
    },

    resize_editor: function() {
        return;
    },

    save: function() {
        var self = this;
        this.spinner.addClass('on');
        var text = this.codemirror.getValue();
        var xhr = pk.utils.ajax(window.location.pathname, {'text':text});
        xhr.done(function(data, textStatus, jqXHR) {
            self.last_saved_text = text;
            self.show_message('<i class="icon-checkmark"></i>&nbsp;Saved');
        });
        xhr.fail(function(jqXHR, textStatus, errorThrown) {
            self.show_message('<i class="icon-notification"></i>&nbsp; Error');
        });
    },

    show_message: function(msg) {
        var self = this;
        this.spinner.removeClass('on');
        this.message.html(msg);
        this.message.css('opacity', 1);
        setTimeout(function() { self.message.css('opacity', 0); }, 5000);
    },

    toggle_editor: function() {
        var self = this;
        if (self.editing()) {
            $('body').removeClass('editing');
            Cookies.set('editing', '');
        } else {
            $('body').addClass('editing');
            setTimeout(function() { self.codemirror.refresh(); }, 100);
            setTimeout(function() { self.codemirror.refresh(); }, 600);
            Cookies.set('editing', '1');
        }
        self.resize_editor();
    },

    update: function() {
        var self = this;
        var text = this.codemirror.getValue();
        if (!self.editing() || (text == this.last_updated_text))
            return null;  // nothing to update
        var xhr = pk.utils.ajax('/markdown/', {'text':text});
        xhr.done(function(data, textStatus, jqXHR) {
            $('#page').html(data.html);
            self.update_includes(data.includes);
            self.resize_editor();
        });
        xhr.always(function() {
            self.last_updated_text = text;
        });
    },

    update_includes: function(includes) {
        var html = [];
        $.each(includes, function(i, slug) {
            html.push('<a href="/p/'+ slug +'">'+ slug +'</a>');
        });
        if (html.length) { this.includes.html('Included: '+ html.join(', ')); }
        else { this.includes.html(''); }
    },

    defaults: {
        url_save: null,                     // url to save contents
        url_markdown: '/markdown/',         // url converts markdown to html
        callback_resize: null,              // callback to resize editor
        codemirror: {                       // default codemirror opts
            extraKeys: {'Enter': 'newlineAndIndentContinueMarkdownList'},
            htmlMode: true,
            lineNumbers: false,
            lineWrapping: false,
            matchBrackets: true,
            mode: 'xml',
            scrollbarStyle: 'simple',
            theme: 'blackboard',
        },
    },

};