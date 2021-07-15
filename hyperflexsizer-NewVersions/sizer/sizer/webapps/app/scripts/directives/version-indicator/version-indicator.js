angular.module('hyperflex')
  .directive('verionIndicator', ['appService', function(appService) {

    /* directive definition */
    return {
      restrict: 'EA',
      templateUrl: "scripts/directives/version-indicator/version-indicator.html",
      scope: {
        tooltipPosition: '@'
      },
      replace: true,
      link: function(scope, element, attrs) {
        var vm = scope || {};
        var serverSizerInfo = appService.getSizerVersion();

        vm.tooltipText = "Current Sizer version (" + serverSizerInfo.sizer_version_str + " / HXDP " + serverSizerInfo.hx_version_str + ") supersedes the version the scenario was sized with. Please resize to update the sizing recommendation";        
        vm.tooltipPosition = attrs.tooltipPosition || "top";
      } //link function

    };


  }]);
