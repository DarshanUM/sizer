angular.module('hyperflex')
  .directive('searchBox', ["$timeout", "$window", "$filter", "utilService", function($timeout, $window, $filter, utilService) {

    /* directive definition */
    return {
      restrict: 'EA',
      templateUrl: "scripts/directives/searchbox/searchbox.html",
      scope: {
        value: '=',
        options: "=",
        // srcData: '=',
        onSelect: "&"
      },
      link: function(scope, element, attrs) {
        var vm = scope;
        vm.hasFocus = false;
        vm.searchStr = "";
        vm.value = vm.value || '';
        vm.options = vm.options || [];
        var prevVal = vm.value;
        vm.filteredOptions = vm.options;
        
        vm.onSearchFieldFocused = function(){
          vm.showSearchList = vm.options.length!=0;  
          vm.searchStr = '';
          vm.hasFocus = true;
          vm.value = vm.value || prevVal;
        }

        vm.hideSearchResults = function(isExternalEvent){
          isExternalEvent = (isExternalEvent===undefined) ? true : isExternalEvent;
          vm.showSearchList = false;
          vm.value = vm.value || prevVal; 
          vm.searchStr = '';
          vm.hasFocus = false;
          if (isExternalEvent) {
            scope.$apply();  
          }          
        };

        vm.showInput = function() {
          prevVal = vm.value || prevVal;
          vm.searchStr = "";
          vm.value = "";
          vm.showSearchList = true;
        };

        vm.onSelectionDone = function(selectedOption){
          vm.value = selectedOption;
          triggerChangeFunction();
          vm.hideSearchResults(false);
        }

        function triggerChangeFunction() {
          if(typeof vm.onSelect === "function"){            
            $timeout(function() {
              vm.onSelect({selectedOption: vm.value});
            })
          }
        }

        scope.$watch('searchStr', function(newVal, oldVal){
          vm.filteredOptions = $filter('filter')(vm.options, vm.searchStr);
        });

        vm.cancelEvent = function(event) {
          event.stopPropagation();
        };

        $window.addEventListener( 'click', vm.hideSearchResults);

        scope.$on('destroy', function() {
          $window.removeEventListener( 'click', vm.hideSearchResults);
        });

        $timeout( function() {
          vm.onSelectionDone(vm.value);
        } )
        
      } //link function

    };

    
  }]);
