// Encoding: UTF-8
'use strict';

pk.focus = {
    UPDATE_URL: '/focus/?json=1',
    REGEX_IP: /([0-9]{1,3}(\.[0-9]{1,3}){3}|[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7})/,

    init: function(selector, initdata) {
      var self = this;
      this.container = $(selector);
      if (!this.container.length) { return; }
      console.debug('init pk.focus on '+ selector);
      self.data = initdata || {};
      self.xhr = null;
      self.init_update_url();
      self.init_elements();
      self.init_triggers();
      // main loop
      this.update_widgets();
      this.update_clock();
      this.update_ip();
      setInterval(function() { self.update_clock(); }, 10000);      // 10 seconds
      setInterval(function() { self.update_news(); }, 20000);       // 20 seconds
      setInterval(function() { self.update_calendar(); }, 60000);   // 1 minute
      setInterval(function() { self.update_data(); }, 300000);      // 5 minutes
    },

    init_update_url: function() {
      var params = pk.utils.url_params();
      if (params.apikey) {
        this.UPDATE_URL += '&apikey='+ params.apikey;
      }
    },

    init_elements: function() {
      this.clock = this.container.find('#clock');
      this.photo = this.container.find('#photo');
      this.calendar = this.container.find('#calendar');
      this.weather = this.container.find('#weather');
      this.tasks = this.container.find('#tasks');
      this.news = this.container.find('#news');
      this.ip = this.container.find('#ip');
    },

    init_triggers: function() {
      var self = this;
      this.container.on('click', function() {
        self.container.toggleClass('hidecursor');
      });
      this.weather.on('click', '.weather-today-icon,.weather-today-details', function() {
        self.weather.toggleClass('hidedetails');
      });
      this.clock.on('click', function() {
        self.photo.toggleClass('hidedetails');
      });
      this.photo.on('click', '.mdi-autorenew', function() {
        self.update_data('&forcephoto=1&forcenews=1&forcecalendar=1&forcetasks=1&forceweather=1');
        $(this).animatecss('rotateOut');
      });
    },
    
    update_data: function(appendurl) {
      var self = this;
      var url = self.UPDATE_URL;
      if (appendurl) { url += appendurl; }
      self.xhr = $.ajax({url:url, type:'GET', dataType:'json'});
      self.xhr.done(function(data, textStatus, jqXHR) {
        self.data = data.data;
        self.update_widgets();
      });
    },

    update_widgets: function() {
      this.update_photo();
      this.update_weather();
      this.update_tasks();
      this.update_calendar();
      this.update_news();
    },

    update_clock: function() {
      try {
        this.clock.html(pk.templates.clock()).css('opacity', 1);
      } catch(err) {
        console.log('Error updating clock.');
      }
    },

    update_photo: function() {
      try {
        var self = this;
        var timer = $('body').css('opacity') == 0 ? 0 : 333;
        $('<img/>').attr('src', this.data.photo.url).on('load', function() {
          var that = this;
          $('body').css('opacity', 0);
          setTimeout(function() {
            self.photo.html(pk.templates.photo(self.data));
            $('body').css('background-image', 'url("'+ self.data.photo.url +'")');
            $('body').css('opacity', 1);
            $(that).remove();
          }, timer);
        });
      } catch(err) {
        console.log('Error updating photo.');
      }
    },

    update_weather: function() {
      try {
        this.weather.html(pk.templates.weather(this.data)).css('opacity', 1);
      } catch(err) {
        console.log('Error updating weather.');
      }
    },

    update_tasks: function() {
      try {
        this.tasks.html(pk.templates.tasks(this.data)).css('opacity', 1);
      } catch(err) {
        console.log('Error updating tasks.');
      }
    },

    update_ip: function() {
      try {
        var self = this;
        window.RTCPeerConnection = window.RTCPeerConnection || window.mozRTCPeerConnection || window.webkitRTCPeerConnection;
        var pc = new RTCPeerConnection({iceServers:[]})
        var noop = function(){};      
        pc.createDataChannel('');  //create a bogus data channel
        pc.createOffer(pc.setLocalDescription.bind(pc), noop);  // create offer and set local description
        pc.onicecandidate = function(ice) {
          if (ice && ice.candidate && ice.candidate.candidate) {
            var ip = self.REGEX_IP.exec(ice.candidate.candidate)[1];
            console.log('IP:', ip); self.ip.text(ip).css('opacity', 1);
            pc.onicecandidate = noop;
          }
        };
      } catch(err) {
        console.log('Error updating ip.');
      }
    },

    update_calendar: function() {
      try {
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
        this.calendar.html(pk.templates.calendar({events:events})).css('opacity', 1);
      } catch(err) {
        console.log('Error updating calendar.');
      }
    },

    update_news: function() {
      try {
        var self = this;
        if (self.data.news) {
          self.news.fadeOut('slow', function() {
            var index = Math.floor(Math.random() * self.data.news.length);
            var data = {article: self.data.news[index]};
            self.news.html(pk.templates.news(data)).fadeIn('slow');
          });
        }
      } catch(err) {
        console.log('Error updating news.');
      }
    },

}
