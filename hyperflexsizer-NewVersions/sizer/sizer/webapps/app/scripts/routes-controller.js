(function() {
  "use strict";

  angular
    .module('hyperflex')
    .run(['$rootScope', '$uibModal', 'appService', "SUPPORTED_BROWSERS", function($rootScope, $uibModal, appService, SUPPORTED_BROWSERS) {
      $rootScope.root = {}; 

      /*if the current browser name is not listed in the supported browsers array, then show a warning message*/        
      if(window.bowser){
        $rootScope.root.willBrowserSupport = ( SUPPORTED_BROWSERS.indexOf(window.bowser.name) !== -1 )
      }

      if(!$rootScope.root.willBrowserSupport){
        $rootScope.root.browserName = window.bowser.name;
        $rootScope.root.supportedBrowsers = SUPPORTED_BROWSERS;
        $uibModal.open({
          templateUrl: 'views/scenario/modals/support_browser.html',
          size: 'sm', 
          backdrop: 'static',
          keyboard: false  
        });
      }

      $rootScope.$on("$stateChangeStart", function(event, toState, toParams, fromState, fromParams) {
        if (toState.name !== 'login' && !appService.isUserLoggedIn()) {
          event.preventDefault();
          appService.gotoView("login");
          return;
        } else if (toState.name === 'scenariodetails' && toParams.id === "") {
          event.preventDefault();
          appService.gotoView("scenario");
          return;
        }

        $rootScope.root.currentState = toState.name;
      });

      /* Google Analytics Related. Setting the page view manually for single page applications(SPA)*/
      $rootScope.$on("$stateChangeSuccess", function(event, toState, toParams, fromState, fromParams) {
        var pageInfo = toState.templateUrl.split("/");
        var pageName = pageInfo[pageInfo.length-1];
        
        ga('set', 'page', pageName);
        ga('send', 'pageview');
      });
      /* Google Analytics */

    }]);




})();
