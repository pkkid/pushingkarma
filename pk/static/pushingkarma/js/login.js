/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

pk.login = {
  logo: $('#logo'),
  form: $('#logo form'),
  login_url: '/api/account/0/login/',
  logout_url: '/api/account/0/logout/',
  KEYS: {F2:113},

  init: function() {
    console.debug('init pk.login on #'+ this.logo.attr('id'));
    this.init_triggers();
    this.init_shortcuts();
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

  init_shortcuts: function() {
    var self = this;
    var KEYS = this.KEYS;
    $(document).on('keydown', function(event) {
      if ((event.keyCode == KEYS.F2) && (!$('body').hasClass('authenticated'))) {
        event.preventDefault();
        event.stopPropagation();
        self.show_form();
      }
    });
  },

  show_form: function() {
    if (this.logo.hasClass('enabled')) {
      return null;
    }
    this.logo.addClass('enabled');
    this.form.find('input[name=email]').val('').focus();
    this.form.find('input[name=password]').val('');
  },

  hide_form: function() {
    this.logo.removeClass('enabled');
    this.form.removeClass('error');
  },

  login: function() {
    var self = this;
    var data = self.form.serializeArray();
    var xhr = $.ajax({url:self.login_url, data:data, type:'POST', dataType:'json'});
    self.form.removeClass('error');
    xhr.done(function(data, textStatus, jqXHR) {
      self.form.animatecss('rubberBand', function() {
        location.reload();
      });
    });
    xhr.fail(function(jqXHR, textStatus, errorThrown) {
      self.form.animatecss('shake');
      self.form.addClass('error');
    });
  },
};
