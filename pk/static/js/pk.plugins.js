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
