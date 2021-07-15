(function () {
  "use strict";

  angular
    .module('hyperflex')
    .controller("FixedSizingController", ["$scope", "$timeout", "FEATURES", "$uibModalInstance", "appService", "utilService", "ReverseSizerService", "scenarioService", "scenarioObj", "fixedConfingFilterData", function ($scope, $timeout, FEATURES, $uibModalInstance, appService, utilService, ReverseSizerService, scenarioService, scenarioObj, fixedConfingFilterData) {
      var vm = this;
      var SEPERATOR = '_*_';
      var defaultNodeType = 'cto';
      var numOfComputeNodes = 0;
      // default values
      var DEFAULT_INPUTS = {
        node_properties: {
          node: 'HX220C-M5SX',
          no_of_nodes: 3,
          compute_node: '',
          no_of_computes: 0,
          cpu: '6130 [Sky] (16, 2.1, 768)',
          ram: 128,
          disks_per_node: 6,
          disk_capacity: 1200,
          cache_size: '',
          nodeType: defaultNodeType
        },
        cluster_properties: {
          rf: 3,
          ft: 1,
          dedupe_factor: 10,
          compression_factor: 20
        }
      };
      vm.threshold = scenarioObj.aggregate.settings.threshold;
      vm.hypervisor = scenarioObj.aggregate.settings.hypervisor;
      vm.hx_boost_conf = scenarioObj.aggregate.settings.hx_boost_conf;
      vm.hercules_conf = scenarioObj.aggregate.settings.hercules_conf;


      // default options
      vm.fixedConfingFilterData = fixedConfingFilterData;
      var hxNodesList = [];
      var filteredHXNodesList = [];  // either cto nodes or bundle nodes
      vm.computeNodesList = [];
      vm.options = {
        hxNodeTypes: [],
        computeNodeTypes: [],
        hxNumNodes: [],
        computeNumNodes: [],
        cpu: [],
        ram: [],
        diskDrives: [],
        diskSizes: [],
        ssdOptions: [],
        workloadOptions: []
      };

      // user values
      vm.inputs = { node_properties: {}, cluster_properties: {} };
      vm.canEnableApply = false;
      vm.FEATURES = FEATURES;

      /* cluster properties code */
      vm.nextSteps = function () {
        $scope.globalSetting = true;
        $scope.globalSetup = true;
      }

      vm.onRFChanged = function (rfVal) {
        vm.inputs.cluster_properties.ft = (vm.inputs.cluster_properties.ft < rfVal) ? vm.inputs.cluster_properties.ft : (rfVal - 1);
        vm.options.headroom = getOptionsInDDFormat(getArray(rfVal));
      };

      vm.onFTChanged = function (ftVal) {
        if (ftVal > 1) {
          vm.options.hxNumNodes = vm.options.hxNumNodes.map(function (option) {
            return Object.assign({}, option, { disabled: (option.value < 5) });
          });
          if (vm.inputs.node_properties.no_of_nodes < 5) {
            vm.inputs.node_properties.no_of_nodes = 5;
            vm.showNodeCountChangeNotification = true;
            if (notificationTimer) {
              clearTimeout(notificationTimer);
            }
            notificationTimer = $timeout(function () {
              vm.showNodeCountChangeNotification = false;
            }, 5 * 1000);
          }
        } else {
          vm.options.hxNumNodes = vm.options.hxNumNodes.map(function (option) {
            return Object.assign({}, option, { disabled: false });
          });
        }
      }

      function getArray(val) {
        var list = []; val = val || 0;
        for (var i = 0; i < val; i++) {
          list.push(i);
        }
        return list;
      }

      vm.onCompressionInputChange = function (e) {
        var val = parseInt(e.target.value);
        vm.compressionError = (val < 0 || val > 99);
        vm.onInputChanged();
      }

      vm.onDedupeInputChange = function (e) {
        var val = parseInt(e.target.value);
        vm.dedupeError = (val < 0 || val > 99);
        vm.onInputChanged();
      }
      /* End cluster properties code */

      vm.onHypervisorChanged = function () {

        // get the nodes list supprted for selected hypervisor
        hxNodesList = utilService.filteredList(vm.fixedConfingFilterData.node_details, function (node) {
          return node.hypervisor.indexOf(vm.hypervisor) !== -1;
        });

        if ('hyperv' === vm.hypervisor) {
          vm.hercules_conf = 'disabled';
          vm.hx_boost_conf = 'disabled';
        }
        /* if(vm.hypervisor === 'hyperv') {
          vm.inputs.node_properties.compute_node = '';
          vm.inputs.node_properties.no_of_computes = 0;
        } */
        // updates the options in UI
        vm.checkNodeFilterParam();
        vm.onNodeTypeChanged();
      };

      vm.checkNodeFilterParam = function () {
        if (vm.hercules_conf === 'forced') {
          hxNodesList = utilService.filteredList(hxNodesList, function (node) {
            return node.hercules_avail;
          });
        }
        if (vm.hx_boost_conf === 'forced') {
          hxNodesList = utilService.filteredList(hxNodesList, function (node) {
            return node.hx_boost_avail;
          });
        }
      }

      vm.onNodeTypeChanged = function () {
        filteredHXNodesList = utilService.filteredList(hxNodesList, function (node) {
          return node.node_type === vm.inputs.node_properties.nodeType;
        });
        // this is to manually / implicitly trigger the change event so that data will be updated appopriately
        updateByNodesList();
        console.log(vm.inputs.node_properties);
      };

      vm.onDiskDriveChange = function (data) {
        var disk = utilService.filteredList(vm.options.diskSizes, function (dData) {
          return dData.value === data;
        })[0];
        vm.options.hxNumNodes = disk ? getOptionsInDDFormat(disk.data[3][vm.hypervisor]) : [];
        vm.options.diskDrives = disk ? getOptionsInDDFormat(disk.data[2]): [];
      }

      vm.onHXNodeTypeChanged = function (hxNodeType) {
        if (filteredHXNodesList && filteredHXNodesList.length === 0) {
          return;
        }
        var hxNodeData = utilService.getItemByPropVal(filteredHXNodesList, 'node_name', hxNodeType);
        if (!hxNodeData) {
          return;
        }
        vm.computeNodesList = hxNodeData.compute_nodes;
        // compute node should be empty when hyperv is selected
        var computeNodeNames = vm.computeNodesList.map(function (computeNode) {
          return computeNode.name;
        });
        vm.options.computeNodeTypes = getOptionsInDDFormat(computeNodeNames);
        vm.options.computeNumNodes = getOptionsInDDFormat([]);
        // vm.options.hxNumNodes = getOptionsInDDFormat(hxNodeData.num_nodes[vm.hypervisor]);
        vm.options.cpu = getCpuOptionsInFormat(hxNodeData.cpu_options);
        vm.options.ram = getRamOptionsInDDFormat(hxNodeData.ram_options);
        // vm.options.diskDrives = getOptionsInDDFormat(hxNodeData.hdd_slots);
        vm.options.rf = getOptionsInDDFormat(hxNodeData.rf, "RF ");

        var totalHddOptions = hxNodeData.hdd_options;
        var totalSsdOptions = hxNodeData.ssd_options;
        // var partsToBeExcluded = vm.fixedConfingFilterData.excluded_parts[vm.hypervisor];
        var supprtedHddOptions = utilService.filteredList(totalHddOptions, function (option) {
          // given option should not be in exclude list
          return option[4].indexOf(vm.hypervisor) !== -1;
        });
        // var supprtedSsdOptions = utilService.filteredList(totalSsdOptions, function (option) {
        //   // given option should not be in exclude list
        //   return partsToBeExcluded.indexOf(option[1]) === -1;
        // });

        vm.options.diskSizes = getOptionsInDDFormat(supprtedHddOptions);
        vm.options.ssdOptions = getOptionsInDDFormat(totalSsdOptions);
        vm.options.workloadOptions = hxNodeData.workload_options;
        vm.onDiskDriveChange(vm.inputs.node_properties.disk_capacity)
        updateComputeNodes(vm.inputs.node_properties.no_of_nodes);
      };

      vm.onComputeNodeTypeChanged = function (computeNodeType) {
        var computeNodeData = utilService.getItemByPropVal(vm.computeNodesList, 'name', computeNodeType);
        if (computeNodeData) {
          vm.options.cpu = getCpuOptionsInFormat(computeNodeData.cpu_options);
          vm.options.ram = getRamOptionsInDDFormat(computeNodeData.ram_options);
          if (vm.hx_boost_conf === 'forced') {
            var reqCores = 12;
            if (vm.inputs.node_properties.node.indexOf("NVME") > -1) {
              reqCores = 16;
            }
            vm.options.cpu = utilService.filteredList(vm.options.cpu, function (cpu) {
              return cpu.cores >= reqCores;
            });
          }
        }

        if (scenarioObj.aggregate.settings.node_properties) {
          numOfComputeNodes = scenarioObj.aggregate.settings.node_properties.no_of_computes;
          vm.inputs.node_properties.cpu = angular.copy(scenarioObj.aggregate.settings.node_properties.cpu);
          vm.inputs.node_properties.ram = angular.copy(scenarioObj.aggregate.settings.node_properties.ram);
          if (vm.inputs.node_properties.cpu instanceof Array) {
            vm.inputs.node_properties.cpu = vm.inputs.node_properties.cpu.join(SEPERATOR);
            vm.inputs.node_properties.ram = vm.inputs.node_properties.ram.join(SEPERATOR);
          }
        } else {
          // setting default CPU value(E5-2650v4) for M4 nodes
          if (utilService.hasText(vm.inputs.node_properties.node, 'M4')) {
            vm.inputs.node_properties.cpu = DEFAULT_INPUTS.node_properties.cpu;
          } else { // setting default CPU value for M5 nodes
            vm.inputs.node_properties.cpu = vm.options.cpu[0].value;
            /* if (computeNodeData.cpu_options.indexOf(vm.inputs.node_properties.cpu) < 0) {
              vm.inputs.node_properties.cpu = computeNodeData.cpu_options[0];
            } */
            var cpuValue = (vm.inputs.node_properties.cpu.split(SEPERATOR))[3];
            var filterBy = (vm.inputs.node_properties.cpu.split(SEPERATOR))[0].split(' ')[1];
            var ramOptions = [];
            const cpuLimit = cpuValue * (utilService.hasText(vm.inputs.node_properties.node, '1 CPU') ? 1 : 2);
            vm.options.ram.map(function (item) {
              if (item.value.indexOf(filterBy) > -1 && item.size <= cpuLimit) {
                ramOptions.push(item);
              }
            });
            vm.options.ram = ramOptions;
          }
        }
      };


      function updateComputeNodes(hxNodeCount) {
        var computeNodes;
        if (vm.options.computeNodeTypes.length === 0) {
          // if there are no compute nodes, then number of compute should be 0
          computeNodes = [0]
        } else {
          computeNodes = [];
          hxNodeCount = hxNodeCount || 0;
          // var maxHXNodesCount = vm.options.hxNumNodes[vm.options.hxNumNodes.length - 1].value;
          // var maxComputeNodes = Math.min( 2*hxNodeCount, maxHXNodesCount);
          var maxComputeNodes;
          // var maxComputeNodes = Math.min( 2*hxNodeCount, maxHXNodesCount);
          if (vm.hypervisor === 'hyperv') {
            maxComputeNodes = vm.inputs.node_properties.no_of_nodes;
          } else {
            maxComputeNodes = (2 * vm.inputs.node_properties.no_of_nodes) > 32 ? 32 : (2 * vm.inputs.node_properties.no_of_nodes);
            // maxComputeNodes = (2 * maxHXNodesCount) > 32 ? 32 : (2 * maxHXNodesCount);
          }
          // else if (vm.inputs.node_properties.node.indexOf('NVME') !== -1) {
          //   maxComputeNodes = vm.inputs.node_properties.no_of_nodes;
          // }
          for (var i = 0; i <= maxComputeNodes; i++) {
            computeNodes.push(i);
          }
        }
        vm.options.computeNumNodes = getOptionsInDDFormat(computeNodes);
      }


      vm.onHxNodeCountChanged = function (hxNodeCount) {
        if (scenarioObj.aggregate.settings && scenarioObj.aggregate.settings.node_properties) {
          vm.inputs.node_properties.no_of_computes = scenarioObj.aggregate.settings.node_properties.no_of_computes || numOfComputeNodes;
        }
        updateComputeNodes(hxNodeCount);
      }

      vm.onCpuInputChanged = function (selectedOption) {
        if (selectedOption) {
          vm.isCPUValueSet = true;
        }
        if (!this.inputs.node_properties.compute_node) {
          return;
        }
        var cpuValue = (selectedOption.split(SEPERATOR))[3];
        var filterBy = (selectedOption.split(SEPERATOR))[0].split(' ')[1];
        // var cpuValue = parseInt(selectedOption.split(', ').pop().split(')'));
        var computeNodeData = utilService.getItemByPropVal(vm.computeNodesList, 'name', this.inputs.node_properties.compute_node);
        if (computeNodeData) {
          vm.options.ram = getRamOptionsInDDFormat(computeNodeData.ram_options);
        }
        var ramOptions = [];
        const cpuLimit = cpuValue * (utilService.hasText(vm.inputs.node_properties.node, '1 CPU') ? 1 : 2);

        vm.options.ram.map(function (item) {
          if (item.value.indexOf(filterBy) > -1 && item.size <= cpuLimit) {
            ramOptions.push(item);
          }
        });
        vm.options.ram = ramOptions;
        vm.onInputChanged();
      }

      vm.onInputChanged = function () {
        $timeout(function () {
          vm.canEnableApply = _canEnableApply();
        });
      }

      function _canEnableApply() {
        var nodePropsData = vm.inputs.node_properties;
        var prop, val;
        for (prop in nodePropsData) {
          if (prop === 'compute_node') {
            continue;
          }
          val = nodePropsData[prop];
          if (val === undefined || val === null || val === '') {
            // console.log( prop, val );
            return false;
          }
        }
        return true;
      }

      vm.onApply = function () {
        var reqObject = getRequestObject();
        reqObject.wl_list = utilService.filteredList(reqObject.wl_list, function (wl) {
          return !((wl.wl_type === 'VDI' || wl.wl_type === 'RDSH') && wl.hasOwnProperty('primary_wl_name'));
        });
        reqObject.settings_json[0].node_properties.ram = reqObject.settings_json[0].node_properties.ram.split(SEPERATOR);
        reqObject.settings_json[0].node_properties.cpu = reqObject.settings_json[0].node_properties.cpu.split(SEPERATOR);
        reqObject.settings_json[0].node_properties.cpu[1] = JSON.parse(reqObject.settings_json[0].node_properties.cpu[1]);
        reqObject.settings_json[0].node_properties.cpu[3] = JSON.parse(reqObject.settings_json[0].node_properties.cpu[3]);
        reqObject.settings_json[0].node_properties.cpu[4] = JSON.parse(reqObject.settings_json[0].node_properties.cpu[4]);
        var dupCpu = angular.copy(reqObject.settings_json[0].node_properties.cpu);
        var val = dupCpu.shift();
        val = val.split(' ')[0] + ' (';
        dupCpu.pop();
        dupCpu.pop();
        reqObject.settings_json[0].node_properties.cpu_label = val + dupCpu.join(', ') + ')';
        reqObject.settings_json[0].node_properties.ram[1] = JSON.parse(reqObject.settings_json[0].node_properties.ram[1]);
        reqObject.settings_json[0].node_properties.ram[2] = JSON.parse('[' + reqObject.settings_json[0].node_properties.ram[2] + ']');
        var dupRam = angular.copy(reqObject.settings_json[0].node_properties.ram)
        var val = 0;
        var addVal = dupRam.pop();
        var mulVal = dupRam.pop();
        var label = '';
        if (addVal instanceof Array) {
          val = addVal.reduce(function (a, b) { return a + b; }, 0);
          if (addVal.length > 1) {
            label = ' ['
            addVal.map(function (item, index) {
              if (index !== 0) {
                label = label + ' + '
              }
              label = label + mulVal + ' x ' + item + 'GiB';
            });
            label = label + ']';
          } else {
            label = ' [' + mulVal + ' x ' + addVal[0] + 'GiB]';
          }
        }
        val = val * mulVal;
        reqObject.settings_json[0].node_properties.ram_label = val + label;
        scenarioService.save({ id: scenarioObj.id }, reqObject).$promise.then(function (response) {
          $uibModalInstance.close({
            fixedConfingFilterData: vm.fixedConfingFilterData,
            scenario: response
          });
        }, function () {

        });

      };

      function getInputVal(dataArr, separator) {
        return (dataArr instanceof Array) ? dataArr.join(separator) : dataArr;
      }

      function getOutputVal(dataStr, separator) {
        var dataArr = dataStr.split(separator);
        // convert to a number only if it is a string formatted numeric value
        if (!(isNaN(dataArr[0]))) {
          dataArr[0] = parseInt(dataArr[0]);
        }

        return dataArr.length > 1 ? dataArr : dataStr;
      }

      function getRequestObject() {
        var nodeProps = vm.inputs.node_properties;
        var clusterProps = vm.inputs.cluster_properties;
        // this is to decide which workload types are allowed for the scenario in fixed sizing
        nodeProps.workload_options = vm.options.workloadOptions;

        nodeProps.cache_size = getOutputVal(nodeProps.cache_size, SEPERATOR);
        nodeProps.disk_capacity = getOutputVal(nodeProps.disk_capacity, SEPERATOR);

        return {
          "model_list": [],
          "overwrite": true,
          "model_choice": "None",
          "sizing_type": "fixed",
          "username": appService.getUserInfo().name,
          "name": scenarioObj.name,
          "settings_json": [
            {
              "account": scenarioObj.aggregate.settings.account,
              "deal_id": scenarioObj.aggregate.settings.deal_id,
              "sizer_version": scenarioObj.aggregate.settings.sizer_version,
              "hx_version": scenarioObj.aggregate.settings.hx_version,
              "result_name": "Fixed Config",
              "node_properties": nodeProps,
              "cluster_properties": clusterProps,
              "threshold": vm.threshold,
              "hypervisor": vm.hypervisor,
              "hx_boost_conf": vm.hx_boost_conf,
              "hercules_conf": vm.hercules_conf
            }
          ],
          "wl_list": scenarioObj.aggregate.workloads
        };
      }


      function preInit() {
        // init();
        if (vm.fixedConfingFilterData) {
          init();
          vm.onHypervisorChanged();
        } else {
          $timeout(function () {
            ReverseSizerService.getNodeOptions().then(function (response) {
              vm.fixedConfingFilterData = response;
              init();
              vm.onHypervisorChanged();
            });
          }, 100);
        }
      }

      function init() {
        vm.inputs = Object.assign({}, utilService.getClone(DEFAULT_INPUTS), {
          node_properties: scenarioObj.aggregate.settings.node_properties,
          cluster_properties: scenarioObj.aggregate.settings.cluster_properties
        });
        // in case of optimal scenario, node_properties will not be avialble in settings
        vm.inputs.node_properties = vm.inputs.node_properties || DEFAULT_INPUTS.node_properties;
        vm.inputs.cluster_properties = vm.inputs.cluster_properties || DEFAULT_INPUTS.cluster_properties;
        vm.inputs.node_properties.nodeType = vm.inputs.node_properties.nodeType || defaultNodeType;

        vm.inputs.node_properties.disk_capacity = getInputVal(vm.inputs.node_properties.disk_capacity, SEPERATOR);
        vm.inputs.node_properties.cache_size = getInputVal(vm.inputs.node_properties.cache_size, SEPERATOR);

      }

      function updateByNodesList() {
        var nodeNames;
        try {
          nodeNames = filteredHXNodesList.map(function (node) { return node.node_name; });
        } catch (e) {
          nodeNames = [];
        }
        vm.options.hxNodeTypes = getOptionsInDDFormat(nodeNames);
        if (vm.options.hxNodeTypes.length) {
          var selectedNode = vm.inputs.node_properties.node || vm.options.hxNodeTypes[0].value;
          vm.onHXNodeTypeChanged(selectedNode);
        }
      }

      function getOptionsInDDFormat(list, prefixStr) {
        prefixStr = prefixStr || "";
        list = list || [];
        return list.map(function (item) {
          var isArray = (item instanceof Array);
          var dataItem = isArray ? utilService.filteredList(item, function (it) {
            return typeof it !== 'object';
          }) : item
          return {
            label: prefixStr + (isArray ? item[0] : item),
            value: isArray ? dataItem.join(SEPERATOR) : item,
            data: isArray ? item : {}
          }
        })
      }

      function getRamOptionsInDDFormat(list) {
        list = list || [];
        return list.map(function (item) {
          var label = '';
          var dupItem = angular.copy(item)
          var val = 0;
          if (dupItem instanceof Array) {
            var addVal = dupItem.pop();
            var mulVal = dupItem.pop();
            if (addVal instanceof Array) {
              val = addVal.reduce(function (a, b) { return a + b; }, 0);
              if (addVal.length > 1) {
                label = ' ['
                addVal.map(function (item, index) {
                  if (index !== 0) {
                    label = label + ' + '
                  }
                  label = label + mulVal + ' x ' + item + 'GiB';
                });
                label = label + ']';
              } else {
                label = ' [' + mulVal + ' x ' + addVal[0] + 'GiB]';
              }
            }
            val = val * mulVal;
            label = val + label;
          }
          return {
            label: label,
            value: item instanceof Array ? item.join(SEPERATOR) : item,
            size: val
          }
        });
      }

      function getCpuOptionsInFormat(list) {
        list = list || [];
        return list.map(function (item) {
          var label = '';
          var dupItem = angular.copy(item);
          var size = 0;
          if (dupItem instanceof Array) {
            var val = dupItem.shift();
            val = val.split(' ')[0] + ' (';
            dupItem.pop();
            size = dupItem.pop();
            label = val + dupItem.join(', ') + ')';
          }/*  else {
            if (label.indexOf('[Sky]') >= 0) {
              label = label.split('[Sky] ').join('').split(', ');
            } else {
              label = label.split('[Cascade] ').join('').split(', ');
            }
            label.pop().pop();
            label = label.join(', ').concat(')');
          } */
          return {
            label: label,
            value: item instanceof Array ? item.join(SEPERATOR) : item,
            size: size,
            cores: dupItem[0]
          }
        });
      }

      preInit();


    }]);

})();


