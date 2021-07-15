angular.module('hyperflex')
  .directive('resizeScenarioWidget', ['$timeout', '$uibModal', 'scenarioService', 'nodeService', 'ScenarioDataProcessor', function($timeout, $uibModal, scenarioService, nodeService, ScenarioDataProcessor) {

    /* directive definition */
    return {
      restrict: 'EA',
      templateUrl: "scripts/directives/resize-scenario/resize-scenario-widget.html",
      scope: {
        scenarioId: '@',
        loaderId: '@'
      },
      link: function(scope, element, attrs) {
        var vm = scope || {};
        var progressBarId = attrs.loaderId;

        function emitEvent(status, data){
          scope.$emit("RESIZE_SCENARIO", {status:status, data: data});
        }

        vm.showConfirmation = function(){
          var confirmModal = $uibModal.open({
            templateUrl: 'views/scenario_details/modals/resize-confirmation.html',
            size: 'sm',
            backdrop: 'static',
            keyboard: false
          });

          confirmModal.result.then(function () {
            emitEvent("PROGRESS");

            nodeService.resizeScenario(attrs.scenarioId, progressBarId).then(function(updatedScenario){
              emitEvent("SUCCESS", updatedScenario);
            }, function(rejection){
              var errorMsg = rejection.data ? rejection.data.errorMessage : '';
              emitEvent("ERROR");
            });
            
          }, function () {
            console.log("Cancel")
          });            
        }

      } //link function

    };


  }]);
