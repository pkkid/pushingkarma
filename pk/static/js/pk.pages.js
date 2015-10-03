/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

pk.pages = {

    init: function() {
        this.editor = $('#page-editor');
        this.codemirror = this.init_codemirror();
        this.last_updated_text = this.codemirror.getValue();
        this.init_triggers();
    },

    init_codemirror: function() {
        var textarea = $('#page-textarea').get(0);
        return CodeMirror.fromTextArea(textarea, {
            extraKeys: {'Enter': 'newlineAndIndentContinueMarkdownList'},
            lineNumbers: false,
            lineWrapping: true,
            matchBrackets: true,
            mode: 'gfm',
            scrollbarStyle: 'simple',
            theme: 'blackboard',
        });
    },

    init_triggers: function() {
        var self = this;
        // Toggle editor visibility
        this.editor.find('.handle').on('click', function() {
            $('body').toggleClass('editing');
            setTimeout(function() { self.codemirror.refresh(); }, 100);
        });
        // Constantly update content
        setInterval(function() { self.update(); }, 1500);
    },

    update: function() {
        var self = this;
        var editing = $('body').hasClass('editing');
        var text = this.codemirror.getValue();
        if (!editing || (text == this.last_updated_text))
            return null;  // Nothing to update
        var data = {'text': text};
        var xhr = $.ajax({url:'/markdown/', method:'post', dataType:'json', data:data});
        xhr.done(function(data, textStatus, jqXHR) {
            self.last_updated_text = text;
            $('#page').html(data.html);
        });
    },

};
