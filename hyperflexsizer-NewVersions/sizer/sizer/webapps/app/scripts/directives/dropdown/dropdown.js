angular.module('hyperflex')
  .directive('mplDropdown', [ 'utilService', function(utilService) {

  	/* directive definition */
    return {
      restrict: 'E',
      templateUrl: "scripts/directives/dropdown/dropdown.html",
      scope: {
      	label: "@",
        options: "=",
        onChange: "&",
        value: "="
      },
      link: function(scope, element, attrs) {
    
        var vm = scope;
        vm.displayVal = '';

        vm.onOptionSelected = function(option) {
          if(option) {
            vm.value = option.value;
            vm.displayVal = option.label;
          } else {
            vm.value = vm.displayVal = '';
          }
          if( typeof vm.onChange === 'function' ){
            vm.onChange({'selectedOption': vm.value});  
          }          
        }
        
        scope.$watch( 'options', function(newVal, oldVal){
          var option = utilService.getItemByPropVal( vm.options, 'value', vm.value );
          option = option || vm.options[0];
          vm.onOptionSelected(option); 
        });

        scope.$watch( 'value', function(newVal, oldVal){
          var option = utilService.getItemByPropVal( vm.options, 'value', newVal );
          option = option || vm.options[0];
          vm.onOptionSelected(option); 
        });


        
        
      } //link function

    };

  }]);
