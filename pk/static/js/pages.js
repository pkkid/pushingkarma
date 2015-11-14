/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

pk.pages = $.extend({}, pk.editor, {
    LAYOUT_WIDTH: 1000,         // from _layout.scss
    HANDLE_WIDTH: 8,            // from _pages.scss

    resize_editor: function() {
        if (this.editing()) {
            var editorwidth = Math.max(500, Math.min(800, $(window).width() - this.LAYOUT_WIDTH - 60));
            var layoutwidth = this.LAYOUT_WIDTH + editorwidth + (this.HANDLE_WIDTH * 2);
            $('#layoutwrap').css({width: layoutwidth +'px'});
            $('#pages-editor').css({width: editorwidth +'px'});
        } else {
            $('#layoutwrap').attr('style', '');
            $('#pages-editor').attr('style', '');
        }
    },

});
