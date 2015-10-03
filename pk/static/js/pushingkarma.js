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
            console.debug('init_tooltips: '+ selector);
            selector = this.set_default(selector, '[data-toggle="tooltip"]');
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
    UPDATE_INTERVAL: 1500,

    init: function() {
        this.editor = $('#page-editor');
        this.menu = this.editor.find('.menu');
        this.spinner = this.menu.find('.spinner');
        this.codemirror = this.init_codemirror();
        this.last_updated_text = this.codemirror.getValue();
        this.last_saved_text = this.last_updated_text;
        this.init_triggers();
        this.init_shortcuts();
    },

    init_codemirror: function() {
        var textarea = $('#page-textarea').get(0);
        return CodeMirror.fromTextArea(textarea, {
            extraKeys: {'Enter': 'newlineAndIndentContinueMarkdownList'},
            lineNumbers: false,
            lineWrapping: false,
            matchBrackets: true,
            mode: 'gfm',
            scrollbarStyle: 'simple',
            theme: 'blackboard',
        });
    },

    init_triggers: function() {
        var self = this;
        // Toggle editor visibility
        this.editor.find('.handle').on('click', function(event) {
            event.preventDefault();
            self.toggle_editor();
        });
        // Reset to last saved state
        this.menu.find('.reset').on('click', function(event) {
            event.preventDefault();
            self.reset();
        });
        // Save current text
        this.menu.find('.save').on('click', function(event) {
            event.preventDefault();
            self.save();
        });
        // Constantly update content
        setInterval(function() { self.update(); }, this.UPDATE_INTERVAL);
    },

    init_shortcuts: function() {
        var self = this;
        document.addEventListener('keydown', function(event) {
            var ctrl = navigator.platform.match('Mac') ? event.metaKey : event.ctrlKey;
            var s = event.keyCode == 83;
            var f2 = event.keyCode == 113;
            var editing = $('body').hasClass('editing');
            if (ctrl && s && editing) {
                event.preventDefault();
                self.save();
            } else if (f2) {
                event.preventDefault();
                self.toggle_editor();
            }
        }, false);
    },

    toggle_editor: function() {
        var self = this;
        if ($('body').hasClass('editing')) {
            $('body').removeClass('editing');
        } else {
            $('body').addClass('editing');
            setTimeout(function() { self.codemirror.refresh(); }, 100);
            setTimeout(function() { self.codemirror.refresh(); }, 600);
        }
    },

    update: function() {
        var self = this;
        var editing = $('body').hasClass('editing');
        var text = this.codemirror.getValue();
        if (!editing || (text == this.last_updated_text))
            return null;  // nothing to update
        var xhr = pk.utils.ajax('/markdown/', {'text':text});
        xhr.done(function(data, textStatus, jqXHR) {
            $('#page').html(data.html);
        });
        xhr.always(function() {
            self.last_updated_text = text;
        });
    },

    reset: function() {
        this.codemirror.setValue(this.last_saved_text);
    },

    save: function() {
        var self = this;
        this.spinner.addClass('on');
        var text = this.codemirror.getValue();
        var xhr = pk.utils.ajax(window.location.pathname, {'text':text});
        xhr.done(function(data, textStatus, jqXHR) {
            console.log('success!');
            self.last_saved_text = text;
        });
        xhr.always(function() {
            self.spinner.removeClass('on');
        });
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
