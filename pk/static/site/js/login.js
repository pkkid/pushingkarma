// Encoding: UTF-8
// Guath Docs: https://developers.google.com/identity/sign-in/web/server-side-flow
'use strict';

pk.login = {
  LOGIN_URL: '/api/user/login',
  KEYS: {F2:113},

  init: function() {
    this.container = $('#logo');
    this.form = $('#logo form');
    console.debug('init pk.login on #'+ this.container.attr('id'));
    this.init_gauth();
    this.init_triggers();
    this.init_shortcuts();
  },

  init_gauth: function() {
    var self = this;
    gapi.load('auth2', function() {
      self.gauth = gapi.auth2.init({
        client_id: GOOGLE_CLIENTID,
        scope: GOOGLE_SCOPES
      });
    });
  },

  init_triggers: function() {
      var self = this;
      // Display login form
      this.container.on('click', function(event) {
        event.stopPropagation();
        setTimeout(function() {
          var clicks = parseInt(self.container.data('clicks'));
          if (clicks > 0) {
            self.container.data('clicks', clicks-1);
          } else {
            window.top.location = '/';
          }
        }, 200);
      }).on('dblclick', function(event) {
        event.stopPropagation();
        self.container.data('clicks', 2);
        self.show_form();
        window.getSelection().removeAllRanges();
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
      // Sign in to Google
      $('#gauth').on('click', function() {
        self.gauth.grantOfflineAccess().then(function(data) {
          if (data['code']) { self.login(data); }
        });
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
    if (this.container.hasClass('enabled')) {
      return null;
    }
    this.container.addClass('enabled');
    this.form.find('input[name=email]').val('').focus();
    this.form.find('input[name=password]').val('');
  },

  hide_form: function() {
    this.container.removeClass('enabled');
    this.form.removeClass('error');
  },

  login: function(data) {
    var self = this;
    var data = data || self.form.serializeArray();
    var xhr = $.ajax({url:self.LOGIN_URL, data:data, type:'POST', dataType:'json'});
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
