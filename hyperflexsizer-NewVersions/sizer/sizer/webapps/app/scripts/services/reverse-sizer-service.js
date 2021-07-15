(function() {
  'use strict';

  angular
    .module('hyperflex')
    .service('ReverseSizerService', ['appService', 'APP_ENV', 'REQUEST_TYPE', function(appService, APP_ENV, REQUEST_TYPE) {

      var fn = this;

      fn.getNodeOptions = function(nodeType, progressBarId){
        var config = {
          url: APP_ENV.baseUrl + "/hyperconverged/reversesizerfilter",
          method: "GET",
          progressbar: {id:progressBarId || 'reverse-size-node-options-request'}
        };
        return appService.processRequest(config);
      }

      fn.reverseSize = function(reqData, progressBarId) {
        var config = {
          url: (APP_ENV.baseUrl + "/hyperconverged/reversesizer"),
          method: "POST",
          data: reqData,
          progressbar: {id:progressBarId || 'reverse-size-request'}
        };
        return appService.processRequest(config);
      };

    }])

})();
