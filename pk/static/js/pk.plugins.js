/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

// Animate a jquery object
// See: https://daneden.github.io/animate.css/
$.fn.animatecss = function(effect, callback) {
    $(this).addClass('animated '+effect).one(pk.ANIMATIONEND, function() {
        $(this).removeClass('animated '+effect);
        if (callback !== undefined)
            callback();
    });
};
