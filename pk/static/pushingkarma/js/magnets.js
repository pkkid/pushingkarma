/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

pk.magnets = {

  init: function(selector, opts) {
    this.container = $(selector);
    if (!this.container.length) { return; }
    console.debug('init pk.magnets on '+ selector);
    this.uri = pk.utils.url({
      protocol: window.location.protocol == 'https:' ? 'wss:' : 'ws:',
      pathname: '/ws/foobar?subscribe-broadcast&publish-broadcast',
    });
    this.ws = this.init_websocket(this.uri);
  },
  
  init_websocket: function(uri) {
    var self = this;
    return new WS4Redis({uri:uri, heartbeat_msg:'heartbeat',
        receive_message: function(data) { self.receive_message(data); },
        connected: function(data) { self.connected(data); },
    });
  },
  
  connected: function() {
    console.debug('connected: '+ this.uri);
  },
  
  receive_message: function(data) {
    console.log('received: '+ data);
    this.container.append($('<div>'+ Date.now() +': '+ data +'</div>'));
  },
  
};
