// Encoding: UTF-8
'use strict';

pk.focus = {
    UPDATE_URL: '/raspi/?json=1',
    UPDATE_INTERVAL: 300 * 1000,

    init: function(selector, opts) {
      var self = this;
      this.container = $(selector);
      if (!this.container.length) { return; }
      console.debug('init pk.focus on '+ selector);
      self.data = {};
      self.xhr = null;
      self.init_update_url();
      self.init_elements();
      self.init_triggers();
      // main loop
      setInterval(function() { self.update_clock(); }, 10000);
      setInterval(function() { self.update_calendar(); }, 60000);
      setInterval(function() { self.update_news(); }, 20000);
      setInterval(this.update_data, self.UPDATE_INTERVAL);
      this.update_data();
      this.update_clock();
    },

    init_update_url: function() {
      var params = pk.utils.url_params();
      if (params.apikey) {
        this.UPDATE_URL += '&apikey='+ params.apikey;
      }
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
        self.weather.html(pk.templates.weather(self.data)).fadeIn();
        self.tasks.html(pk.templates.tasks(self.data)).fadeIn();
        self.update_calendar();
        self.update_news();
      });
    },

    update_clock: function() {
      this.clock.html(pk.templates.clock()).fadeIn();
    },

    update_calendar: function() {
      var events = [];
      var now = moment();
      var max = moment().add(12, 'hours');
      for (var i=0; i < this.data.calendar.length; i++) {
        var start = moment(this.data.calendar[i].Start);
        var end = moment(this.data.calendar[i].End);
        if ((end > now) && (start < max)) {
          events.push(this.data.calendar[i]);
        }
      }
      this.calendar.html(pk.templates.calendar({events:events})).fadeIn();
    },

    update_news: function() {
      var self = this;
      if (self.data.news) {
        self.news.fadeOut(function() {
          var index = Math.floor(Math.random() * self.data.news.length)
          var data = {article: self.data.news[index]};
          self.news.html(pk.templates.news(data)).fadeIn();
        });
      }
    },

}
