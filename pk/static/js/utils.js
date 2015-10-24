/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

var pk = {  // jshint ignore:line
    ANIMATIONEND: 'webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend',

    utils: {
        ajax: function(url, data) {
            var xhr = $.ajax({url:url, data:data, type:'POST', dataType:'json'});
            return xhr.then(function(data, textStatus, jqXHR) {
                var deferred = new $.Deferred();
                if (!data.success) 
                    return deferred.reject(jqXHR, textStatus, data);
                return deferred.resolve(data, textStatus, jqXHR);
            });
        },

        enable_animations: function() {
            setTimeout(function() {
                $('body').removeClass('preload');
            }, 500);
        },

        init_tooltips: function(selector) {
            selector = this.set_default(selector, '[data-toggle="tooltip"]');
            console.debug('init_tooltips: '+ selector);
            $(selector).tooltip({delay:{show:200, hide:50}});
        },

        set_default: function(input, default_value) {
            return typeof input !== 'undefined' ? input : default_value;
        },
    },
};
