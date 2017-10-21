/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

// pk namespace and constants
var pk = {  // jshint ignore:line
  ANIMATIONEND: 'webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend',
};

$(function() {
  // Handlebars templates
  pk.templates = [];
  $.each($('script[type="text/x-handlebars-template"]'), function() {
    pk.templates[this.getAttribute('id')] = Handlebars.compile(this.innerText);
  });

  // Core website functions
  pk.utils.enable_animations();
  pk.utils.copycode();
  pk.utils.highlightjs();
  pk.utils.init_tooltips();
  pk.login.init();
  pk.magnets.init('#magnets');
});
