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

  copycode: function(selector) {
    // initilize the clipboard plugin
    var clippy = new Clipboard('article pre .copycode', {
      text: function(trigger) {
        return _.trimEnd($(trigger).parents('pre').text());
      }
    });
    clippy.on('success', function(event) {
      $(event.trigger).animatecss('bounce');
    });
    // append copy button to each code block
    selector = this.set_default(selector, 'article pre code');
    $(selector).each(function(i, block) {
      var btn = $('<span class="copycode mdi mdi-content-duplicate"></span>');
      $(block).prepend(btn);
    });
  },
  
  hash: function(str) {
    var hash = 0, i, chr, len;
    if (str.length === 0) return hash;
    for (i = 0, len = str.length; i < len; i++) {
      chr = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + chr;
      hash |= 0; // Convert to 32bit integer
    }
    return Math.abs(hash).toString(16);
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

  add_commas: function(value) {
    var parts = value.toString().split('.');
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    return parts.join('.');
  },

  round: function(number, precision) {
    var factor = Math.pow(10, precision);
    var tempNumber = number * factor;
    var roundedTempNumber = Math.round(tempNumber);
    return roundedTempNumber / factor;
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

  //--------------------
  // Budget Functions
  // validate and convert int to amount
  is_int: function(value) {
    return !!value.match(/^-?\d+$/);
  },

  is_float: function(value) {
    return !!value.match(/^-?\d+\.\d{2}$/) || !!value.match(/^-?\d+$/);
  },

  to_int: function(value) {
    console.log(value);
    value = value.replace('$', '').replace(',', '');
    console.log(value);
    return pk.utils.round(value, 0)
  },

  to_float: function(value) {
    value = value.replace('$', '').replace(',', '');
    return pk.utils.round(value, 2);
  },

  to_amount_int: function(value) {
    var negative = value < 0;
    value = Math.abs(value);
    if (negative) { return '-$'+ pk.utils.add_commas(value); }
    return '$'+ pk.utils.add_commas(value);
  },

  to_amount_float: function(value) {
    var result;
    var negative = value < 0;
    value = Math.abs(value);
    if (negative) { result = '-$'+ pk.utils.add_commas(value); }
    else { result = '$'+ pk.utils.add_commas(value); }
    if (result.match(/\.\d{1}$/)) { return result +'0'; }
    if (!result.match(/\./)) { return result +'.00'; }
    return result;
  },

};
