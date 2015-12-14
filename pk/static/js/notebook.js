/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

pk.notebook = {
    EDITOR_SELECTOR: '#notebook-editor',
    NOTE_SELECTOR: '#note',

    init: function(selector, noteid) {
        this.container = $(selector);
        console.debug('init pk.notebook: '+ selector);
        this.init_editor(noteid);
    },

    init_editor: function(noteid) {
        pk.editor.init(this.EDITOR_SELECTOR, {
            id: noteid,
            apiroot: '/api/notes/',
            output: this.NOTE_SELECTOR,
            scrollbottom: true,
        });
    },

};
