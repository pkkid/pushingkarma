/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

pk.notebook = {
    EDITOR_SELECTOR: '#notebook-editor',
    NOTE_SELECTOR: '#note',

    init: function(selector) {
        this.container = $(selector);
        console.debug('init pk.notebook: '+ selector);
        this.init_editor();
    },

    init_editor: function() {
        pk.editor.init(this.EDITOR_SELECTOR, {
            output: this.NOTE_SELECTOR,
            scrollbottom: true,
        });
    },

};
