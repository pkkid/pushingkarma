/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

pk.pages = {
    UPDATE_INTERVAL: 1500,

    init: function() {
        this.editor = $('#page-editor');
        this.menu = this.editor.find('.menu');
        this.spinner = this.menu.find('.spinner');
        this.message = this.menu.find('.message');
        this.codemirror = this.init_codemirror();
        this.last_updated_text = this.codemirror.getValue();
        this.last_saved_text = this.last_updated_text;
        this.init_triggers();
        this.init_shortcuts();
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
        // Toggle editor visibility
        this.editor.find('.handle').on('click', function(event) {
            event.preventDefault();
            self.toggle_editor();
        });
        // Reset to last saved state
        this.menu.find('.reset').on('click', function(event) {
            event.preventDefault();
            self.reset();
        });
        // Save current text
        this.menu.find('.save').on('click', function(event) {
            event.preventDefault();
            self.save();
        });
        // Constantly update content
        setInterval(function() { self.update(); }, this.UPDATE_INTERVAL);
    },

    init_shortcuts: function() {
        var self = this;
        document.addEventListener('keydown', function(event) {
            var ctrl = navigator.platform.match('Mac') ? event.metaKey : event.ctrlKey;
            var s = event.keyCode == 83;
            var f2 = event.keyCode == 113;
            var editing = $('body').hasClass('editing');
            if (ctrl && s && editing) {
                event.preventDefault();
                self.save();
            } else if (f2) {
                event.preventDefault();
                self.toggle_editor();
            }
        }, false);
    },

    toggle_editor: function() {
        var self = this;
        if ($('body').hasClass('editing')) {
            $('body').removeClass('editing');
        } else {
            $('body').addClass('editing');
            setTimeout(function() { self.codemirror.refresh(); }, 100);
            setTimeout(function() { self.codemirror.refresh(); }, 600);
        }
    },

    update: function() {
        var self = this;
        var editing = $('body').hasClass('editing');
        var text = this.codemirror.getValue();
        if (!editing || (text == this.last_updated_text))
            return null;  // nothing to update
        var xhr = pk.utils.ajax('/markdown/', {'text':text});
        xhr.done(function(data, textStatus, jqXHR) {
            $('#page').html(data.html);
        });
        xhr.always(function() {
            self.last_updated_text = text;
        });
    },

    reset: function() {
        this.codemirror.setValue(this.last_saved_text);
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

};
