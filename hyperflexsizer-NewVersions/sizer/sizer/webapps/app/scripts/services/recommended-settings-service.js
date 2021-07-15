(function() {
  'use strict';

  angular
    .module('hyperflex')
    .service('RecommendedSettingsService', ['appService', 'APP_ENV', function(appService, APP_ENV) {
      console.log(' RecommendedSettingsServiceProvider  ');
      var fn = this;

      fn.getRecommendedSettingsNodeOptions = function(nodeType, progressBarId){
        var config = {
          url: APP_ENV.baseUrl + "/hyperconverged/benchsheet",
          method: "GET",
          progressbar: {id:progressBarId || 'settings-node-options-request'}
        };
        return appService.processRequest(config);
      }

      fn.calculate = function(reqData, progressBarId) {
        var config = {
          url: (APP_ENV.baseUrl + "/hyperconverged/benchsheet"),
          method: "POST",
          data: reqData,
          progressbar: {id:progressBarId || 'recommended-settings-request'}
        };
        return appService.processRequest(config);
      };

    }])

})();
