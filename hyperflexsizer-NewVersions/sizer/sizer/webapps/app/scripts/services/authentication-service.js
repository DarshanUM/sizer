(function() {
  "use strict";

  angular
    .module('hyperflex')
    .service('authService', ["appService", "APP_ENV", function(appService, APP_ENV) {

      this.login = function(username, password) {
        var config = {
          url: APP_ENV.baseUrl + "/auth/login/",
          method: "POST",
          progressbar: {id:'login-request'},
          data: { "username": username, "password": password },
          requireToken: false
        };

        return appService.processRequest(config);
      };

      this.getServerEnv = function() {
        var config = {
          url: APP_ENV.baseUrl + "/envinfo",
          method: "GET",
          progressbar: {id:'login-request'},
          requireToken: false
        };

        return appService.processRequest(config);
      };

      // this.logout = function(username, password) {
      //   var config = {
      //       url: "/profiler/logout",
      //       method: "POST"
      //   };

      //   return appService.processRequest(config);
      // };


    }]); //controller

})();
