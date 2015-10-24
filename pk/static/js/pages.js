/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

pk.pages = {
    LAYOUT_WIDTH: 1000,         // from _layout.scss
    EDITOR_WIDTH: 550,          // from _pages.scss
    HANDLE_WIDTH: 8,            // from _pages.scss
    UPDATE_INTERVAL: 1500,

    init: function() {
        this.editor = $('#page-editor');
        this.menu = this.editor.find('.menu');
        this.spinner = this.menu.find('.spinner');
        this.message = this.menu.find('.message');
        this.included = this.editor.find('.item.includes');
        this.codemirror = this.init_codemirror();
        this.last_updated_text = this.codemirror.getValue();
        this.last_saved_text = this.last_updated_text;
        this.init_triggers();
        this.init_shortcuts();
        this.resize_editor();
    },

    init_codemirror: function() {
        var textarea = $('#page-textarea').get(0);
        return CodeMirror.fromTextArea(textarea, {
            extraKeys: {'Enter': 'newlineAndIndentContinueMarkdownList'},
            htmlMode: true,
            lineNumbers: false,
            lineWrapping: false,
            matchBrackets: true,
            mode: 'xml',
            scrollbarStyle: 'simple',
            theme: 'blackboard',
        });
    },

    init_triggers: function() {
        var self = this;
        // toggle editor visibility
        this.editor.find('.handle').on('click', function(event) {
            event.preventDefault();
            self.toggle_editor();
        });
        // reset to last saved state
        this.menu.find('.reset').on('click', function(event) {
            event.preventDefault();
            self.reset();
        });
        // save current text
        this.menu.find('.save').on('click', function(event) {
            event.preventDefault();
            self.save();
        });
        // constantly update content
        setInterval(function() { self.update(); }, this.UPDATE_INTERVAL);
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
        // set editor window width
        if (this.editing()) {
            var editorwidth = Math.max(500, Math.min(800, $(window).width() - this.LAYOUT_WIDTH - 60));
            var layoutwidth = this.LAYOUT_WIDTH + editorwidth + (this.HANDLE_WIDTH * 2);
            $('#layoutwrap').css({width: layoutwidth +'px'});
            $('#page-editor').css({width: editorwidth +'px'});
        } else {
            $('#layoutwrap').attr('style', '');
            $('#page-editor').attr('style', '');
        }
        // always set editor height
        var editorheight = $('#page').height();
        this.editor.css({height: editorheight +'px'});
    },

    save: function() {
        var self = this;
        this.spinner.addClass('on');
        var text = this.codemirror.getValue();
        var xhr = pk.utils.ajax(window.location.pathname, {'text':text});
        xhr.done(function(data, textStatus, jqXHR) {
            self.last_saved_text = text;
            self.show_message('<i class="icomoon-checkmark"></i>&nbsp;Saved');
        });
        xhr.fail(function(jqXHR, textStatus, errorThrown) {
            self.show_message('<i class="icomoon-notification"></i>&nbsp; Error');
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
            self.update_included(data.included);
            self.resize_editor();
        });
        xhr.always(function() {
            self.last_updated_text = text;
        });
    },

    update_included: function(included) {
        var html = [];
        $.each(included, function(i, slug) {
            html.push('<a href="/p/'+ slug +'">'+ slug +'</a>');
        });
        if (html.length) { this.included.html('Included: '+ html.join(', ')); }
        else { this.included.html(''); }
    },

};
