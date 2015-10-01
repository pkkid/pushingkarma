/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

(function() {

    var init_editor = function() {
        $('#page-editor .handle').on('click', function() {
            $('body').toggleClass('editing');
        });
        CodeMirror.fromTextArea(document.getElementById('page-textarea'), {
            lineNumbers: true,
            mode: 'markdown',
            theme: 'blackboard',
            scrollbarStyle: 'simple',
        });
    };

    pk.login_form.init();
    pk.utils.enable_animations();
    pk.utils.init_tooltips();
    init_editor();

})();
