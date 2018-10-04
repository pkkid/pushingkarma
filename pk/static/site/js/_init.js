// Encoding: UTF-8
'use strict';

// pk namespace and constants
var pk = {  // jshint ignore:line
  ANIMATIONEND: 'webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend',
};

$(function() {
  // Handlebars templates
  pk.templates = [];
  $.each($('script[type="text/x-handlebars-template"]'), function() {
    var id = this.getAttribute('id');
    pk.templates[id] = Handlebars.compile(this.innerText);
    if ($(this).hasClass('partial')) {
      Handlebars.registerPartial(id, pk.templates[id]);
    }
  });

  // Core website functions
  pk.utils.enable_animations();
  pk.utils.copycode();
  pk.utils.highlightjs();
  pk.utils.init_tooltips();
  pk.login.init();
  pk.magnets.init('#magnets');
});
