/*  :::: NOTES :::: */
/*browser names should be names of the bowser librabry*/
/* url : https://github.com/lancedikson/bowser */

(function() {
  'use strict';

angular
    .module('hyperflex')
    .constant("SUPPORTED_BROWSERS", [ 
        "Chrome", 
        "Firefox"
      ]
    );

})();
