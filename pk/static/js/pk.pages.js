/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

pk.pages = {

    init: function() {
        this.editor = $('#page-editor');
        this.codemirror = this.init_codemirror();
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
        setInterval(function() {
            var data = {'markdown': self.codemirror.getValue()};
            var xhr = $.ajax({url:'/markdown/', method:'post', dataType:'json', data:data});
            xhr.done(function(data, textStatus, jqXHR) {
                console.log(data);
                $('#page').html(data.html);
            });
        }, 2000);
    },

};
