/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

(function() {
    // Register Tooltips
    $('a[data-tooltip]').tooltip({delay:{show:200, hide:50}});
    // Apply Prettyprint to code blocks
    $('.content pre').prettyPrint();
})(); 
