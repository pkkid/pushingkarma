/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

(function() {

    var init_editor = function() {
        $('.page-editor .handle').on('click', function() {
            $('#layoutborder').toggleClass('editing');
        });
        CodeMirror.fromTextArea(document.getElementById('page-textarea'), {
            lineNumbers: true,
            mode: 'htmlmixed',
            theme: 'blackboard',
            scrollbarStyle: 'simple',
        });
    };

    setTimeout(function() {
        $('body').removeClass('preload');
    }, 500);

    pk.login_form.init();
    pk.utils.init_tooltips();
    init_editor();
})();
