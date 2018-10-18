// Encoding: UTF-8
'use strict';

pk.utils = {

  add_commas: function(value) {
    var parts = value.toString().split('.');
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    return parts.join('.');
  },

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

  autosize_textarea: function(jqtext, padding, lineheight, minlines) {
    // padding and line-height must be set for this to work.
    minlines = minlines || 2;
    jqtext.on('input keyup', function(event) {
      var nlines = jqtext.val().split('\n').length
      var lines = Math.max(minlines, nlines);
      $(this).css('height', (lines * lineheight) + padding);
    }).trigger('input');
  },

  basename: function(path) {
    return path.split('/').reverse()[0];
  },
  
  format: function() {
    var result = arguments[0];
    for (var i=0; i<arguments.length-1; i++) {
        var regexp = new RegExp('\\{'+i+'\\}', 'gi');
        result = result.replace(regexp, arguments[i+1]);
    }
    return result;
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

  init_animations: function() {
    setTimeout(function() {
      $('body').removeClass('preload');
    }, 500);
  },

  init_copycode: function(selector) {
    if (window.ClipboardJS === undefined) { return; }
    selector = this.set_default(selector, 'article pre code');
    console.log('init copycode on '+ selector)
    // initilize the clipboard plugin
    var clippy = new ClipboardJS('article pre .copycode', {
      text: function(trigger) {
        return _.trimEnd($(trigger).parents('pre').text());
      }
    });
    clippy.on('success', function(event) {
      $(event.trigger).animatecss('bounce');
    });
    // append copy button to each code block
    $(selector).each(function(i, block) {
      var btn = $('<span class="copycode mdi mdi-content-duplicate"></span>');
      $(block).prepend(btn);
    });
  },

  init_handlebars: function() {
    if (window.Handlebars === undefined) { return; }
    // register handlebar helpers
    console.log('init handlebars');
    helpers._register();
    pk.budget.helpers._register();
    // compile handlebar templates
    pk.templates = [];
    $.each($('script[type="text/x-handlebars-template"]'), function() {
      var id = this.getAttribute('id');
      pk.templates[id] = Handlebars.compile(this.innerText);
      if ($(this).hasClass('partial')) {
        Handlebars.registerPartial(id, pk.templates[id]);
      }
    });
  },

  init_highlightjs: function(selector) {
    if (window.hljs === undefined) { return; }
    selector = this.set_default(selector, 'article pre code');
    $(selector).each(function(i, block) {
      hljs.highlightBlock(block);
    });
  },

  init_tooltips: function(selector) {
    if (jQuery().tooltip === undefined) { return; }
    selector = this.set_default(selector, '[data-toggle="tooltip"]');
    console.debug('init tooltips on '+ selector);
    $(selector).tooltip({delay:{show:200, hide:50}});
  },

  rset: function(object, property, value) {
    var parts = property.split('.');
    var current = parts.shift();
    var pointer = object;
    while (parts.length > 0) {
      if (pointer[current] === undefined)
        pointer[current] = {};
      pointer = pointer[current];
      current = parts.shift();
    }
    pointer[current] = value;
  },

  rget: function(object, property, delim) {
    delim = delim === undefined ? '.' : delim;
    var parts = property.split(delim);
    var current = parts.shift();
    if (object[current] !== undefined) {
      if (parts.length >= 1)
        return getProperty(object[current], parts.join(delim), delim);
      return object[current];
    }
    return undefined;
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

  url_params: function(url) {
    var params = {};
    var regex = /[?&]+([^=&]+)=([^&]*)/gi;
    var url = url || window.location.href;
    var parts = url.replace(regex, function(m, key, value) {
        params[key] = value;
    });
    return params;
  },

  update_url: function(url, params) {
    url = url === null ? new URL(window.location.href) : new URL(url);
    for (var key in params) {
      var value = params[key];
      if (value == '' || value == null) { url.searchParams.delete(key); }
      else { url.searchParams.set(key, value); }
    }
    return url.toString();
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
    value = value.replace('$', '').replace(',', '');
    return pk.utils.round(value, 0);
  },

  to_float: function(value) {
    value = value.replace('$', '').replace(',', '');
    return pk.utils.round(value, 2).toFixed(2);
  },

  to_amount_int: function(value) {
    var negative = value < 0;
    value = Math.round(Math.abs(value));
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
