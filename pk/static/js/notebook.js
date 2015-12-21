/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

pk.notebook = {
    APIROOT: '/api/notes/',
    EDITOR_SELECTOR: '#notebook-editor',
    NOTE_SELECTOR: '#note',
    
    KEY_ENTER: 13,
    KEY_ESC: 27,
    KEY_UP: 38,
    KEY_DOWN: 40,
    
    init: function(selector, noteid) {
        this.container = $(selector);
        console.debug('init pk.notebook: '+ selector);
        this.sidepanel = this.container.find('#notebook-sidepanel');
        this.searchinput = this.container.find('#notebook-search');
        this.addnote = this.container.find('#notebook-add');
        this.notelist = this.container.find('#notebook-list');
        this.xhr = null;
        this.last_searched = '__init__';
        this.init_editor(noteid);
        this.init_triggers();
        this.update_list();
    },
    
    init_triggers: function() {
        var self = this;
        var keycodes = [this.KEY_ENTER, this.KEY_ESC, this.KEY_UP, this.KEY_DOWN];
        // search input changes
        this.searchinput.on('change paste keyup', function(event) {
            if (keycodes.indexOf(event.keyCode) == -1) {
                event.preventDefault();
                var search = $(this).val();
                if (search.length === 0) { self.update_list(); }
                else if (search.length >= 3) { self.update_list(search); }
            }
        });
        // start a new note
        this.addnote.on('click', function() {
            event.preventDefault();
            self.setup_new_note();
        });
        // select noteitems via keyboard
        $(window).on('keydown', function(event) {
            var noteitems = self.notelist.find('.notebook-item');
            var focused = self.searchinput.is(':focus');
            if(focused && (keycodes.indexOf(event.keyCode) > -1)) {
                event.preventDefault();
                var selected = noteitems.filter('.selected');
                if (event.keyCode == self.KEY_DOWN) {
                    var next = selected.next();
                    next = next.length ? next : noteitems.filter(':first-child');
                    noteitems.removeClass('selected');
                    next.addClass('selected');
                } else if (event.keyCode == self.KEY_UP) {
                    var prev = selected.prev().filter('.notebook-item');
                    prev = prev.length ? prev : noteitems.filter(':last-child');
                    noteitems.removeClass('selected');
                    prev.addClass('selected');
                } else if ((event.keyCode == self.KEY_ENTER) && (selected.length)) {
                    window.top.location = selected.attr('href');
                } else if (event.keyCode == self.KEY_ESC) {
                    noteitems.removeClass('selected');
                }
            }
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
    
    setup_new_note: function() {
        console.log('Setup New Note!');
    },
    
    update_list: function(search) {
        var self = this;
        if (search == this.last_searched) { return; }
        if (this.xhr) { this.xhr.abort(); }
        var url = search ? this.APIROOT +'?search='+ encodeURIComponent(search) : this.APIROOT;
        this.xhr = $.ajax({url:url, type:'GET', dataType:'json'});
        this.xhr.done(function(data, textStatus, jqXHR) {
            var html = self.templates.listitems(data);
            self.container.find('#notebook-list').html(html);
            self.last_searched = search;
        });
    },
    
    templates: {
        listitems: Handlebars.compile([
            '{{#each this}}',
            '  <a class="notebook-item" href="{{this.weburl}}" data-url="{{this.url}}">',
            '    <div class="title">{{this.title}}</div>',
            '    <div class="subtext">{{this.tags}} - {{formatDate this.created "%Y-%m-%d"}}</div>',
            '  </a>',
            '{{/each}}',
        ].join('\n')),
    },

};
