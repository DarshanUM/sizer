angular.module('hyperflex')
  .directive('multiSelect', [ 'utilService', function(utilService) {

  	var MSCounter = 0;
    var defautlModel = {
      title: "",
      options: [ ],
      model: [ ],
      disabledOptions: [],
      hiddenOptions: [],
      optionSuffix: '',
      includeSelectAll: false,
    }

    /* directive definition */
    return {
      restrict: 'E',
      templateUrl: "scripts/directives/multi-select/multi-select.html",
      scope: {
      	modelData: "=",
        disabled: '=',
        onSelectionChanged: '&'
      },
      link: function(scope, element, attrs) {
      	MSCounter++;

        var vm = scope;

        vm.prefix = "MS"+MSCounter;
        vm.data = {
        	selectAll: false,
        	options: getOptionsModel(vm.modelData.options, vm.modelData.model, vm.modelData.disabledOptions, vm.modelData.hiddenOptions)
        };

        scope.$on("SCENARIO_UPDATED", function(){
            vm.data.selectAll = true;
            vm.data.options = getOptionsModel(vm.modelData.options, vm.modelData.model, vm.modelData.disabledOptions, vm.modelData.hiddenOptions);
            vm.onChange();
        });

        vm.toggleSelectAll = function(){
        	for(var option in vm.data.options){
            if( !vm.data.options[ option ].isDisabled && !vm.data.options[ option ].isHidden ){
              vm.data.options[ option ].isChecked = vm.data.selectAll;
            }
        	}
        	vm.onChange(null, true);
        };

        vm.onChange = function(data, explicitChange){
        	var selectedOptionsData, selectedOptions;
          selectedOptionsData = getSelectedOptions(vm.data.options);
          if(selectedOptionsData && selectedOptionsData.length){
            selectedOptions = selectedOptionsData.map(function(option) {
              return option.value;
            });
          }
          
          var nonHiddenSelectedOptions = utilService.filteredList(selectedOptionsData, function(option) {
            return !option.isHidden;
          } );

          var nonHiddenOptions = getNonHiddenOptions(vm.data.options);

          vm.modelData.isNoneSelected = (!selectedOptions || selectedOptions.length===0);
          // if(selectedOptions && selectedOptions.length === (vm.modelData.options.length - (vm.modelData.hiddenOptions ? vm.modelData.hiddenOptions.length : 0)) ){
          if(nonHiddenSelectedOptions && nonHiddenSelectedOptions.length >= nonHiddenOptions.length) {
        		vm.data.selectAll = true;
        	}else{
        		vm.data.selectAll = false;
        	}

          if(selectedOptions && selectedOptions.length === vm.modelData.options.length ){
            vm.modelData.model = [];
          }else{
            vm.modelData.model = selectedOptions;           
          }

          if (typeof vm.onSelectionChanged === 'function') {
            vm.onSelectionChanged({'$event': {
              selectedOptions: selectedOptions,
              changeType: explicitChange ? 'EXPLICIT' : 'IMPLICIT'
            }});
          }
          
        };	

        vm.onChange();
      } //link function

    };

    /*PRIVTE FUNCTIONS*/
    function getSelectedOptions(options){
    	var list = [];
    	for(var option in options){
    		if( !options[option].isDisabled && options[option].isChecked ){
    			list.push(options[option]);
    		}
    	}
    	return list.length ? list : null;
    }

    function getNonHiddenOptions(options) {
      var list = [];
      for(var option in options){
        if( !options[option].isHidden ){
          list.push(options[option]);
        }
      }
      return list.length ? list : null;
    }

    function getOptionsModel(options, selectedOptions, disabledOptions, hiddenOptions){
    	var list = {}, isChecked=false;
    	for(var i=0; i<options.length; i++){
    		isChecked = !selectedOptions ? 
                      false : 
                      selectedOptions.length ? (selectedOptions.indexOf( options[i] )>-1) : true;
        list[ options[i] ] = {
          value: options[i],
          isChecked: isChecked,
          isDisabled: (  disabledOptions && disabledOptions.indexOf(options[i]) != -1 ),
          isHidden: (  hiddenOptions && hiddenOptions.indexOf(options[i]) != -1 )
        };
    	}
    	return list;
    }

  }]);
