(function() {
  'use strict';
  var module = angular.module('maple.progress', []);

  var REQUEST_STATES = {
    'PROGRESS' : 'mpl-progress',
    'ERROR' : 'mpl-error',
    'SUCCESS' : 'mpl-success',
    'CLOSE' : 'mpl-clear'
  };

  var CLSSES_LIST = REQUEST_STATES.PROGRESS + ' ' + REQUEST_STATES.ERROR + ' ' +
                    REQUEST_STATES.SUCCESS + ' ' + REQUEST_STATES.CLOSE;

  module.service('mplprogService', ['$rootScope', function($rootScope) {

    this.progress = function(elementId, statusMsg) {
      broadcast(elementId, REQUEST_STATES.PROGRESS, statusMsg);      
    };
    this.error = function(elementId, statusMsg, statusCode) {
      broadcast(elementId, REQUEST_STATES.ERROR, statusMsg, statusCode);
    };
    this.success = function(elementId, statusMsg) {
      broadcast(elementId, REQUEST_STATES.SUCCESS, statusMsg);
    };
    this.close = function(elementId, statusMsg) {
      broadcast(elementId, REQUEST_STATES.CLOSE, statusMsg);
    };

    function broadcast(progressElemId, requestState, statusMsg, statusCode) {
      $rootScope.$broadcast('MPL_PROGRESS_EVENT', { 
        progressElemId: progressElemId, 
        requestState: requestState,
        message: statusMsg,
        statusCode: statusCode
      });
    }

  }]);//service



  // Interceptor configuration
  module.config(["$provide", "$httpProvider", function httpInterceptorsConfig($provide, $httpProvider) {
    // Intercept http calls.
    $provide.factory('mplprogressHttpInterceptor', ["$q", "$injector", "mplprogService", function($q, $injector, mplprogService) {
      
      function reloadApplication(){
        // window.location.href = window.location.protocol + "//" + window.location.host;
        window.location.reload();
      }

      return {
        // On request success
        request: function(config) {
          if(config.progressbar && config.progressbar.id){
            mplprogService.progress(config.progressbar.id);
          }
          // Return the config or wrap it in a promise if blank.
          return config || $q.when(config);
        } ,

        // On request failure
        requestError: function(rejection) {
          var config = rejection.config;
          var errorMsg = rejection.data ? rejection.data.errorMessage : '';
          if(config.progressbar && config.progressbar.id){
            mplprogService.error(config.progressbar.id, errorMsg);
          }
          // Return the promise rejection.
          return $q.reject(rejection);
        },

        // On response success
        response: function(response) {
          var config = response.config;
          if(config.progressbar && config.progressbar.id){
            mplprogService.success(config.progressbar.id);
          }

          // Return the response or promise.
          return response || $q.when(response);
        },

        // On response error
        responseError : function(response) {
          var config = response.config;
          
          var errorMsg = response.data ? response.data.errorMessage : '';
          
          var $uibModal = $injector.get("$uibModal");
          /* Handling redirections :: */
          /* Reloading the current web page, so that app will be redirected to sign in page in this application*/
          /* 302 for Redirection request (though the status code from api http header comes from Server is 302, to the angular code it comes as -1) */
          if(response.status === 302 || response.status === -1){
            $uibModal.open({
              template: '<div class="modal-header"><h4 class="modal-title"> Browser Redirect <span class="pull-right cursor" ng-click="$dismiss()"><i class="fa fa-remove" aria-hidden="true"></i></span></h4></div><div class="modal-body delPopup_padding"> <p>Your session timed out. </p> <p> You will be redirected to the login page. </p></div>',
              size: 'sm', 
              backdrop: 'static',
              keyboard: false  
            }).result.then(function(data) {
              reloadApplication();
            }, function(data) {
              reloadApplication();
            });

            window.setTimeout(function(){
              reloadApplication();
            }, 5 * 1000);

            if(config.progressbar && config.progressbar.id){
              mplprogService.close(config.progressbar.id, "", "");
            }

          }else if(config.progressbar && config.progressbar.id){
            mplprogService.error(config.progressbar.id, errorMsg, response.status);
          }

          return $q.reject(response);
        }
      };//return

    }]);//mplprogressHttpInterceptor

    // Add interceptor to the $httpProvider.
    $httpProvider.interceptors.push('mplprogressHttpInterceptor');

  }]);//httpInterceptorsConfig  



  module.directive('mplProgress', ['$timeout', function($timeout) {
    var config = {
      progress: 'Your request is in progress',
      error: 'Oops!, got an error while processing your request',
      success: 'Your request has been processed successfully',
      autoClose: false,
      autoCloseOnError: false,
      autoCloseOnSuccess: true,
      timeoutOnError: 1000,
      timeoutOnSuccess: 0,
      closeBtn: true,
      backDrop: true
    }

    function getTruthyVal(givenVal, defaultValue){
      return angular.isUndefined(givenVal) ? defaultValue : 
              (givenVal === 'false' || givenVal === '0') ? false : Boolean(givenVal);
    }

    function getTimeoutVal(givenVal, defaultValue){
      var givenVal = parseInt(givenVal);
      return isNaN(givenVal) ? defaultValue : givenVal;         
    }

    return {
      restrict: 'A',
      scope:true,
      templateUrl: function(element, attrs) {
        return attrs.templateUrl || 'scripts/directives/progress-bar/progress-bar.html';
      },
      link: function(scope, el, attrs) {
        var elementId = el.attr('id');
        el.addClass('mpl-progress-bar-container');

        scope.progressMessage = attrs.progressMessage || config.progress;
        scope.errorMessage = attrs.errorMessage || config.error;
        scope.successMessage = attrs.successMessage || config.success;
        scope.autoClose = getTruthyVal(attrs.autoClose, config.autoClose);
        scope.autoCloseOnError = getTruthyVal(attrs.autoCloseOnError, config.autoCloseOnError);
        scope.autoCloseOnSuccess = getTruthyVal(attrs.autoCloseOnSuccess, config.autoCloseOnSuccess);
        scope.closeBtn = getTruthyVal(attrs.closeBtn, config.closeBtn);
        scope.backDrop = getTruthyVal(attrs.backDrop, config.backDrop);
        scope.timeoutOnError = getTimeoutVal(attrs.timeoutOnError, config.timeoutOnError);
        scope.timeoutOnSuccess = getTimeoutVal(attrs.timeoutOnSuccess, config.timeoutOnSuccess);

        var defaultProgressMessage = scope.progressMessage;
        var defaultErrorMessage = scope.errorMessage;
        var defaultSuccessMessage = scope.successMessage;

        scope.close = function(){
          scope.canShow=false;
        }        

        document.addEventListener("keyup", keyboardHander, true);
        document.addEventListener("keydown", keyboardHander, true);
        document.addEventListener("keypress", keyboardHander, true);
        scope.$on('$destroy', function() {
          document.removeEventListener("keyup", keyboardHander, true);
          document.removeEventListener("keydown", keyboardHander, true);
          document.removeEventListener("keypress", keyboardHander, true);
        });

        function keyboardHander(evt){
          if(scope.canShow && evt.keyCode === 27){
            evt.preventDefault();
            evt.stopPropagation();
            evt.stopImmediatePropagation();  
          }          
        }


        //listening to progress event
        scope.$on('MPL_PROGRESS_EVENT', function(event, data) {
          if(elementId!==data.progressElemId) return;

          if( data.message instanceof Array){
            data.message = data.message.join("<br />");
          }
          
          el.removeClass(CLSSES_LIST);
          el.addClass(data.requestState);

          if( data.message instanceof Array){
            data.message = data.message.join("<br />");
          }

          switch(data.requestState){
            case REQUEST_STATES.PROGRESS:
              scope.progressMessage = data.message || defaultProgressMessage;
              scope.canShow = true;  
              break;
            case REQUEST_STATES.ERROR:
              var msg = data.message ? "" : ("<br>Request Type:: "+ data.progressElemId + "<br>Status Code:: " + data.statusCode);            
              scope.errorMessage =  (data.message || defaultErrorMessage) + msg;
              scope.canShow = true;
              if(scope.autoClose || scope.autoCloseOnError){
                clear(scope.timeoutOnError)                
              }
              break;
            case REQUEST_STATES.SUCCESS:
              scope.successMessage = data.message || defaultSuccessMessage;
              scope.canShow = true;
              if(scope.autoClose || scope.autoCloseOnSuccess){
                clear(scope.timeoutOnSuccess);                
              }
              break;
            case REQUEST_STATES.CLOSE:
              scope.canShow = false;
              break;    
          }

          function clear(timeout){
            if(timeout){
              $timeout(function(){
                scope.canShow = false;
              }, timeout);  
            }else{
              scope.canShow = false;                  
            }
          }

        });//event listener

      }//link function
    }//directive definition object

  }]);

})();
