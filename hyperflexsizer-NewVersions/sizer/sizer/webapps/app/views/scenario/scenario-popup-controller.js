(function() {
  "use strict";

  angular
    .module('hyperflex')
    .controller("ScenarioPopupController", ["$scope", "$uibModalInstance", "appService", "nodeService", "shareScenarioService", "scenarioService", "scenarioObject", "sharedUsers", function($scope, $uibModalInstance, appService, nodeService, shareScenarioService, scenarioService, scenarioObject, sharedUsers) {
      var vm = this;
      var defaultScenario = {
        username : appService.getUserInfo().name,
        name: "",
        settings_json: {
          account: "",
          deal_id: ""
        },
        sizing_type: 'optimal'
      };
      
      sharedUsers = sharedUsers || [];
      var srcSharedUsers = sharedUsers.concat([]);

      vm.shared = {
        sharedUsers: sharedUsers,
        selectedUsers: []
      }

      vm.scenarioObject = angular.extend(defaultScenario, scenarioObject);
      
      vm.onUsersSelected = function(){
        var tempUsers = vm.shared.selectedUsers.map(function(user){
          return Object.assign({}, user, {sharedusername: user.emp_userid, acl: "w"})
        })
        vm.shared.sharedUsers = srcSharedUsers.concat( tempUsers );
      }
      
      vm.shareScenario = function() {
        console.log(" saveSharing  ");
        var data = vm.shared.selectedUsers.map(function(user){
          return user.emp_userid
        })

        var reqData = {
          users_list: data
        }
        shareScenarioService.save(vm.scenarioObject.id, reqData).then(function(scenarioObjectAdded){
          $uibModalInstance.close(scenarioObjectAdded);
        });

        // if ($scope.addScenarioForm.$valid) {
        //   scenarioService.save(scenarioToAdd).$promise.then(function(scenarioObjectAdded){
        //     $uibModalInstance.close(scenarioObjectAdded);
        //   });
        // }
      }; //shareScenario

      vm.addScenario = function(scenarioToAdd) {
        if ($scope.addScenarioForm.$valid) {
          scenarioService.save(scenarioToAdd).$promise.then(function(scenarioObjectAdded){
            $uibModalInstance.close(scenarioObjectAdded);
          });
        }
      }; //addScenario

      vm.editScenario = function(scenarioToUpdate) {        
        console.log(scenarioToUpdate);
        if ($scope.editScenarioForm.$valid) {
          var dataToAPI = {};
          dataToAPI.name = scenarioToUpdate.name;
          dataToAPI.settings_json = scenarioToUpdate.settings_json;

          scenarioService.update({id:scenarioToUpdate.id}, dataToAPI).$promise.then(function(scenarioObjectUpdated) {
            $uibModalInstance.close(scenarioObjectUpdated);
          });
        }
      }; //editScenario

      vm.cloneScenario = function(scenarioToUpdate) {        
        if ($scope.cloneScenarioForm.$valid) {
          var dataToAPI = {};
          dataToAPI.settings_json = scenarioToUpdate.settings_json;
          dataToAPI.name = scenarioToUpdate.name;

          nodeService.cloneScenario(scenarioToUpdate.id, dataToAPI).then(function(data){
            $uibModalInstance.close(data);
          })
        }
      }; //cloneScenario

      vm.deleteScenario = function(scenarioIdToDelete) {
        scenarioService.delete({ id: scenarioIdToDelete.id }).$promise.then(function(response){
          $uibModalInstance.close(response);
        });
      }; //deleteScenario


    }]);

})();
