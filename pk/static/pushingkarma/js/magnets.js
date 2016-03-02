/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

pk.magnets = {
  KEYS: {ENTER:13},

  init: function(selector, opts) {
    this.container = $(selector);
    if (!this.container.length) { return; }
    console.debug('init pk.magnets on '+ selector);
    this.newword = this.container.find('#addword');
    this.canvas = this.container.find('#canvas');
    this.uri = pk.utils.url({
      protocol: window.location.protocol == 'https:' ? 'wss:' : 'ws:',
      pathname: '/ws/magnets?subscribe-broadcast&publish-broadcast&echo',
    });
    this.init_triggers();
    this.init_shortcuts();
    this.ws = this.init_websocket(this.uri);
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
        self.addword($(this).val());
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
  
  addword: function(word) {
    console.log('Adding: '+ word);
    var data = {
      word: word,
      id: 'word-'+ Date.now() +'-'+ word.toLowerCase(),
      status: 'placed',
      x: parseInt(Math.random() * (this.canvas.width() - 100)) + 20,
      y: parseInt(Math.random() * (this.canvas.height() - 50)) + 20,
      r: (Math.random() * 10) - 5,
    };
    var elem = $('<div id="'+ data.id +'" class="word">'+ word +'</div>');
    elem.css({
      'position': 'absolute',
      'transform': 'rotate('+ data.r +'deg)',
      'top': data.y +'px',
      'left': data.x +'px',
    });
    this.canvas.append(elem);
  },
  
  removeword: function(elem) {
    console.log('Removing: '+ elem.text());
    elem.remove();
  },
  
  drag: function(elem, event) {
    var self = this;
    var h = elem.outerHeight();
    var w = elem.outerWidth();
    var y = elem.offset().top + h - event.pageY;
    var x = elem.offset().left + w - event.pageX;
    var move = function(event) {
      event.preventDefault();
      elem.addClass('dragging');
      elem.offset({top:event.pageY+y-h, left:event.pageX+x-w});
    };
    var stop = function(event) {
      event.preventDefault();
      $('body').unbind('mousemove', move);
      $('body').unbind('mouseup', stop);
      elem.removeClass('dragging');
      if (!self.is_inbound(elem)) {
        self.removeword(elem);
      }
    };
    $('body').bind('mousemove', move);
    $('body').bind('mouseup', stop);
  },
  
  is_inbound: function(elem) {
    var x1 = parseInt(elem.position().left);
    var y1 = parseInt(elem.position().top);
    var x2 = parseInt(x1 + elem.width());
    var y2 = parseInt(y1 + elem.height());
    return !((x1 < -5) || (y1 < -5) || (x2 > this.canvas.width() + 5) || (y2 > this.canvas.height() + 5));
  },
  
  connected: function() {
    console.debug('connected: '+ this.uri);
  },
  
  receive_message: function(data) {
    console.log('received: '+ data);
    this.container.append($('<div>'+ Date.now() +': '+ data +'</div>'));
  },
  
};
