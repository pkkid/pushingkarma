/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

pk.login = {
    logo: $('#logo'),
    form: $('#logo form'),
    login_url: '/auth/login/',
    logout_url: '/auth/logout/',

    init: function() {
        console.log('init_login_form');
        this.init_triggers();
    },

    init_triggers: function() {
        var self = this;
        // Display login form
        self.logo.on('click', function(event) {
            event.stopPropagation();
            self.show_form();
        }).children().on('click', function(event) {
            event.stopPropagation();
        });
        // Hide login form
        $('header').on('click', function(event) {
            event.preventDefault();
            self.hide_form();
        });
        // Submit login form
        self.form.on('submit', function(event) {
            event.preventDefault();
            event.stopPropagation();
            self.login();
        });
    },

    show_form: function() {
        if (this.logo.hasClass('enabled'))
            return null;
        this.logo.addClass('enabled');
        this.form.find('input[name=username]').val('').focus();
        this.form.find('input[name=password]').val('');
    },

    hide_form: function() {
        this.logo.removeClass('enabled');
        this.form.removeClass('error');
    },

    login: function() {
        var self = this;
        var data = self.form.serializeArray();
        var xhr = pk.utils.ajax(self.login_url, data);
        self.form.removeClass('error');
        xhr.done(function(data, textStatus, jqXHR) {
            self.form.animatecss('tada', function() {
                location.reload();
            });
        });
        xhr.fail(function(jqXHR, textStatus, errorThrown) {
            self.form.animatecss('shake');
            self.form.addClass('error');
        });
    },

};
