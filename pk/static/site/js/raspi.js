// Encoding: UTF-8
'use strict';

pk.raspi = {
    UPDATE_URL: '/raspi/?json=1',
    UPDATE_INTERVAL: 300 * 1000,

    init: function(selector, opts) {
      var self = this;
      this.container = $(selector);
      if (!this.container.length) { return; }
      console.debug('init pk.raspi on '+ selector);
      self.data = {};
      self.xhr = null;
      self.init_elements();
      self.init_triggers();
      // main loop
      setInterval(function() { self.update_clock(); }, 10000);
      setInterval(function() { self.update_news(); }, 10000);
      setInterval(this.update_data, self.UPDATE_INTERVAL);
      this.update_data();
      this.update_clock();
    },

    init_elements: function() {
      this.clock = this.container.find('#clock');
      this.calendar = this.container.find('#calendar');
      this.weather = this.container.find('#weather');
      this.tasks = this.container.find('#tasks');
      this.news = this.container.find('#news');
    },

    init_triggers: function() {
      var self = this;
      this.container.on('click', function() {
        self.container.toggleClass('hidecursor');
      });
    },
    
    update_data: function() {
      var self = this;
      self.xhr = $.ajax({url:self.UPDATE_URL, type:'GET', dataType:'json'});
      self.xhr.done(function(data, textStatus, jqXHR) {
        self.data = data;
        self.weather.html(pk.templates.weather(self.data));
        self.update_news();
      });
    },

    update_clock: function() {
      this.clock.html(pk.templates.clock());
    },

    update_news: function() {
      var self = this;
      if (self.data.news) {
        self.news.fadeOut(function() {
          var index = Math.floor(Math.random() * self.data.news.length)
          var data = {article: self.data.news[index]};
          self.news.html(pk.templates.news(data));
          self.news.fadeIn();
        });
      }
    },

}
