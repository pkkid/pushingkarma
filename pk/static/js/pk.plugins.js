/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';


// Animate a jquery object
// See: https://daneden.github.io/animate.css/
$.fn.animatecss = function(effect) {
    var animationend = 'webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend';
    $(this).addClass('animated '+effect).one(animationend, function() {
        $(this).removeClass('animated '+effect);
    });
};
