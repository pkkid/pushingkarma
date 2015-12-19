/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

pk.notebook = {
    APIROOT: '/api/notes/',
    EDITOR_SELECTOR: '#notebook-editor',
    NOTE_SELECTOR: '#note',

    init: function(selector, noteid) {
        this.container = $(selector);
        console.debug('init pk.notebook: '+ selector);
        this.input = this.container.find('#notebook-filter');
        this.xhr = null;
        this.init_editor(noteid);
        this.init_triggers();
        this.update_list();
    },
    
    init_triggers: function() {
        var self = this;
        // search input changes
        this.input.on('change paste keyup', function(event) {
            event.preventDefault();
            var search = $(this).val();
            if (search.length === 0) { self.update_list(); }
            else if (search.length >= 3) { self.update_list(search); }
        });
    },

    init_editor: function(noteid) {
        pk.editor.init(this.EDITOR_SELECTOR, {
            id: noteid,
            apiroot: this.APIROOT,
            output: this.NOTE_SELECTOR,
            scrollbottom: true,
        });
    },
    
    update_list: function(search) {
        var self = this;
        if (this.xhr) { this.xhr.abort(); }
        var url = search ? this.APIROOT +'?search='+ encodeURIComponent(search) : this.APIROOT;
        this.xhr = $.ajax({url:url, type:'GET', dataType:'json'});
        this.xhr.done(function(data, textStatus, jqXHR) {
            var html = self.templates.listitems(data);
            self.container.find('#notebook-list').html(html);
        });
        // this.xhr.always(function() {
        //     console.log('..always');
        // });
    },
    
    templates: {
        listitems: Handlebars.compile([
            '{{#each this}}',
            '  <div class="notebook-item">',
            '    <div class="title">{{this.title}}</div>',
            '    <div class="subtext">{{this.tags}} - {{formatDate this.created "%Y-%m-%d"}}</div>',
            '  </div>',
            '{{/each}}',
        ].join('\n')),
    },

};
