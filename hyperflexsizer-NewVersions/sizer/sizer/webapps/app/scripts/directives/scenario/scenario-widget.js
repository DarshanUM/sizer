angular.module('hyperflex')
  .directive('scenarioWidget', ["$timeout", "appService", function($timeout, appService) {

    /* directive definition */
    return {
      restrict: 'EA',
      templateUrl: "scripts/directives/scenario/scenario-widget.html",
      scope: {
        modelData: '@',
        onShare: '&',
        onView: '&',
        onEdit: '&',
        onClone: '&',
        onDelete: '&',
        onClick: '&',
        onHeartClick: '&',
        onArchive: '&'
      },
      link: function(scope, element, attrs) {
        var vm = scope;

        vm.modelData = vm.modelData || {};

        vm.currentOwnership = scope.$parent.scenarioCtrl.currentOwnership;
        vm.loggedInUserName = appService.getUserInfo().name;

        scope.model = JSON.parse(attrs.modelData);
        attrs.modelData = '';
        
      } //link function

    };


  }]);
