(function() {
  "use strict";

  angular
    .module('hyperflex')
    .config(routeConfig);

  //routes configuration
  function routeConfig($stateProvider, $locationProvider, $urlRouterProvider) {

    $stateProvider
      .state('login', {
        url: '/',
        templateUrl: 'views/login/login.html',
        controller: 'LoginController as loginCtrl'
      })
      .state('scenario', {
        url: '/scenario',
        templateUrl: 'views/scenario/scenario.html',
        controller: 'ScenarioController as scenarioCtrl'
      })
      .state('scenariodetails', {
        url: '/scenario/:id',
        templateUrl: 'views/scenario_details/scenario_details.html',
        controller: 'WorkloadController as workloadCtrl'
      })
      .state('help', {
        url: '/help',
        templateUrl: 'views/help/help.html',
        controller: 'HelpController as helpCtrl'
      }) 
      .state('iops_table', {
        url: '/iops_table',
        templateUrl: 'views/iops_table/iops_table.html',
        controller: 'IOPSController as iopsCtrl'
      })
      .state('reverse_sizing', {
        url: '/reverse_sizing',
        templateUrl: 'views/reverse_sizing/reverse_sizing.html',
        controller: 'ReverseSizerController as reverseCtrl'
      })
      .state('hx_bench', {
        url: '/hx_bench',
        templateUrl: 'views/hx_tools/hx_bench.html',
        controller: 'HxToolsController as hxtoolsCtrl'
      })
       .state('hx_profiler', {
        url: '/hx_profiler',
        templateUrl: 'views/hx_tools/hx_profiler.html',
        controller: 'HxToolsController as hxtoolsCtrl'
      })
      // .state('settings', {
      //   url: '/settings',
      //   templateUrl: 'views/settings/settings.html',
      //   controller: 'settingController as settingsCtrl'
      // })
    $urlRouterProvider.otherwise('/');

    //set pretty url or enabling html5 mode
    // $locationProvider.html5Mode({
    //   enabled: true,
    //   requireBase: false
    // });

  }

}());
