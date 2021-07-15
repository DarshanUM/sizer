(function() {
  "use strict";

  angular
    .module('hyperflex')
    .controller("ScenarioShareController", ["$scope", "$uibModal", "$filter", "$uibModalInstance", "HX_ANALYTICS_EVENTS", "appService", "utilService", "shareScenarioService", "scenarioObject", function($scope, $uibModal, $filter, $uibModalInstance, HX_ANALYTICS_EVENTS, appService, utilService, shareScenarioService, scenarioObject) {
      var vm = this;
      var loggedInUserName = appService.getUserInfo().name;

      var srcSharedUsers = [];
      var invalidUsers = []; //['test@test.com', 'mpalem@cisco.com'];
      var hasSharedUsersListChanged = false;
      vm.sharedUsers = [];
      vm.scenarioObject = angular.extend({}, scenarioObject);
      vm.errorMessage = "";
      vm.isValidEmailId = false;
      vm.isEnterPressed = false;



      $uibModalInstance.rendered.then(function() {
        shareScenarioService.getSharedUsers(scenarioObject.id).then( function(sharedUsersList) {
          srcSharedUsers = utilService.getClone(sharedUsersList);
          vm.sharedUsers = sharedUsersList;
        } );
      });
      
      vm.keyboardHander = function(evt){
        if(evt.keyCode === 27 || evt.key === "Escape"){
          vm.searchString = '';
          vm.isValidEmailId = false;
        }else if(evt.keyCode === 13 || evt.key === "Enter"){
          vm.isEnterPressed = true;
          if ( vm.isValidEmailId ) {
            vm.addUserToShareList();
          }
        } else {
          vm.isValidEmailId = isValidEmail(vm.searchString);
        }
      }

      function isValidEmail(stringData) {
        var mailRegEx = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
        if(stringData.match(mailRegEx)) {
          return true;
        } else{
          return false;
        }
      }


      $scope.$on('$destroy', function() {});

      /* Search box related */
      vm.searchString = "";

      vm.onCancelSharing = function(){
        if( isChanged(srcSharedUsers, vm.sharedUsers) ){          
          showConfirmation();
        }else{
          $uibModalInstance.dismiss();
        }
      };

      function showConfirmation() {
        var confirmModal = $uibModal.open({
          templateUrl: 'views/scenario/modals/share-cancel-confirmation.html',
          size: 'sm',
          backdrop: 'static',
          keyboard: false
        });
        confirmModal.result.then(function () {          
          if (hasSharedUsersListChanged) {
            $uibModalInstance.close();
          } else {
            $uibModalInstance.dismiss();
          }          
        }, function () {
          console.log("Cancel");
        }); 
      }

      function showShareScenarioError() {
        return $uibModal.open({
          templateUrl: 'views/scenario/modals/share-error.html',
          size: 'sm',
          backdrop: 'static',
          keyboard: false,
          controller: ['$scope', 'errorMessage', function(popupScope, errorMessage) {
            popupScope.errorMessage = errorMessage;
          }],
          resolve: {
            errorMessage: function() {
              return vm.errorMessage;
            }
          }
        });
      }

      function isChanged(srcList, tarList){
        if(srcList.length != tarList.length ){
          return true;
        }
        
        for(var i=0; i<srcList.length; i++){
          if(srcList[i].email != tarList[i].email || srcList[i].acl != tarList[i].acl ){
            return true;
          }
        }

        return false;
      }

      function updateUsersStatus(invalidUsersList) {
        vm.sharedUsers.forEach( function(user) {
          var data = utilService.doesListHasItem(invalidUsersList, user.email);
          user.invalid = !(!(data));
        } );
        // this is to trigger re-rendering
        vm.sharedUsers = [].concat(vm.sharedUsers);
      }
      
      vm.addUserToShareList = function(){
        /*updating the shared users*/
        var selectedUser = { 
          email: vm.searchString,
          acl: true
        };
        
        /* checking if the user is aleady in shared list*/
        var existingUsers = utilService.filteredList(vm.sharedUsers, function(user){
          return user.email == selectedUser.email;
        })
        if(existingUsers && existingUsers.length){
          // alert("This user is already in shared list");
          return console.log("This user is already in shared list");
        }

        vm.sharedUsers = [selectedUser].concat(vm.sharedUsers);

        vm.searchString = "";
        vm.isValidEmailId = false;
        vm.isEnterPressed = false;

        updateUsersStatus(invalidUsers);

      };// addUsersToShareList

      vm.deleteUserFromShareList = function(user){
        vm.sharedUsers = utilService.filteredList(vm.sharedUsers, function(dataItem){
          return user.email != dataItem.email
        });
      };

      vm.shareScenario = function() {

        var data = vm.sharedUsers.map(function(user){
          return {
            "email": user.email,
            "acl": user.acl
          }  
        });

        var reqData = {
          users_list: data
        }
        // return console.log(reqData);
        shareScenarioService.save(vm.scenarioObject.id, reqData).then(function(response){
          // $uibModalInstance.close();
          if (!hasSharedUsersListChanged) {
            hasSharedUsersListChanged = isChanged(srcSharedUsers, data);
          }

          // UI assumes that the response will be array & 2nd element of the reponse will be the error message if there is any error in sharing scenario
          if(response && response.length > 0 && response[1]){
            vm.errorMessage = response[1];
            invalidUsers = response[2];
            var shareErrorModal = showShareScenarioError();
            shareErrorModal.result.then(function () {          
              updateUsersStatus(invalidUsers);
              // $uibModalInstance.close();
            }, function () {
              updateUsersStatus(invalidUsers);
              // $uibModalInstance.close();
            });            
          }else{
            $uibModalInstance.close();
            vm.errorMessage = "";
          }

          // Google analytics :: Tracking the number scenario shares 
          ga('send', 'event', {
            eventCategory: HX_ANALYTICS_EVENTS.CATEGORY.SHARING_SCENARIO.UI_LABEL,
            eventAction: HX_ANALYTICS_EVENTS.CATEGORY.SHARING_SCENARIO.ACTIONS.SHARING_SCENARIO,
            eventLabel: HX_ANALYTICS_EVENTS.CATEGORY.SHARING_SCENARIO.LABELS.SHARING_SCENARIO,
            transport: 'beacon'
          });
        });
      }; //shareScenario


    }]);

})();
