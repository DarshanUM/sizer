(function() {
  "use strict"; 

  angular
    .module('hyperflex')
    .controller("HxToolsController", ["$scope", function($scope) {
      var vm = this; 
      vm.contentHeight = window.innerHeight - 90;
      var viewItems1 = true;
      var viewItems2 = false;
      // vm.hxTool = [
      // 	{
      // 		name: "vCenter"
      // 	},
      // 	{
      // 		name: "Hyper-V"
      // 	}
      // ]
    //   vm.showSelectedItems = vm.hxTool[0].name;
    //   vm.selectItems = function(obj,index){ 
    //   	vm.showSelectedItems = obj;

    //   	 if(index == 0){ 
    //   	 	vm.viewItems1 = false; 
    //   		vm.viewItems2 = false; 
    //   	 }
    //   	else{ 
    //   	 	vm.viewItems1 = true; 
    //   		vm.viewItems2 = true; 
    //   	 }
    //   } 
    // 

  vm.selectVcenter = function(){
    vm.viewItems1 = false;
    vm.viewItems2 = false;
  }
   vm.selectHyper = function(){
    vm.viewItems1 = true;
    vm.viewItems2 = true;
  }
}]);

})();


