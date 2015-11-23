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


// ScrollBottom (similar to scrolltop, but use bottom as the root)
// see: http://stackoverflow.com/questions/4188903/opposite-of-scrolltop-in-jquery
$.fn.scrollBottom = function(val) { 
    if (val) { return this.scrollTop($(document).height() - val - this.height()); }
    return $(document).height() - this.scrollTop() - this.height();
};


// Always send CSRF token with ajax requests
// https://docs.djangoproject.com/en/1.8/ref/csrf/#ajax
function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({beforeSend: function(xhr, settings) {
    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        var csrftoken = Cookies.get('csrftoken');
        xhr.setRequestHeader('X-CSRFToken', csrftoken);
    }
}});
