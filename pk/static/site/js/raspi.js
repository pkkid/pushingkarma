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
      this.update_data();
      setInterval(this.update_data, self.UPDATE_INTERVAL);
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
        console.log(data);
        self.weather.html(pk.templates.weather(data));
      });
    },

}
