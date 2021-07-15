(function() {
  "use strict"; 

  angular
    .module('hyperflex')
    .controller("settingController", ["$scope", "$timeout", "utilService", "appService", "RecommendedSettingsService", function($scope, $timeout, utilService, appService, RecommendedSettingsService) {
      var vm = this;
      vm.settingHeight = window.innerHeight - 145; 
      // default values
      var DEFAULT_INPUTS = {
        node: 'HX220C-M4S',
        no_of_nodes: 3,
        disks_per_node: 6,
        disk_capacity: 1200,
        rf: 3,
        cache_size: 480,
        no_of_vms: 3
      };

      // default options
      vm.hxNodesList = [];
      vm.options = {
        hxNodeTypes: [],
        hxNumNodes: [],
        diskDrives: [],
        diskSizes: [],        
        cacheDiskSizes: [],
        rf: []
      };

      // user values
      vm.inputs = {};
      vm.isManualVMsInupt = false;
      vm.minNumVMs = 3;
      vm.maxNumVMs = 100;
      vm.numVMsError = false;
      vm.canEnableApply = false;  
      vm.noVMsFields = false;
      vm.result = {
        "no_of_vms": '--',
        "vm_size": '--',
        "dedupe": '--',
        "compression": '--',
        "working_set_percent": '--',
        "vm_size_unit": 'GB',
        "threads": '--'
      };
      vm.rfvalue = '';
      
    vm.onHXNodeTypeChanged = function(hxNodeType) {
      
      var hxNodeData = utilService.getItemByPropVal(vm.hxNodesList, 'node_name', hxNodeType);
      
      vm.options.hxNumNodes = getOptionsInDDFormat(hxNodeData.num_nodes);
      vm.options.cpu = getOptionsInDDFormat(hxNodeData.cpu_options);
      vm.options.ram = getOptionsInDDFormat(hxNodeData.ram_options);
      vm.options.diskDrives = getOptionsInDDFormat(hxNodeData.hdd_slots);
      vm.options.diskSizes = getOptionsInDDFormat(hxNodeData.hdd_options);
      vm.options.cacheDiskSizes = getOptionsInDDFormat(hxNodeData.ssd_options);      
      vm.options.rf = getOptionsInDDFormat(hxNodeData.rf, "RF ");
    };

    vm.onHxNodeCountChanged = function() {
      // vm.inputs.no_of_vms = vm.inputs.no_of_nodes * 3;
      vm.maxNumVMs = vm.inputs.no_of_nodes * 100;
      vm.onNumVMsChanged(null, vm.inputs.no_of_vms);
    };

    vm.onInputChanged = function() {
      $timeout( function() {
        vm.canEnableApply = _canEnableApply();
      });
    }

    vm.onNumVMsChanged = function(e, inputVal) { 
      var val = (inputVal==undefined) ? parseInt(e.target.value) : inputVal;
      vm.numVMsError =  (!val || val < vm.minNumVMs || val > vm.maxNumVMs);
      vm.onInputChanged();
    }

    vm.toggleVMsInputType = function(isManual){
      vm.isManualVMsInupt = isManual;
      vm.inputs.no_of_vms = (vm.inputs.no_of_vms > DEFAULT_INPUTS.no_of_vms) ? vm.inputs.no_of_vms : DEFAULT_INPUTS.no_of_vms;
      vm.onHxNodeCountChanged();
      vm.onInputChanged();
    }

    function _canEnableApply() {
      var prop, val, inputData;
      if (vm.isManualVMsInupt) {
        if (vm.numVMsError) {
          return false;  
        }        
        inputData = vm.inputs;
      }else {
        inputData = utilService.getClone(vm.inputs);
        delete inputData['no_of_vms'];
      }
      for(prop in inputData){
        val = inputData[prop];
        if(val === undefined || val === null || val === '') {
          return false;
        }
      }
      return true;
    }

    vm.onApply = function() {
      var inputData = utilService.getClone(vm.inputs);
      if(!vm.isManualVMsInupt) {
        delete inputData['no_of_vms'];
      }
      RecommendedSettingsService.calculate(inputData).then(function(response) {
        vm.result = response;
      });
    }
       
    function init() {
      vm.versionData = appService.getSizerVersion();
      vm.inputs = Object.assign({}, DEFAULT_INPUTS);
      $timeout( function() {
        RecommendedSettingsService.getRecommendedSettingsNodeOptions().then(function(response) {
          vm.hxNodesList = response || {};
          var nodeNames = vm.hxNodesList.map( function(node){ return node.node_name; } );
          vm.options.hxNodeTypes = getOptionsInDDFormat(nodeNames);
          var selectedNode = vm.options.hxNodeTypes[0].value;
          vm.onHXNodeTypeChanged( selectedNode );
        });
      } );
    }

    function getOptionsInDDFormat(list, prefixStr) {
      prefixStr = prefixStr || "";
      list = list || [];
      return list.map( function(item) {
        return {
          label: prefixStr+item,
          value: item
        }
      })
    }

    $scope.$on('$viewContentLoaded', function(event, viewConfig) {
        //If timeout is not used, loader message for initial reuqest(scenaio details) will not be visible as the mpl-progressabar not initialized by the time
        $timeout(function(){          
          init();
        }, 10)
      });

    }]);

})();
