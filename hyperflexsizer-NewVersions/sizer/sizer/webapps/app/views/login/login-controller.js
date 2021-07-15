(function() {
  "use strict";

  angular
    .module('hyperflex')
    .controller("LoginController", ["$scope", "$rootScope", "appService", "authService", "nodeService", function($scope, $rootScope, appService, authService, nodeService) {
      var vm = $scope;
      vm.loginError = false;
      var defaultErrorMessage = "Something went wrong!";
      vm.hasNotAuthorized = false;

      function login(){
      	vm.loginError = false;
      	var user = { name: "admin", password: "admin" };
        vm.hasNotAuthorized = false;
      	authService.login(user.name, user.password).then(function(data){
          appService.setRecommendedSettingsAccess(data.bench_cheat_sheet);
          appService.setIopsAccessDet(data.iops_access);
          if(data.status=="error"){
            vm.hasNotAuthorized = true;
          }else{
            data.username = data.username || user.name;
            /*if non LAE env, then set default user as logged in user*/
            if(!appService.isLAE()){
              appService.setUserDetails(data);                      
            }            
            getSizerVersion();  
          }
          
      	}, AjaxErrorCallback);
      };

      function getServerEnv(){
        authService.getServerEnv().then(function(data){
          if(data.lae){
            appService.setLAEStatus(true);
            appService.setUserDetails(data);            
          }else{
            appService.setLAEStatus(false);
          }          
          appService.setFeedbackEmail(data.email);
          login();
        }, AjaxErrorCallback);
      }

      function getSizerVersion(){
        nodeService.getSizerVersion().then(function(data){          
          appService.setSizerVersion(data);        
          // getProfilerInfo();
          appService.gotoView("scenario");
        }, AjaxErrorCallback);
      }

      function AjaxErrorCallback(error){
        error = error || {};
        vm.loginError = true;
        vm.errorMessage = error.errorMessage || defaultErrorMessage;
      }

      function getProfilerInfo(){
        nodeService.getProfilerInfo().then(function(data){          
          appService.setProfilerInfo(data);
          appService.gotoView("scenario");
        }, AjaxErrorCallback);
      }

      getServerEnv();

    }]);

})();
