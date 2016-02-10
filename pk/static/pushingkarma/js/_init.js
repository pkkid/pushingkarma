/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

// pk namespace and constants
var pk = {  // jshint ignore:line
  ANIMATIONEND: 'webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend',
};

$(function() {
  // Core website functions
  pk.utils.enable_animations();
  pk.utils.highlightjs();
  pk.utils.init_tooltips();
  pk.login.init();
  
  // Side projects
  pk.magnets.init('#magnets');
});
