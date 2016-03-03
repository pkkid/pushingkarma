/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

pk.magnets = {
  ACTIONS: {ADD:'add', UPDATE:'update', REMOVE:'remove'},
  DRAGGING: 'dragging',
  FRAMES_PER_SEC: 10,
  KEYS: {ENTER:13},

  init: function(selector, opts) {
    this.container = $(selector);
    if (!this.container.length) { return; }
    console.debug('init pk.magnets on '+ selector);
    this.newword = this.container.find('#addword');
    this.canvas = this.container.find('#canvas');
    this.uri = pk.utils.url({
      protocol: window.location.protocol == 'https:' ? 'wss:' : 'ws:',
      pathname: '/ws/magnets?subscribe-broadcast&publish-broadcast',
    });
    this.ws = this.init_websocket(this.uri);
    this.init_triggers();
    this.init_shortcuts();
  },
  
  init_triggers: function() {
    var self = this;
    this.container.on('mousedown', '.word', function(event) {
      event.preventDefault();
      self.drag($(this), event);
    });
  },
  
  init_shortcuts: function() {
    var self = this;
    // add word
    this.newword.keyup(function(event) {
      if (event.keyCode == self.KEYS.ENTER) {
        event.preventDefault();
        self.add_word($(this).val());
        $(this).val('');
      }
    });
  },
  
  init_websocket: function(uri) {
    var self = this;
    return new Redsocket({uri:uri, heartbeat_msg:'heartbeat',
        receive_message: function(data) { self.receive_message(data); },
        connected: function(data) { self.connected(data); },
    });
  },
  
  add_word: function(data) {
    // Check input data is a simple string and generate new data
    if (typeof(data) == 'string') {
      data = {
        word:data,
        cls:'',
        id: pk.utils.format('word-{0}-{1}', Date.now(), data.toLowerCase()),
        x: parseInt(Math.random() * (this.canvas.width() - 100)) + 20,
        y: parseInt(Math.random() * (this.canvas.height() - 50)) + 20,
        r: (Math.random() * 10) - 5,
      };
      this.send_message(this.ACTIONS.ADD, data);
    }
    // Build the DOM object and add it to canvas
    var elem = $(pk.utils.format('<div id="{0}" class="word">{1}</div>', data.id, data.word));
    this.update_word(data, elem);
    this.canvas.append(elem);
  },
  
  drag: function(elem, event) {
    var self = this;
    var h = elem.outerHeight();
    var w = elem.outerWidth();
    var y = elem.position().top + h - event.pageY;
    var x = elem.position().left + w - event.pageX;
    var move = function(event) {
      event.preventDefault();
      var newdata = {'cls':self.DRAGGING, 'x':event.pageX+x-w, 'y':event.pageY+y-h};
      self.update_word(newdata, elem);
      // elem.addClass(self.DRAGGING);
      // elem.offset({top:event.pageY+y-h, left:event.pageX+x-w});
    };
    var timer = setInterval(function() {
      self.send_message(self.ACTIONS.UPDATE, elem.data('data'));
    }, 1000 / this.FRAMES_PER_SEC);
    var stop = function(event) {
      event.preventDefault();
      clearTimeout(timer);
      $('body').unbind('mousemove', move);
      $('body').unbind('mouseup', stop);
      elem.removeClass(self.DRAGGING);
      if (!self.is_inbounds(elem)) {
        self.send_message(self.ACTIONS.REMOVE, elem.data('data'));
        return self.remove_word(elem.data('data'));
      }
      var data = self.update_word({'cls':''}, elem);
      self.send_message(self.ACTIONS.UPDATE, data);
    };
    $('body').bind('mousemove', move);
    $('body').bind('mouseup', stop);
  },
  
  is_inbounds: function(elem) {
    var x1 = parseInt(elem.position().left);
    var y1 = parseInt(elem.position().top);
    var x2 = parseInt(x1 + elem.width());
    var y2 = parseInt(y1 + elem.height());
    return !((x1 < -5) || (y1 < -5) || (x2 > this.canvas.width() + 5) || (y2 > this.canvas.height() + 5));
  },
  
  remove_word: function(data) {
    this.canvas.find('#'+data.id).remove();
  },
  
  update_word: function(newdata, elem) {
    elem = elem !== undefined ? elem : this.canvas.find('#'+newdata.id);   
    var data = $.extend({}, elem.data('data'), newdata);
    if ('cls' in newdata) { elem.attr('class', 'word '+ data.cls); }
    if ('x' in newdata) { elem.css('left', data.x +'px'); }
    if ('y' in newdata) { elem.css('top', data.y +'px'); }
    if ('r' in newdata) { elem.css('transform', 'rotate(', data.r +'deg)'); }
    elem.data('data', data);
    return data;
  },
  
  connected: function() {
    console.debug('connected: '+ this.uri);
  },
  
  receive_message: function(datastr) {
    console.log('recieve_message: '+ datastr);
    var data = JSON.parse(datastr);
    if (data.action == this.ACTIONS.ADD) { this.add_word(data); }
    else if (data.action == this.ACTIONS.UPDATE) { this.update_word(data); }
    else if (data.action == this.ACTIONS.REMOVE) { this.remove_word(data); }
  },
  
  send_message: function(action, data) {
    var datastr = JSON.stringify($.extend({}, data, {action:action}));
    console.log('send_message: '+ datastr);
    this.ws.send_message(datastr);
  },
  
};
