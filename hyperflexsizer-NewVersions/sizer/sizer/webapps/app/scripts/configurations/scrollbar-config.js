(function() {
  "use strict";

  angular
    .module("hyperflex")
    .config(["ScrollBarsProvider", function (ScrollBarsProvider) {
      // scrollbar defaults
      ScrollBarsProvider.defaults = {
        autoHideScrollbar: false,
        axis: 'y',
        advanced: {
          updateOnContentResize: true
        },
        scrollButtons: {
          scrollAmount: 'auto', // scroll amount when button pressed
          enable: true // enable scrolling buttons by default
        } 
      };
    }]);


})();
