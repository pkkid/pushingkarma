/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

/**
 * Pretty Print Plugin
 * Applies Prettyprint to the selected elements
 **/
$.fn.prettyPrint = function() {
    if ($(this).length) {
        $(this).addClass('prettyprint');
        prettyPrint();
    }
};


/**
 * Slide Link Plugin
 * Slide to the selected element's href
 **/
$.fn.slideLink = function() {
    $(this).click(function() {
        var anchor = $(this).attr('href');
        $('html,body').animate({scrollTop: $(anchor).offset().top}, function() {
            return true;
        });
    });
};