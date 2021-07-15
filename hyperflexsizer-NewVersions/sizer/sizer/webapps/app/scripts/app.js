(function() {
  "use strict";

  var ngModules = [
    'ngAnimate',
    'ngStorage',
    'ngSanitize',
    'ngResource',
    'ui.router',
    'ui.bootstrap'    
  ];

  var externalModules = [
      'chart.js',
      'angular-svg-round-progressbar',
      'ngScrollbars'
  ];

  var appModules = [
    'hyperflex-env',
    'maple.formvalidation',
    'maple.progress'    
  ];

  var modulesToInject = [];
  modulesToInject = modulesToInject.concat(ngModules);
  modulesToInject = modulesToInject.concat(externalModules);
  modulesToInject = modulesToInject.concat(appModules);

  // modulesToInject = [];

  angular.module('hyperflex', modulesToInject);

})();
