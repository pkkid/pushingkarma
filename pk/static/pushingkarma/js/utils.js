/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

pk.utils = {
  ajax: function(url, data, type) {
    type = type ? type : 'POST';
    var xhr = $.ajax({url:url, data:data, type:type, dataType:'json'});
    return xhr.then(function(data, textStatus, jqXHR) {
      var deferred = new $.Deferred();
      if (!data.success) 
        return deferred.reject(jqXHR, textStatus, data);
      return deferred.resolve(data, textStatus, jqXHR);
    });
  },

  basename: function(path) {
    return path.split('/').reverse()[0];
  },

  enable_animations: function() {
    setTimeout(function() {
      $('body').removeClass('preload');
    }, 500);
  },
  
  format: function() {
    var result = arguments[0];
    for (var i=0; i<arguments.length-1; i++) {
        var regexp = new RegExp('\\{'+i+'\\}', 'gi');
        result = result.replace(regexp, arguments[i+1]);
    }
    return result;
  },
  
  highlightjs: function(selector) {
    selector = this.set_default(selector, 'article pre code');
    $(selector).each(function(i, block) {
      hljs.highlightBlock(block);
    });
  },

  init_tooltips: function(selector) {
    selector = this.set_default(selector, '[data-toggle="tooltip"]');
    console.debug('init tooltips on '+ selector);
    $(selector).tooltip({delay:{show:200, hide:50}});
  },

  set_default: function(input, default_value) {
    return typeof input !== 'undefined' ? input : default_value;
  },
  
  url: function(opts) {
    var protocol = opts.protocol || window.location.protocol || '';
    var hostname = opts.hostname || window.location.hostname || '';
    var port = opts.port || window.location.port || '';
    var pathname = opts.pathname || window.location.pathname || '';
    var search = opts.search || window.location.search || '';
    if (port) { port = ':'+ port; }
    return pk.utils.format('{0}//{1}{2}{3}{4}', protocol, hostname, port, pathname, search);
  },
};
