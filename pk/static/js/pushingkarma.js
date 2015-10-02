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
            console.log('init_tooltips: '+ selector);
            $(selector).tooltip({delay:{show:200, hide:50}});
        },

        set_default: function(input, default_value) {
            return typeof input !== 'undefined' ? input : default_value;
        },

    },
};



/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

pk.login = {
    logo: $('#logo'),
    form: $('#logo form'),
    login_url: '/auth/login/',
    logout_url: '/auth/logout/',

    init: function() {
        console.log('init_login_form');
        this.init_triggers();
    },

    init_triggers: function() {
        var self = this;
        // Display login form
        self.logo.on('click', function(event) {
            event.stopPropagation();
            self.show_form();
        }).children().on('click', function(event) {
            event.stopPropagation();
        });
        // Hide login form
        $('header').on('click', function(event) {
            event.preventDefault();
            self.hide_form();
        });
        // Submit login form
        self.form.on('submit', function(event) {
            event.preventDefault();
            event.stopPropagation();
            self.login();
        });
    },

    show_form: function() {
        if (this.logo.hasClass('enabled'))
            return null;
        this.logo.addClass('enabled');
        this.form.find('input[name=username]').val('').focus();
        this.form.find('input[name=password]').val('');
    },

    hide_form: function() {
        this.logo.removeClass('enabled');
        this.form.removeClass('error');
    },

    login: function() {
        var self = this;
        var data = self.form.serializeArray();
        var xhr = pk.utils.ajax(self.login_url, data);
        self.form.removeClass('error');
        xhr.done(function(data, textStatus, jqXHR) {
            self.form.animatecss('tada', function() {
                location.reload();
            });
        });
        xhr.fail(function(jqXHR, textStatus, errorThrown) {
            self.form.animatecss('shake');
            self.form.addClass('error');
        });
    },

};



/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

pk.pages = {

    init: function() {
        this.editor = $('#page-editor');
        this.codemirror = this.init_codemirror();
        this.init_triggers();
    },

    init_codemirror: function() {
        var textarea = $('#page-textarea').get(0);
        return CodeMirror.fromTextArea(textarea, {
            extraKeys: {'Enter': 'newlineAndIndentContinueMarkdownList'},
            lineNumbers: false,
            lineWrapping: true,
            matchBrackets: true,
            mode: 'gfm',
            scrollbarStyle: 'simple',
            theme: 'blackboard',
        });
    },

    init_triggers: function() {
        var self = this;
        // Toggle editor visibility
        this.editor.find('.handle').on('click', function() {
            $('body').toggleClass('editing');
            setTimeout(function() { self.codemirror.refresh(); }, 100);
        });
        // Constantly update content
        setInterval(function() {
            var data = {'markdown': self.codemirror.getValue()};
            var xhr = $.ajax({url:'/markdown/', method:'post', dataType:'json', data:data});
            xhr.done(function(data, textStatus, jqXHR) {
                console.log(data);
                $('#page').html(data.html);
            });
        }, 2000);
    },

};



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



/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

(function() {

    pk.utils.enable_animations();
    pk.utils.init_tooltips();
    pk.login.init();
    pk.pages.init();

})();
