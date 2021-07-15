(function () {
  "use strict";

  angular
    .module('hyperflex')
    .controller("ReverseSizerController", ["$scope", "$uibModal", "$timeout", "APP_ENV", "FEATURES", "HX_ANALYTICS_EVENTS", "appService", "utilService", "ReverseSizerService", "nodeService", function ($scope, $uibModal, $timeout, APP_ENV, FEATURES, HX_ANALYTICS_EVENTS, appService, utilService, ReverseSizerService, nodeService) {
      var vm = this;
      var SEPERATOR = '_*_';
      var defaultNodeType = 'cto';
      vm.reverseSizingHeight = window.innerHeight - 162;
      vm.resultSizingHeight = window.innerHeight - 195;
      // default values
      var DEFAULT_INPUTS = {
        node_properties: {
          node: '',
          no_of_nodes: 3,
          compute_node: 'HX220C-M4S',
          no_of_computes: 0,
          cpu: 'E5-2650v4',
          ram: 128,
          disks_per_node: 6,
          disk_capacity: 1200,
          cache_size: '',
          nodeType: defaultNodeType
        },
        scenario_settings: {
          threshold: '1',// standard
          hypervisor: 'esxi',
          rf: 3,
          ft: 1,
          dedupe_factor: 10,
          compression_factor: 20
        }
      };

      vm.FEATURES = FEATURES;

      // default options
      var fixedConfingFilterData = {};
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
        rf: [],
        headroom: [],
        ssdOptions: [],
        workloadOptions: []
      };

      // user values
      vm.inputs = {};
      vm.dedupeError = false;
      vm.compressionError = false;
      vm.canEnableApply = false;
      vm.result = {
        cores: {
          post_spec: '-',
          pre_spec: '-'
        },
        disk_capacity: {
          post_savings: '-',
          post_savings_unit: '-',
          pre_savings: '-',
          pre_savings_unit: '-',
          available: '-',
          effective: '-',
          usable: '-'
        },
        ram: '-',
        thresholds: {
          CPU: 100,
          DISK: 100,
          RAM: 100
        },
        enableDownload: false
      };
      vm.rfvalue = '';
      vm.showNodeCountChangeNotification = false;
      var notificationTimer;

      vm.comprDedupeCalc = function () {
        var compCalc = ((100 - vm.inputs.scenario_settings.compression_factor) / 100);
        var dedupeCalc = ((100 - vm.inputs.scenario_settings.dedupe_factor) / 100);
        var compData = vm.result.disk_capacity.available / compCalc;
        // var dedupeData = compData / dedupeCalc;
        vm.tooltipDataComp = vm.result.disk_capacity.available + "" + vm.result.disk_capacity.available_unit + " after " + vm.inputs.scenario_settings.compression_factor + "% compression becomes " + vm.result.disk_capacity.available + " / " + compCalc.toFixed(1) + " = " + compData.toFixed(1) + vm.result.disk_capacity.available_unit;
        vm.tooltipDataDedup = compData.toFixed(1) + "" + vm.result.disk_capacity.available_unit + " after " + vm.inputs.scenario_settings.dedupe_factor + "% dedupe becomes " + compData.toFixed(1) + " / " + dedupeCalc.toFixed(1) + " = " + vm.result.disk_capacity.effective + vm.result.disk_capacity.available_unit;
      }
      vm.onHypervisorChanged = function () {
        // get the nodes list supprted for selected hypervisor
        hxNodesList = utilService.filteredList(fixedConfingFilterData.node_details, function (node) {
          return node.hypervisor.indexOf(vm.inputs.scenario_settings.hypervisor) !== -1;
        });
        /* if(vm.inputs.scenario_settings.hypervisor === 'hyperv') {
          vm.inputs.node_properties.compute_node = '';
          vm.inputs.node_properties.no_of_computes = 0;
        } */
        //updates the options in UI
        vm.onNodeTypeChanged();
      };

      vm.onNodeTypeChanged = function () {
        filteredHXNodesList = utilService.filteredList(hxNodesList, function (node) {
          return node.node_type === vm.inputs.node_properties.nodeType;
        });
        // this is to manually / implicitly trigger the change event so that data will be updated appopriately
        updateByNodesList();
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
        vm.computeNodesList = hxNodeData.compute_nodes;

        // compute node should be empty when hyperv is selected
        var computeNodeNames = vm.computeNodesList.map(function (computeNode) {
          return computeNode.name;
        });
        vm.options.computeNodeTypes = getOptionsInDDFormat(computeNodeNames);
        vm.options.computeNumNodes = getOptionsInDDFormat([]);
        // vm.options.hxNumNodes = getOptionsInDDFormat(hxNodeData.num_nodes[vm.inputs.scenario_settings.hypervisor]);
        vm.options.cpu = getOptionsInDDFormat(hxNodeData.cpu_options);
        vm.options.ram = getOptionsInDDFormat(hxNodeData.ram_options);
        // vm.options.diskDrives = getOptionsInDDFormat(hxNodeData.hdd_slots);

        // var partsToBeExcluded = fixedConfingFilterData.excluded_parts[vm.inputs.scenario_settings.hypervisor];
        var totalHddOptions = hxNodeData.hdd_options;
        var totalSsdOptions = hxNodeData.ssd_options;
        var supprtedHddOptions = utilService.filteredList(totalHddOptions, function (option) {
          // given option should not be in exclude list
          return option[4].indexOf(vm.hypervisor) !== -1;
          // return partsToBeExcluded.indexOf(option[1]) === -1;
        });
        // var supprtedSsdOptions = utilService.filteredList(totalSsdOptions, function (option) {
        //   given option should not be in exclude list
        //   return partsToBeExcluded.indexOf(option[1]) === -1;
        // });

        vm.options.diskSizes = getOptionsInDDFormat(supprtedHddOptions);
        vm.options.ssdOptions = getOptionsInDDFormat(totalSsdOptions);
        vm.options.rf = getOptionsInDDFormat(hxNodeData.rf, "RF ");
        vm.onDiskDriveChange(vm.inputs.node_properties.disk_capacity)
        updateComputeNodes(vm.inputs.node_properties.no_of_nodes);
      };

      vm.onRFChanged = function (rfVal) {
        vm.inputs.scenario_settings.ft = (vm.inputs.scenario_settings.ft < rfVal) ? vm.inputs.scenario_settings.ft : (rfVal - 1);
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

        updateComputeNodes(vm.inputs.node_properties.no_of_nodes);

      };

      vm.onComputeNodeTypeChanged = function (computeNodeType) {
        var computeNodeData = utilService.getItemByPropVal(vm.computeNodesList, 'name', computeNodeType);
        if (computeNodeData) {
          vm.options.cpu = getOptionsInDDFormat(computeNodeData.cpu_options);
          vm.options.ram = getOptionsInDDFormat(computeNodeData.ram_options);
        }

        // setting default CPU value(E5-2650v4) for M4 nodes
        if (utilService.hasText(vm.inputs.node_properties.node, 'M4')) {
          vm.inputs.node_properties.cpu = DEFAULT_INPUTS.node_properties.cpu;
        } else { // setting default CPU value for M5 nodes
          vm.inputs.node_properties.cpu = "6130";
        }

      };

      function updateComputeNodes(hxNodeCount) {
        var computeNodes;
        if (vm.options.computeNodeTypes.length === 0) {
          // if there are no compute nodes, then number of compute should be 0
          computeNodes = [0]
        } else {
          hxNodeCount = hxNodeCount || 0;
          computeNodes = [];
          var maxHXNodesCount = vm.options.hxNumNodes[vm.options.hxNumNodes.length - 1].value;
          var maxComputeNodes;
          // var maxComputeNodes = Math.min( 2*hxNodeCount, maxHXNodesCount);
          if (vm.inputs.scenario_settings.hypervisor === 'hyperv') {
            maxComputeNodes = vm.inputs.node_properties.no_of_nodes;
          } else if (vm.inputs.node_properties.node.indexOf('NVME') !== -1) {
            maxComputeNodes = vm.inputs.node_properties.no_of_nodes;
          } else {
            maxComputeNodes = (2 * vm.inputs.node_properties.no_of_nodes) > 32 ? 32 : (2 * vm.inputs.node_properties.no_of_nodes);
          }
          for (var i = 0; i <= maxComputeNodes; i++) {
            computeNodes.push(i);
          }
        }
        vm.options.computeNumNodes = getOptionsInDDFormat(computeNodes);
      }

      vm.onHxNodeCountChanged = function (hxNodeCount) {
        updateComputeNodes(hxNodeCount);
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

      vm.onInputChanged = function () {
        $timeout(function () {
          vm.canEnableApply = _canEnableApply();
        });
      }

      function _canEnableApply() {
        if (vm.dedupeError || vm.compressionError) {
          return false;
        }
        var settingsData = vm.inputs.scenario_settings;
        var nodePropsData = vm.inputs.node_properties;
        var prop, val;
        for (prop in settingsData) {
          val = settingsData[prop];
          if (val === undefined || val === null || val === '') {
            return false;
          }
        }
        for (prop in nodePropsData) {
          if (prop === 'compute_node') {
            continue;
          }
          val = nodePropsData[prop];
          if (val === undefined || val === null || val === '') {
            console.log(prop, val);
            return false;
          }
        }
        return true;
      }

      vm.onApply = function () {
        var reqObj = getRequestObject();

        ReverseSizerService.reverseSize(reqObj).then(function (response) {
          vm.result = response;
          vm.result.enableDownload = true;
          vm.rfvalue = '(RF ' + reqObj.scenario_settings.rf + ')';
          vm.comprDedupeCalc();
        });

      }

      vm.downloadReport = function () {
        var reqObj = getRequestObject();
        var userInfo = appService.getUserInfo();
        var payload = Object.assign({}, reqObj, {
          results: vm.result,
          username: userInfo.name
        });
        nodeService.downloadFixedConfigScenarioReport(payload).then(function (data) {
          var url = APP_ENV.baseUrl + '/hyperconverged/scenarios/report/download?fname=' + encodeURIComponent(data.filename);

          // this is to avoid popup blocker
          var link = angular.element('#hidden-download-trigger').attr('href', url).get(0).click();

          // Google analytics :: Tracking the count of Sizing Report Downloads
          ga('send', 'event', {
            eventCategory: HX_ANALYTICS_EVENTS.CATEGORY.DOWNLOADS.UI_LABEL,
            eventAction: HX_ANALYTICS_EVENTS.CATEGORY.DOWNLOADS.ACTIONS.HX_FIXED_CONFIG_SIZING_REPORT,
            eventLabel: HX_ANALYTICS_EVENTS.CATEGORY.DOWNLOADS.LABELS.HX_FIXED_CONFIG_SIZING_REPORT,
            transport: 'beacon'
          });
        });
      };

      function getRequestObject() {
        var reqObj = utilService.getClone(vm.inputs);
        reqObj.scenario_settings.threshold = parseInt(reqObj.scenario_settings.threshold);
        reqObj.node_properties.cache_size = getOutputVal(reqObj.node_properties.cache_size, SEPERATOR);
        reqObj.node_properties.disk_capacity = getOutputVal(reqObj.node_properties.disk_capacity, SEPERATOR);
        return reqObj;
      }

      function preInit() {
        init();
        $timeout(function () {
          ReverseSizerService.getNodeOptions().then(function (response) {
            fixedConfingFilterData = response;
            init();
            vm.onHypervisorChanged();
          });
        });
      }

      function init() {
        vm.inputs = Object.assign({}, utilService.getClone(DEFAULT_INPUTS));
        // in case of optimal scenario, node_properties will not be avialble in settings
        vm.inputs.node_properties = vm.inputs.node_properties || DEFAULT_INPUTS.node_properties;
        vm.inputs.node_properties.nodeType = vm.inputs.node_properties.nodeType || defaultNodeType;

        vm.inputs.node_properties.disk_capacity = getInputVal(vm.inputs.node_properties.disk_capacity, SEPERATOR);
        vm.inputs.node_properties.cache_size = getInputVal(vm.inputs.node_properties.cache_size, SEPERATOR);
      }

      function updateByNodesList() {
        var nodeNames = filteredHXNodesList.map(function (node) { return node.node_name; });
        vm.options.hxNodeTypes = getOptionsInDDFormat(nodeNames);
        if (vm.options.hxNodeTypes.length) {
          var selectedNode = vm.options.hxNodeTypes[0].value;
          vm.onHXNodeTypeChanged(selectedNode);
        }
      }

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

      function getArray(val) {
        var list = []; val = val || 0;
        for (var i = 0; i < val; i++) {
          list.push(i);
        }
        return list;
      }

      function getOptionsInDDFormat(list, prefixStr) {
        prefixStr = prefixStr || "";
        list = list || [];
        return list.map(function (item) {
          var isArray = (item instanceof Array);
          return {
            label: prefixStr + (isArray ? item[0] : item),
            value: isArray ? item.join(SEPERATOR) : item
          }
        })
      }

      $scope.$on('$viewContentLoaded', function (event, viewConfig) {
        preInit();
      });



    }]);

  angular
    .module('hyperflex')
    .controller("ReverseSizerPopupController", ["$scope", "$uibModalInstance", function ($scope, $uibModalInstance) {
      var vm = this;

      vm.closeEvent = function () {
        $uibModalInstance.close();

      }
    }]);


})();


