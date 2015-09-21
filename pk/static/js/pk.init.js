/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

(function() {

    var init_csrf_token = function() {
        $('body').bind('ajaxSend', function(event, xhr, opts) {
            if (opts.type == 'POST') {
                token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
                console.log('----');
                console.log(token);
                xhr.setRequestHeader('X-CSRF-Token', token);
            }
        });
    };

    var init_login_form = function() {
        console.log('init_login_form');
        var logo = $('#logo');
        var form = logo.find('form');
        // display login form
        logo.on('click', function(event) {
            event.stopPropagation();
            $(this).addClass('enabled');
            $(this).find('input[name=username]').focus();
        }).children().on('click', function(event) {
            event.stopPropagation();
        });
        // hide login form
        $('header').on('click', function(event) {
            logo.removeClass('enabled');
        });
        // submit login form
        form.on('submit', function(event) {
            event.preventDefault();
            event.stopPropagation();
            console.log('HEYA!');
            form.addClass('error');  // REMOVE
            form.animatecss('shake');  // REMOVE
            var xhr = $.ajax({url:'test.html', data:{}});
            xhr.done(function() {
                console.log('done!');
                form.animatecss('shake');
            });
        });
    };

    var init_tooltips = function(selector) {
        selector = pk.utils.set_default(selector, '[data-toggle="tooltip"]');
        console.log('init_tooltips: '+ selector);
        $(selector).tooltip({delay:{show:200, hide:50}});
    };

    // main
    init_csrf_token();
    init_login_form();
    init_tooltips();

})();
