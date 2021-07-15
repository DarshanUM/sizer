(function () {
  "use strict";

  angular
    .module('hyperflex')
    .controller("WorkloadController", ['$scope', '$rootScope', '$stateParams', '$timeout', '$uibModal', 'HX_ANALYTICS_EVENTS', 'FEATURES', 'utilService', 'filtersService', 'APP_ENV', 'workloadService', 'appService', 'nodeService', 'scenarioService', 'ScenarioDataProcessor', function ($scope, $rootScope, $stateParams, $timeout, $uibModal, HX_ANALYTICS_EVENTS, FEATURES, utilService, filtersService, APP_ENV, workloadService, appService, nodeService, scenarioService, ScenarioDataProcessor) {
      // internal/private variables
      var vm = $scope;
      var prevThresholdVal;
      var prevNodeChoiceVal;
      var prevSizingOptionVal;
      var prevDiskOptionVal;
      var prevHypervisorOptionVal;
      var ctoOnlyFilters = {};
      var regularFilters = {};
      var fixedConfingFilterData = null;

      // Hyperv is not allowed if one of workloads of scenario is having replication / stretch cluster enabled
      vm.isHyperVSelectionAllowed = true;


      vm.versionInfo = appService.getSizerVersion();
      vm.FEATURES = FEATURES;

      vm.tooltips = {
        "fixedConfig": "Regular sizing workflow helps identify the cost optimal HX configuration for a set of workloads. This workflow starts with a fixed HX configuration and helps validate whether a given set of workloads will run on it or not.",
        "fixedConfigDisabled": "Fixed Config Sizing is not supported for Stretch Cluster, Replication workloads or Epic Workloads.",
        "hypervDisabled": "Replication, Stretch Cluster and vGPU are not supported in Hyper-V clusters. Delete any workloads that have Replication, Stretch Cluster, vGPU before choosing the Hyper-V option."
      }

      vm.customTabs = [{
        label: 'Global Settings',
        value: 'global_setting'
      }, {
        label: 'Node Filter',
        value: 'node_filter'
      }];
      vm.currentCustomTab = vm.customTabs[0].value;


      vm.isViewLoaded = false;
      vm.fiPackageOptions = [];
      vm.filterDetails = {
        showFilterNodes: false,
        nodeTypeData: {
          title: "Hyperflex Nodes",
          options: [],
          model: [],
          disabledOptions: [],
          hiddenOptions: [],
          optionSuffix: '',
          includeSelectAll: true
        },
        computeNodesData: {
          title: "Compute Nodes",
          options: [],
          model: [],
          optionSuffix: '',
          includeSelectAll: true
        },
        cpuClockData: {
          title: "Clock (GHz)",
          options: [],
          model: [],
          optionSuffix: '',
          includeSelectAll: true
        },
        cpuTypeData: {
          title: "CPU (Cores, GHz)",
          options: [],
          model: [],
          optionSuffix: '',
          includeSelectAll: true
        },
        ramSlotsData: {
          title: "RAM Slots",
          options: [],
          model: [],
          optionSuffix: '',
          includeSelectAll: true
        },
        ramMemoryData: {
          title: "RAM",
          options: [],
          model: [],
          optionSuffix: '',
          includeSelectAll: true
        },
        diskCapacity: {
          title: "Disk Capacity",
          options: [],
          model: [],
          optionSuffix: '',
          includeSelectAll: true
        },
        gpuData: {
          title: "GPU",
          options: [],
          model: [],
          optionSuffix: '',
          includeSelectAll: true

        },
        capacityData: {
          title: "Cache Capacity",
          options: [],
          model: [],
          optionSuffix: '',
          includeSelectAll: true
        }
      };

      vm.thresholdOtions = [
        {
          key: 0,
          value: 'Conservative'
        },
        {
          key: 1,
          value: 'Standard'
        },
        {
          key: 2,
          value: 'Aggressive'
        }
      ];

      vm.nodeChoiceOtions = [
        {
          key: true,
          value: 'Hyperconverged &  Compute'
        },
        {
          key: false,
          value: 'Hyperconverged Only'
        }
      ]

      vm.scenario = {};
      vm.rawScenarioData = [];
      vm.totalWorkloads = [];
      vm.quickEditData = {};
      $rootScope.root.currentView = 'CLUSTER_VIEW';
      vm.clusterIndex = 0;
      vm.selectedWorkload;
      // vm.thresholdDefinitions = THRESHOLD_DEFINITION;
      vm.filterContainerHeight = window.innerHeight - 450;
      vm.workloadContainerHeight = window.innerHeight - 80;
      vm.nodeContainerHeight = window.innerHeight - 140;
      vm.mainContainerHeight = window.innerHeight - 100;
      vm.globalSettingHeight = window.innerHeight - 120;
      vm.noResultHeight = window.innerHeight - 50;
      vm.innerNoResultHeight = window.innerHeight - 180;
      vm.globalsettingHeight = window.innerHeight - 100;
      $rootScope.root.isCurrentScenarioUptodate = true;
      vm.moreSelection = false;
      vm.selectionCancel = true;
      vm.isThereUnsavedResults = false;
      vm.testData = {};
      vm.testData.hasSizingErrorClosed = false;
      vm.testData.hasTempSizingErrorClosed = false;

      /* User values */
      vm.minDiscountValue = 0;
      vm.maxDiscountValue = 50;
      vm.numDiscountBundleError = false;
      vm.numDiscountCtoError = false;

      /* Min length and Max length validation */
      vm.discountBundleChanged = function (e, inputVal) {
        var val = (inputVal == undefined) ? parseInt(e.target.value) : inputVal;
        vm.numDiscountBundleError = (isNaN(val) || (val == undefined) || val < vm.minDiscountValue || val > vm.maxDiscountValue);
      }

      vm.discountCtoChanged = function (e, inputVal) {
        var val = (inputVal == undefined) ? parseInt(e.target.value) : inputVal;
        vm.numDiscountCtoError = (isNaN(val) || (val == undefined) || val < vm.minDiscountValue || val > vm.maxDiscountValue);
      }

      /*Chart Related*/
      var chartColorsMapping = {
        wl_util: "#f00",
        ft_util: "#0f0",
        site_ft_util: "#000"
      };
      Chart.defaults.global.tooltipFontSize = 6;
      vm.utilizationChartConfig = {
        labels: ["Workload", "FT Buffer", "Free", "Not Usable"],
        colors: ["#c0ea80", "#faf878", "#aaccee", "#b0b0b0"],
        colorsNormal: ["#6cc04a", "#EB6D00", "#c4c4c4"],
        colorsMax: ["#fb5f5d", "#e1e1e1"],
        colorThreshold: 80,
        dataset: {
          borderColor: ["#000", "#000", "#000"],
          borderWidth: [0, 0, 0, 0],
          hoverBackgroundColor: ["#6cc04a", "#EB6D00", "#c4c4c4"]
        },
        options: {
          responsive: true,
          segmentShowStroke: false,
          showTooltips: false,
          fontSize: 12,
          cutoutPercentage: 85,
          /*legend: {
            display: true,
            position: 'bottom',
            fullWidth: false,
          },*/
          tooltips: {
            enabled: false
          }
        }
      };

      vm.navigateToMain = function () {
        var scenarioId = $stateParams.id;
        var pageData = appService.getPageData();
        nodeService.getScenarioById(scenarioId).then(function (response) {
          var scenData = utilService.filteredList(pageData.scenarioList, function (scen) {
            return scen && scen.id === response.id;
          })[0];
          if (scenData) {
            if (scenData.updated_date !== response.updated_date) {
              var indexdat;
              pageData.scenarioList = utilService.filteredList(pageData.scenarioList, function (scen, index) {
                if (!scen) {
                  return true;
                }
                return scen.id !== response.id;
              });
              pageData.scenarioMap = {
                'active': {},
                'fav': {},
                'arch': {}
              }
              pageData.scenarioList = [response].concat(pageData.scenarioList);
            } else {
              pageData.scenarioList = pageData.scenarioList.map(function (scen) {
                if (scen && scen.id === scenarioId) {
                  scen = response;
                }
                return scen;
              });
            }
          }
          appService.setHomeDispFlag(false);
          appService.setPageData(pageData);
          appService.gotoView('scenario');
        })
      }

      vm.setCurrentCustomTab = function (tab) {
        vm.currentCustomTab = tab.value;
      }

      /*This event will be fired from resize-scenario directive on success of resize*/
      $scope.$on("RESIZE_SCENARIO", function (event, data) {
        if ("SUCCESS" === data.status) {
          // getScenarioDetails();
          addDatacentresEpicWl(data.data);
          checkHXVersion(data.data);
          updateScenarioToUI(data.data, null);
        }
      });

      vm.hasAsterisk = function (str) {
        return str ? (str.indexOf('*') !== -1) : false;
      };

      vm.closeSizingErrorMessage = function () {
        vm.testData.hasSizingErrorClosed = vm.testData.hasTempSizingErrorClosed = true;
      };

      vm.downloadReport = function (e, fiPackagesCount, fiPackageName, language, slides) {
        e.preventDefault();
        var scenarioId = $stateParams.id;
        nodeService.downloadScenarioReport(scenarioId, vm.scenario.currentResult, fiPackagesCount, fiPackageName, language, slides).then(function (data) {
          var url = APP_ENV.baseUrl + '/hyperconverged/scenarios/report/download?fname=' + encodeURIComponent(data.filename);
          // vm.reportUrl = url;
          // window.open(url);

          // this is to avoid popup blocker
          var link = angular.element('#hidden-download-trigger').attr('href', url).get(0).click();

          // Google analytics :: Tracking the count of Sizing Report Downloads
          ga('send', 'event', {
            eventCategory: HX_ANALYTICS_EVENTS.CATEGORY.DOWNLOADS.UI_LABEL,
            eventAction: HX_ANALYTICS_EVENTS.CATEGORY.DOWNLOADS.ACTIONS.HX_SIZING_REPORT,
            eventLabel: HX_ANALYTICS_EVENTS.CATEGORY.DOWNLOADS.LABELS.HX_SIZING_REPORT,
            transport: 'beacon'
          });
        });
      };

      vm.onDownloadPopup = function (type, event) {
        if (vm.totalWorkloads.length === 0) {
          if (type === 'bom') {
            vm.downloadBOM();
          } else {
            vm.downloadReport(event);
          }
        } else {
          $uibModal.open({
            templateUrl: 'views/scenario_details/modals/download-bom.html',
            backdrop: 'static',
            size: 'sm',
            controller: ['$scope', 'fiOptions', 'fiPackageOptions', 'fiWorkloadLength', 'stretchCheck', 'nodeCheck', function ($scope, fiOptions, fiPackageOptions, fiWorkloadLength, stretchCheck, nodeCheck) {
              $scope.fiPackagesCount = 0;
              $scope.fiPackageName = fiPackageOptions.length ? fiPackageOptions[0].value : '';
              $scope.fiOptions = fiOptions;
              $scope.fiPackageOptions = fiPackageOptions;
              $scope.isStretch = stretchCheck;
              $scope.nodeCheck = nodeCheck;
              $scope.errorMsg = ''
              $scope.showLableRC = fiWorkloadLength ? true : false;
              $scope.title = type === "report" ? 'Sizing Report' : 'BOM';
              var optimalItemsPages = ["Agenda", "Lowest_Cost/All-Flash/All NVMe Comparison", "Sizing Report", "Lowest_Cost Sizing Report", "All-Flash Sizing Report", "All NVMe Sizing Report", "Workload Calculation", "Node Calculation", "Workload Summary", "Glossary"];
              var fixedItemsPages = ["Agenda", 'Sizing Report', 'Fixed Config Sizing Report', "Workload Calculation", "Node Calculation", "Workload Summary", "Glossary"];
              // $scope.ItemPages = ['Agenda', 'Lowest_Cost/All-Flash Comparison', 'Sizing Report', 'Lowest_Cost Sizing Report', 'All-Flash Sizing Report', 'Workload Calculation', 'Node Calculation', 'UCS Layout', 'Workload Summary', 'Glossary'];
              $scope.ItemPages = vm.scenario.sizing_type === 'optimal' ? optimalItemsPages : fixedItemsPages;
              var optimalItemsSelected = ['Agenda', 'Sizing Report', 'Lowest_Cost Sizing Report', 'All-Flash Sizing Report', 'All NVMe Sizing Report', 'Workload Summary'];
              var fixedItemsSelected = ['Agenda', 'Sizing Report', 'Fixed Config Sizing Report', 'Workload Summary'];
              $scope.selectedItems = vm.scenario.sizing_type === 'optimal' ? optimalItemsSelected : fixedItemsSelected;
              $scope.language = "english";
              $scope.deleteSelection = function (items) {
                $scope.selectedItems = utilService.filteredList($scope.selectedItems, function (sel) {
                  return sel !== items;
                });
              }
              $scope.packageUpdate = function () {
                $scope.errorMsg = '';
                if ($scope.fiPackageName === 'HX-FI-64108') {
                  if ($scope.isStretch) {
                    $scope.errorMsg += 'Warning: This HX-FI-64108 FI is currently not supported for Stretched cluster. \n'
                  }
                  if ($scope.nodeCheck) {
                    $scope.errorMsg += 'Warning: This HX-FI-64108 FI is currently supported only upto 32 nodes with any combination of converged / compute only nodes'
                  }
                }
              }
              $scope.enableCheck = function () {
                if (type === "report" && $scope.selectedItems.length === 0) {
                  return true;
                }
                return false;
              }
            }],
            resolve: {
              fiOptions: function () {
                var list = [];
                var count = vm.scenario.totalClusters.length;
                for (var i = 0; i <= count; i++) {
                  list.push(i);
                }
                return list;
              },
              fiPackageOptions: function () {
                return vm.fiPackageOptions;
              },
              fiWorkloadLength: function () {
                return vm.totalWorkloads.length;
              },
              stretchCheck: function () {
                var stretchCLuster = utilService.filteredList(vm.scenario.totalClusters, function (cluster) {
                  return cluster.isStretchCluster
                });
                return stretchCLuster.length > 0;
              },
              nodeCheck: function () {
                var nodeCount32 = utilService.filteredList(vm.scenario.totalClusters, function (cluster) {
                  return cluster.totalNodesCount > 32;
                });
                return nodeCount32.length > 0;
              }
            }
          }).result.then(function (data) {
            if (type === 'bom') {
              vm.downloadBOM(data.fiPackagesCount, data.fiPackageName);
            } else if (!vm.totalWorkloads.length) {
              vm.downloadReport(event, undefined, undefined, data.language);
            } else {
              vm.downloadReport(event, data.fiPackagesCount, data.fiPackageName, data.language, data.selectedItems);
            }
          }, function () {
            // console.log("dismissed");
          });
        }
      };



      vm.globalSettingModal = function () {
        $uibModal.open({
          templateUrl: 'views/scenario_details/modals/fixed_config.html',
          backdrop: 'static',
          size: 'sm',
          controller: 'FixedSizingController',
          controllerAs: 'fixedCtrl',
          resolve: {
            scenarioObj: function () {
              var scenario = utilService.getClone(vm.scenario);
              /* if (hypervisorSelected) {
                scenario.aggregate.settings.hypervisor = hypervisorSelected;
              } */
              return scenario;
            },
            fixedConfingFilterData: function () {
              return fixedConfingFilterData;
            }
          }
        }).result.then(function (result) {
          fixedConfingFilterData = result.fixedConfingFilterData;
          updateScenarioToUI(result.scenario, result.scenario.settings_json[0].result_name);
          vm.scenario.excludeWls = fixedConfingFilterData.excluded_wls[vm.scenario.aggregate.settings.hypervisor];
        }, function (data) {
          console.log("dismissed");
          fixedConfingFilterData = data;
          vm.scenario.excludeWls = fixedConfingFilterData.excluded_wls[vm.scenario.aggregate.settings.hypervisor];
        });
      };

      vm.noShowPost = function () {
        vm.infoPageFlag = false;
        if (vm.scenario.noShowFlag) {
          var req;
          if (vm.scenario.sizing_type === 'optimal') {
            req = {
              'optimal_sizing_desc': false
            }
          } else {
            req = {
              'fixed_sizing_desc': false
            }
          }
          nodeService.userDataPost(req).then(function (response) {
            vm.userData = response;
            vm.scenario.noShowFlag = false;
            console.log('No show');
          });
        }
      }

      function showHypervisorChangeWarningInCustomizeWindow(onConfirm, onDismiss) {
        $uibModal.open({
          templateUrl: 'views/scenario_details/modals/hyperview_confirm.html',
          backdrop: 'static',
          size: 'sm',
          controller: 'WorkloadController',
          resolve: {
          }
        }).result.then(onConfirm, onDismiss);
      };

      vm.optimalDialog = function () {
        $uibModal.open({
          templateUrl: 'views/scenario_details/modals/optimal_confirm.html',
          backdrop: 'static',
          size: 'sm',
          controller: 'WorkloadController',
          resolve: {
          }
        }).result.then(function (result) {
          var reqObject = ScenarioDataProcessor.getScenarioInPutRequestFormat(vm.scenario);
          vm.scenario.sizing_type = 'optimal';
          reqObject.sizing_type = 'optimal';
          reqObject.overwrite = true;
          var scenarioToUpdate = vm.scenario;
          scenarioToUpdate.aggregate.settings.filters = getFilterValuesFromUI();
          reqObject.wl_list.forEach(function (workload) {
            for (var prop in workload) {
              if (prop.indexOf("_ui") === 0) {
                delete workload[prop];
              }
            }
            delete workload['clusterList'];
            delete workload.citrix;
            delete workload.horizon;
            delete workload['hot'];
            delete workload['warm'];
            delete workload['cold'];
            delete workload['frozen'];
            delete workload['admin'];
            delete workload['indexer'];
            delete workload['search'];
            delete workload['app_rf_dup'];
            if (workload.wl_type === "EPIC") {
              delete workload['concurrent_user_pcnt'];
              delete workload['num_clusters'];
              delete workload['dc_name'];
            }
          });
          reqObject.wl_list = utilService.filteredList(reqObject.wl_list, function (wl) {
            return !((wl.wl_type === 'VDI' || wl.wl_type === 'RDSH') && wl.hasOwnProperty('primary_wl_name'));
          });
          scenarioService.save({ id: vm.scenario.id }, reqObject).$promise.then(function (updatedScenario) {
            addDatacentresEpicWl(updatedScenario);
            checkHXVersion(updatedScenario);
            // updateQuickEditData();
            updateScenarioToUI(updatedScenario, 'Lowest_Cost');
            // getScenarioDetails();
            vm.infoPageFlag = vm.scenario.sizing_type === 'fixed' ? vm.userData.fixed_sizing_desc : vm.userData.optimal_sizing_desc;
            if (!vm.infoPageFlag) {
              $timeout(function () {
                vm.closeMask();
              }, 100)
            } else {
              $('.noResultIndex,.plusBtn').css('pointer-events', 'none');
            }
          }, function () {
            vm.infoPageFlag = vm.scenario.sizing_type === 'fixed' ? vm.userData.fixed_sizing_desc : vm.userData.optimal_sizing_desc;
            if (!vm.infoPageFlag) {
              $timeout(function () {
                vm.closeMask();
              }, 100)
            } else {
              $('.noResultIndex,.plusBtn').css('pointer-events', 'none');
            }
          });
        }, function () {
          console.log("dismissed");
        });
      }

      vm.fixedDialog = function () {
        $uibModal.open({
          templateUrl: 'views/scenario_details/modals/fixed_confirm.html',
          backdrop: 'static',
          size: 'sm',
          controller: 'WorkloadController',
          resolve: {
          }
        }).result.then(function (result) {
          vm.showFixedPopup();
        }, function () {
          console.log("dismissed");
        });
      }

      vm.closeMask = function () {
        $('.noResultBoxPopup,.got_it_btn,.remove_icon_position').hide();
        $('.begin_arrow_position,.custom_arrow_position,.fixed_message,.result_message').hide();
        $('.begin_arrow_position,.custom_arrow_position,.optimal_message').hide();
        $('.noResultIndex,.plusBtn').css('pointer-events', 'unset')
        $('.plusBtn').removeClass('maskIcon');
      }

      vm.downloadBOM = function (fiPackagesCount, fiPackageName) {
        var scenarioId = $stateParams.id;
        nodeService.downloadBOM(scenarioId, vm.scenario.currentResult, fiPackagesCount, fiPackageName).then(function (data) {
          var url = APP_ENV.baseUrl + '/hyperconverged/scenarios/bom/download?fname=' + encodeURIComponent(data.filename);
          // vm.reportUrl = url;
          // window.open(url);

          // this is to avoid popup blocker
          var link = angular.element('#hidden-download-trigger').attr('href', url).get(0).click();

          // Google analytics :: Tracking the count of BOM Report Downloads
          ga('send', 'event', {
            eventCategory: HX_ANALYTICS_EVENTS.CATEGORY.DOWNLOADS.UI_LABEL,
            eventAction: HX_ANALYTICS_EVENTS.CATEGORY.DOWNLOADS.ACTIONS.HX_BOM_REPORT,
            eventLabel: HX_ANALYTICS_EVENTS.CATEGORY.DOWNLOADS.LABELS.HX_BOM_REPORT,
            transport: 'beacon'
          });
        });
      };

      /*QUICK EDIT WORKLOAD RELATED CODE*/
      vm.enableQuickEdit = function (event, workload, quickEditData) {
        event.stopPropagation();
        event.stopImmediatePropagation();
        quickEditData.showQuickEdit = true;
      };

      vm.quickEditCancel = function (event, workload, quickEditData) {
        event.stopPropagation();
        event.stopImmediatePropagation();
        quickEditData.value = workload[quickEditData.propName];
        quickEditData.showQuickEdit = false;
        quickEditData.hasFloatError = false;
        quickEditData.hasRangeError = false;
      };

      vm.quickEditSave = function (event, workload, quickEditData) {
        event.stopPropagation();
        event.stopImmediatePropagation();
        quickEditData.showQuickEdit = false;
        var prevVal = workload[quickEditData.propName];
        workload[quickEditData.propName] = quickEditData.value;

        // this is to move the in edit workload to the top in the list
        var newScenarioObj = utilService.getClone(vm.scenario);
        for (var i = 0; i < newScenarioObj.aggregate.workloads.length; i++) {
          if (newScenarioObj.aggregate.workloads[i].wl_name === workload.wl_name) {
            newScenarioObj.aggregate.workloads.splice(i, 1);
          }
        }
        newScenarioObj.aggregate.workloads.unshift(workload);

        updateScenario(null, null, function () {
          quickEditData.value = workload[quickEditData.propName] = prevVal;
        }, newScenarioObj, true);
      };

      function updateQuickEditData() {
        vm.quickEditData = {};
        var propName;
        var workloadFields;
        var field;
        for (var i = 0; i < vm.scenario.aggregate.workloads.length; i++) {
          propName = getQuickEditPropName(vm.scenario.aggregate.workloads[i].wl_type);
          workloadFields = workloadService.fields[vm.scenario.aggregate.workloads[i].wl_type];
          field = getFieldByModelName(propName, workloadFields, false);
          vm.quickEditData[vm.scenario.aggregate.workloads[i].wl_name] = {
            showQuickEdit: false,
            propName: propName,
            value: vm.scenario.aggregate.workloads[i][propName],
            min: field ? field.min : 0,
            max: field ? field.max : 0,
            hasFloatError: false,
            hasRangeError: false
          };
        }
      }

      vm.onQuickEditInputChanged = function (quickEditField) {
        /*to not allow decimal numbers*/
        quickEditField.hasFloatError = (parseInt(quickEditField.value) != quickEditField.value);
        quickEditField.hasRangeError = (quickEditField.value === undefined || quickEditField.value === null) ||
          (quickEditField.value < quickEditField.min || quickEditField.value > quickEditField.max);
      }

      function getFieldByModelName(modelName, workloadFields, includeDependentFields) {
        var stepIndex, fieldIndex, currentStep, currentField;
        // updating step fields
        for (stepIndex = 1; stepIndex < workloadFields.steps.length; stepIndex++) {
          currentStep = workloadFields.steps[stepIndex];
          for (fieldIndex = 0; fieldIndex < currentStep.fields.length; fieldIndex++) {
            currentField = currentStep.fields[fieldIndex];
            if (currentField.modelName === modelName) {
              return currentField;
            }
          }

          if (includeDependentFields && currentStep.dependentFields) {
            for (fieldIndex = 0; fieldIndex < currentStep.dependentFields.length; fieldIndex++) {
              currentField = currentStep.dependentFields[fieldIndex];
              if (currentField.modelName === modelName) {
                return currentField;
              }
            }
          }
        }
      }
      function getQuickEditPropName(wlType) {
        var fieldName = "";
        switch (wlType) {
          case "VDI":
            fieldName = "num_desktops"; break;
          case "VSI":
            fieldName = "num_vms"; break;
          case "DB":
            fieldName = "num_db_instances"; break;
          case "ORACLE":
            fieldName = "num_db_instances"; break;
          case "ROBO":
            fieldName = "num_vms"; break;
          case "CONTAINER":
            fieldName = "num_containers"; break;
          case "AIML":
            fieldName = "num_data_scientists"; break;

        }
        return fieldName;
      }

      /*WORKLOAD RELATED CODE*/
      vm.addWorkload = function () {
        openWorkloadModal('Add Workload', null, "views/scenario_details/modals/workload.html", 'md');
      };

      vm.editWorkload = function (workloadToUpdate) {
        openWorkloadModal('Edit Workload', JSON.parse(JSON.stringify(workloadToUpdate)), "views/scenario_details/modals/workload.html", 'md');
      };

      vm.cloneWorkload = function (workloadToClone) {
        workloadToClone = angular.extend({}, workloadToClone);
        workloadToClone.wl_name = workloadToClone.wl_name + "_Copy";
        openWorkloadModal('Clone Workload', workloadToClone, "views/scenario_details/modals/clone_workload.html", 'sm');
      };

      vm.deleteWorkload = function (workloadToDelete) {
        openWorkloadModal('Delete Workload', workloadToDelete, "views/scenario_details/modals/delete_workload.html", 'sm');
      };


      vm.nextSteps = function () {
        $scope.globalSetting = true;
        $scope.globalSetup = true;
        console.log('inner')
      }



      function getNonErrorResult(rawScenarioData, currentResult) {
        var settingsList = rawScenarioData.settings_json || [];
        var errorsList = rawScenarioData.errors || rawScenarioData.temp_error || [];
        var resultName = currentResult;
        // check if there is a non-error result
        if (errorsList.length !== settingsList.length) {
          // if there is an error in the current result
          if (utilService.getItemByPropVal(errorsList, "result_name", resultName)) {
            resultName = (resultName === "Lowest_Cost") ? "All-Flash" : "Lowest_Cost";
          }
        }
        return resultName;
      }

      function openWorkloadModal(modalTitle, workload, modalTemplate, modalWindowSize) {


        var workloadModal = $uibModal.open({
          templateUrl: modalTemplate,
          controller: 'WorkloadModalController',
          controllerAs: 'ctrl',
          size: modalWindowSize,
          backdrop: 'static',
          keyboard: false,
          resolve: {
            workloadData: function () {
              // this is to keep the readonly property to default data given in workload-data.js
              var workloadData = JSON.parse(JSON.stringify(workloadService.fields));
              // var supportedWorkloads = vm.scenario.aggregate.settings.node_properties.workload_options;
              // var totalWorkloadTypesAvailable = Object.keys(workloadData);
              // if(supportedWorkloads) {
              //   totalWorkloadTypesAvailable.forEach( function(workloadType) {
              //     // remove the configutaion / options of this workload if not in supported list
              //     if( supportedWorkloads.indexOf(workloadType) === -1) {
              //       delete workloadData[workloadType];
              //     }
              //   } );  
              // }

              return workloadData;
            },
            srcWorkload: function () {
              return workload;
            },
            scenario: function () {
              return vm.scenario;
            },
            modalTitle: function () {
              return modalTitle;
            }
          }
        });



        workloadModal.result.then(function (scenarioData) {
          vm.selectedWorkload = null;
          addDatacentresEpicWl(scenarioData);
          var nonErrorResultName = getNonErrorResult(scenarioData, vm.scenario.currentResult);
          updateScenarioToUI(scenarioData, nonErrorResultName);
          window._$clonedFile = null;
          $timeout(function () {
            vm.closeMask();
          }, 100);
        }, function () {
          // console.log("dismissed");
          if (!vm.infoPageFlag) {
            $timeout(function () {
              vm.closeMask();
            }, 100);
          }
          window._$clonedFile = null;
        });
      };

      /*SCENARIO SETTINGS RELATED CODE*/
      vm.onHypervisorOptionClicked = function (event, hypervisorSelected) {
        if (!FEATURES.isHypervisorEnabled || (vm.scenario.aggregate.settings.hypervisor === hypervisorSelected)) { return; }
        event.stopPropagation();
        event.stopImmediatePropagation();

        if (hypervisorSelected === 'hyperv') {
          if (vm.scenario.sizing_type === 'fixed') {
            vm.showFixedPopup(hypervisorSelected);
          } else if (vm.scenario.sizing_type === 'optimal') {
            vm.scenario.aggregate.settings.hypervisor = hypervisorSelected;
            if (hypervisorSelected) {
              vm.scenario.aggregate.settings.hypervisor = hypervisorSelected;
              if (vm.scenario.aggregate.settings.hypervisor === 'hyperv') {
                // vm.scenario.aggregate.settings.heterogenous = false;
                vm.scenario.aggregate.settings.disk_option = vm.scenario.aggregate.settings.disk_option === "NVME" || vm.scenario.aggregate.settings.disk_option === "LFF" ? vm.scenario.aggregate.settings.disk_option : "ALL";
                vm.scenario.aggregate.settings.server_type = "M5";
                vm.scenario.aggregate.settings.hx_boost_conf = 'disabled';
                vm.scenario.aggregate.settings.hercules_conf = 'disabled';
              }
            }
            submitHypervisorChange();
          }
        } else if (hypervisorSelected === 'esxi') {
          vm.scenario.aggregate.settings.hypervisor = hypervisorSelected;
          submitHypervisorChange();
        }
        if (fixedConfingFilterData) {
          vm.scenario.excludeWls = fixedConfingFilterData.excluded_wls[vm.scenario.aggregate.settings.hypervisor];
        }

      };

      function submitHypervisorChange() {
        if (vm.scenario.aggregate.workloads.length === 0) {
          var dataToSave = ScenarioDataProcessor.getTempScenarioResultToSave(vm.scenario.currentResult, vm.scenario.aggregate.settings);
          nodeService.saveResults(vm.scenario.id, dataToSave).then(function (data) {
            ScenarioDataProcessor.updateSettingsOfRawScenarioData(dataToSave.settings_json);
          }, function () {
            vm.scenario.aggregate.settings.hypervisor = prevHypervisorOptionVal;
          });
        } else {
          updateScenario(vm.scenario.aggregate.settings.filters, function () {
          }, function () {
            vm.scenario.aggregate.settings.hypervisor = prevHypervisorOptionVal;
          });
        }

      };

      vm.onHeterogenousChanged = function () {
        if (vm.scenario.aggregate.workloads.length === 0) {
          var dataToSave = ScenarioDataProcessor.getTempScenarioResultToSave(vm.scenario.currentResult, vm.scenario.aggregate.settings);
          //dataToSave.settings_json = vm.scenario.aggregate.settings;
          // dataToSave.settings_json = getUnifiedSettings(vm.scenario.aggregate.settings);
          nodeService.saveResults(vm.scenario.id, dataToSave).then(function (data) {
            ScenarioDataProcessor.updateSettingsOfRawScenarioData(dataToSave.settings_json);
          }, function () {
            vm.scenario.aggregate.settings.heterogenous = prevNodeChoiceVal;
          });
        } else {
          updateScenario(null, function () {
          }, function () {
            vm.scenario.aggregate.settings.heterogenous = prevNodeChoiceVal;
          });
        }
        // console.log(" scenario.aggregate.settings.heterogenous ", vm.scenario.aggregate.settings.heterogenous)

      };

      vm.onThresholdChanged = function () {
        if (vm.scenario.aggregate.workloads.length === 0) {
          var dataToSave = ScenarioDataProcessor.getTempScenarioResultToSave(vm.scenario.currentResult, vm.scenario.aggregate.settings);
          //dataToSave.settings_json = vm.scenario.aggregate.settings;
          // dataToSave.settings_json = getUnifiedSettings(vm.scenario.aggregate.settings);
          nodeService.saveResults(vm.scenario.id, dataToSave).then(function (data) {
            ScenarioDataProcessor.updateSettingsOfRawScenarioData(dataToSave.settings_json);
          }, function () {
            vm.scenario.aggregate.settings.threshold = prevThresholdVal;
          });
        } else {
          updateScenario(null, function () {
          }, function () {
            vm.scenario.aggregate.settings.threshold = prevThresholdVal;
          });
        }
      };

      vm.onDiskOptionChanged = function () {
        var filters = getFilterValuesFromUI();
        var prevFilters = vm.scenario.aggregate.settings.filters;
        updateFilterOptions(filters, vm.scenario);
        var filters = getFilterValuesFromUI();
        vm.scenario.aggregate.settings.filters = filters;

        if (vm.scenario.aggregate.workloads.length === 0) {
          var dataToSave = ScenarioDataProcessor.getTempScenarioResultToSave(vm.scenario.currentResult, vm.scenario.aggregate.settings);
          // dataToSave.settings_json = vm.scenario.aggregate.settings;
          // dataToSave.settings_json = getUnifiedSettings(vm.scenario.aggregate.settings);
          nodeService.saveResults(vm.scenario.id, dataToSave).then(function (data) {
            ScenarioDataProcessor.updateSettingsOfRawScenarioData(dataToSave.settings_json);
          }, function () {
            vm.scenario.aggregate.settings.disk_option = prevDiskOptionVal;
            vm.scenario.aggregate.settings.filters = prevFilters;
          });
        } else {
          updateScenario(null, function () {
          }, function () {
            vm.scenario.aggregate.settings.disk_option = prevDiskOptionVal;
            vm.scenario.aggregate.settings.filters = prevFilters;
          });
        }
      };

      vm.onHypervisorOptionClickedInCustomize = function (event, hypervisorSelected) {
        if (!FEATURES.isHypervisorEnabled) { return; }
        event.stopPropagation();
        event.stopImmediatePropagation();
        if (vm.tempScenario.aggregate.settings.hypervisor !== hypervisorSelected) {
          /* CleanUp required */
          // showHypervisorChangeWarningInCustomizeWindow(function() {
          //   // confim callback 
          //   vm.tempScenario.aggregate.settings.hypervisor = hypervisorSelected;
          //   onHypervisorChangedInCustomize();
          // }, function() {
          //   // dismiss callback
          // })
          vm.tempScenario.aggregate.settings.hypervisor = hypervisorSelected;
          onHypervisorChangedInCustomize();
        }
        if (vm.tempScenario.aggregate.settings.hypervisor === 'hyperv') {
          if (vm.tempScenario.aggregate.settings.disk_option !== 'LFF' || vm.tempScenario.aggregate.settings.disk_option !== 'ALL') {
            vm.tempScenario.aggregate.settings.disk_option = 'ALL';
          }
          if (vm.tempScenario.aggregate.settings.cache_option !== 'NVMe' || vm.tempScenario.aggregate.settings.cache_option !== 'ALL') {
            vm.tempScenario.aggregate.settings.cache_option = 'ALL';
          }
          vm.tempScenario.aggregate.settings.hx_boost_conf = 'disabled';
          vm.tempScenario.aggregate.settings.hercules_conf = 'disabled';
        }
      };

      function onHypervisorChangedInCustomize() {
        var filters = getFilterValuesFromUI();
        if (vm.tempScenario.aggregate.settings.hypervisor === 'hyperv') {
          // vm.tempScenario.aggregate.settings.heterogenous = false;
          vm.scenario.aggregate.settings.disk_option = vm.scenario.aggregate.settings.disk_option === "NVME" || vm.scenario.aggregate.settings.disk_option === "LFF" ? vm.scenario.aggregate.settings.disk_option : "ALL";
          // vm.tempScenario.aggregate.settings.disk_option = "ALL";
          vm.tempScenario.aggregate.settings.server_type = "M5";
        }
        $timeout(function () {
          // this function should be executed with delay as the changes above triggers disk option change event
          updateFilterOptions(filters, vm.tempScenario);
        });

      };

      vm.computeNodesUpdate = function () {
        var filters = getFilterValuesFromUI();
        if (!vm.tempScenario.aggregate.settings.heterogenous) {
          // vm.filterDetails.computeNodesData.model = vm.filterDetails.computeNodesData.model ? vm.filterDetails.computeNodesData.model : vm.filterDetails.computeNodesData.options
          filters.Compute_Type = vm.filterDetails.computeNodesData.model ? vm.filterDetails.computeNodesData.model : vm.filterDetails.computeNodesData.options;
          updateFilterOptions(filters, vm.tempScenario);
        }
      }

      vm.onHwAccelChangedInCustomize = function () {
        var filters = getFilterValuesFromUI();
        if (vm.tempScenario.aggregate.settings.hercules_conf === 'forced') {
          vm.tempScenario.aggregate.settings.disk_option = vm.tempScenario.aggregate.settings.disk_option === "SED" || vm.tempScenario.aggregate.settings.disk_option === "FIPS" ? "ALL" : vm.tempScenario.aggregate.settings.disk_option;
          vm.tempScenario.aggregate.settings.cache_option = vm.tempScenario.aggregate.settings.cache_option === "SED" ? "ALL" : vm.tempScenario.aggregate.settings.cache_option;
        }
        $timeout(function () {
          // this function should be executed with delay as the changes above triggers disk option change event
          updateFilterOptions(filters, vm.tempScenario);
        });
      }

      vm.onHyperflexBoostInCustomize = function () {
        var filters = getFilterValuesFromUI();
        if (vm.tempScenario.aggregate.settings.hx_boost_conf === 'forced') {
          // vm.tempScenario.aggregate.settings.disk_option = vm.tempScenario.aggregate.settings.disk_option === "SED" || vm.tempScenario.aggregate.settings.disk_option === "FIPS" ? "ALL" : vm.tempScenario.aggregate.settings.disk_option;
          // vm.tempScenario.aggregate.settings.cache_option = vm.tempScenario.aggregate.settings.cache_option === "SED" ? "ALL" : vm.tempScenario.aggregate.settings.cache_option;
        }
        $timeout(function () {
          // this function should be executed with delay as the changes above triggers disk option change event
          updateFilterOptions(filters, vm.tempScenario);
        });
      }

      vm.onNodeChoiceChangedInCustomize = function () {
        vm.computeNodesUpdate();
      }

      vm.onSizingOptionChangedInCustomize = function () {
        var filters = getFilterValuesFromUI();
        /*if sizing option is bundle only, then set the disk option to default, ie. 'ALL'*/
        if (vm.tempScenario.aggregate.settings.bundle_only==='bundle') {
          // vm.tempScenario.aggregate.settings.disk_option = "ALL";
          vm.tempScenario.aggregate.settings.disk_option = vm.tempScenario.aggregate.settings.disk_option === "FIPS" ? "ALL" : vm.tempScenario.aggregate.settings.disk_option;
          vm.tempScenario.aggregate.settings.modular_lan = "ALL";
          vm.tempScenario.aggregate.settings.cpu_generation = vm.tempScenario.aggregate.settings.cpu_generation === 'sky' ? 'sky' : 'ALL';
          vm.tempScenario.aggregate.settings.server_type = "M5";
          vm.tempScenario.aggregate.settings.cache_option = vm.tempScenario.aggregate.settings.cache_option !== "SED" ? 'ALL' : vm.tempScenario.aggregate.settings.cache_option;
        }

        $timeout(function () {
          // this function should be executed with delay as the changes above triggers disk option change event
          updateFilterOptions(filters, vm.tempScenario);
          vm.computeNodesUpdate();
        });
      };

      vm.onDiskOptionChangedInCustomize = function () {
        var filters = getFilterValuesFromUI();
        if (vm.tempScenario.aggregate.settings.disk_option === 'COLDSTREAM') {
          vm.tempScenario.aggregate.settings.server_type = 'M5';
        }
        if (vm.tempScenario.aggregate.settings.disk_option === 'LFF') {
          vm.tempScenario.aggregate.settings.server_type = 'M5';
          vm.tempScenario.aggregate.settings.cache_option = 'ALL';
        }
        if (vm.tempScenario.aggregate.settings.disk_option === 'NON-SED') {
          vm.tempScenario.aggregate.settings.cache_option = vm.tempScenario.aggregate.settings.cache_option !== 'Optane' || vm.tempScenario.aggregate.settings.cache_option !== 'NVMe' ? 'ALL' : vm.tempScenario.aggregate.settings.cache_option;
        }
        if (vm.tempScenario.aggregate.settings.disk_option === 'SED' || vm.tempScenario.aggregate.settings.disk_option === 'FIPS') {
          vm.tempScenario.aggregate.settings.cache_option = vm.tempScenario.aggregate.settings.cache_option !== 'SED' ? 'ALL' : vm.tempScenario.aggregate.settings.cache_option;
        }
        updateFilterOptions(filters, vm.tempScenario);
      };

      vm.onCPUGenerationChangedInCustomize = function () {
        var filters = getFilterValuesFromUI();
        updateFilterOptions(filters, vm.tempScenario);
      };

      vm.onModularOptionChangedInCustomize = function () {
        // No change in filter values, so nothing to handle here
        var filters = getFilterValuesFromUI();
        updateFilterOptions(filters, vm.tempScenario);
      };

      vm.onCacheOptionChangedInCustomize = function () {
        // No change in filter values, so nothing to handle here
        var filters = getFilterValuesFromUI();
        updateFilterOptions(filters, vm.tempScenario);
      };

      vm.onServerTypeChangedInCustomize = function () {
        var filters = getFilterValuesFromUI();

        if (vm.tempScenario.aggregate.settings.server_type === 'M4') {
          if (vm.tempScenario.aggregate.settings.disk_option === 'COLDSTREAM') {
            vm.tempScenario.aggregate.settings.disk_option = 'ALL';
          }
        }
        if (vm.tempScenario.aggregate.settings.server_type === 'M4') {
          if (vm.tempScenario.aggregate.settings.disk_option === 'LFF') {
            vm.tempScenario.aggregate.settings.disk_option = 'ALL';
          }
        }
        $timeout(function () {
          updateFilterOptions(filters, vm.tempScenario);
        });
      };


      vm.toggleView = function (event) {
        vm.totalWorkloads = vm.scenario.aggregate.workloads;

        if ($rootScope.root.currentView == 'CLUSTER_VIEW') {
          vm.clusterIndex = (vm.clusterIndex < vm.scenario.totalClusters.length ? vm.clusterIndex : 0);
          vm.cluster = vm.scenario.totalClusters[vm.clusterIndex] || {};
          vm.viewObject = vm.cluster;
          vm.clusterDisplayName = vm.cluster._uiDisplayName;
          sortWorkloadsBySelectedCluster(vm.cluster._uiDisplayName);
        } else if ($rootScope.root.currentView == 'AGGREGATE_VIEW') {
          vm.viewObject = vm.scenario.aggregate;
        }
        updateQuickEditData();
      };

      function sortWorkloadsBySelectedCluster(clusterDisplayName) {

        var worklaodsOfSelectedCluster = utilService.filteredList(vm.totalWorkloads, function (wl) {
          return (wl._uiPrimaryCluster && wl._uiPrimaryCluster._uiDisplayName === vm.clusterDisplayName) || (wl.wl_type === "EPIC" && wl.wl_name === vm.viewObject._wlName);
        });
        if (vm.selectedWorkload) {
          for (var i = 0; i < worklaodsOfSelectedCluster.length; i++) {
            if (worklaodsOfSelectedCluster[i].wl_name === vm.selectedWorkload.wl_name) {
              var wl = worklaodsOfSelectedCluster.splice(i, 1)[0];
              if (wl.wl_type === 'VDI' || wl.wl_type === 'RDSH') {
                var wl2;
                for (var j = 0; j < worklaodsOfSelectedCluster.length; j++) {
                  if (worklaodsOfSelectedCluster[j].primary_wl_name === vm.selectedWorkload.wl_name) {
                    wl2 = worklaodsOfSelectedCluster.splice(j, 1)[0];
                  }
                }
                if (wl2) {
                  worklaodsOfSelectedCluster.unshift(wl, wl2);
                } else {
                  worklaodsOfSelectedCluster.unshift(wl);
                }
              } else {
                worklaodsOfSelectedCluster.unshift(wl);
              }
            }
          }
        }

        var worklaodsOfOtherCluster = utilService.filteredList(vm.totalWorkloads, function (wl) {
          return !((wl._uiPrimaryCluster && wl._uiPrimaryCluster._uiDisplayName === vm.clusterDisplayName) || (wl.wl_type === "EPIC" && wl.wl_name === vm.viewObject._wlName));
        });

        vm.totalWorkloads = worklaodsOfSelectedCluster.concat(worklaodsOfOtherCluster);
      }

      vm.selectWorkload = function (workload) {
        if (vm.quickEditData[workload.wl_name].showQuickEdit || vm.scenario.totalClusters.length === 0) {
          return;
        }
        vm.selectedWorkload = workload;

        // keep the workload's cluster at the top of the list
        var clusterIndex = getClusterIndexByWorklaodName(workload);
        var primaryCluster = vm.scenario.totalClusters[clusterIndex];
        var clustersToAdd = [primaryCluster];
        var clusteData;
        if (primaryCluster.isPartOfReplicationPair && !primaryCluster.isEpicCluster) {
          var replicationIndex = clusterIndex + (primaryCluster.isFirtsClusterInGroup ? +1 : -1);
          var replicatedCluster = vm.scenario.totalClusters[replicationIndex];
          primaryCluster.isFirtsClusterInGroup = true;
          replicatedCluster.isFirtsClusterInGroup = false;
          clustersToAdd.push(replicatedCluster);
          utilService.deleteItemByPropVal(vm.scenario.totalClusters, '_uiDisplayName', replicatedCluster._uiDisplayName);
        }
        vm.totalWorkloads.map(function (wlData) {
          var totalClusters = utilService.filteredList(vm.scenario.totalClusters, function (cluster) {
            return cluster.isEpicCluster && cluster.workloads[0].wl_name === wlData.wl_name;
          });
          var dc1 = utilService.filteredList(totalClusters, function (clustDc1) {
            return totalClusters[0]._clusterGroup === clustDc1._clusterGroup && 'DC1' === clustDc1.workloads[0].dc_name;
          });
          var dc2 = utilService.filteredList(totalClusters, function (clustDc2) {
            return totalClusters[0]._clusterGroup === clustDc2._clusterGroup && 'DC2' === clustDc2.workloads[0].dc_name;
          });
          var groupLength1 = 0, groupLength2 = 0;
          var clust1 = [], clust2 = [];
          dc1.map(function (dcClust, index) {
            if (primaryCluster._clusterGroup === dcClust._clusterGroup) {
              dcClust.isFirtsClusterInGroup = false;
            }
            var clustIndx = dcClust._uiDisplayName.split(' ')[1];
            clust1.push(clustIndx);
            dcClust._wlName = dcClust.workloads[0].wl_name;
            groupLength1 += dcClust.nodesList.length;
            dcClust.isFirtsClusterInGroup = (index === 0);
            utilService.deleteItemByPropVal(vm.scenario.totalClusters, '_uiDisplayName', dcClust._uiDisplayName);
          });
          dc2.map(function (dcClust, index) {
            if (primaryCluster._clusterGroup === dcClust._clusterGroup) {
              dcClust.isFirtsClusterInGroup = false;
            }
            var clustIndx = dcClust._uiDisplayName.split(' ')[1];
            clust2.push(clustIndx);
            dcClust._wlName = dcClust.workloads[0].wl_name;
            groupLength2 += dcClust.nodesList.length;
            utilService.deleteItemByPropVal(vm.scenario.totalClusters, '_uiDisplayName', dcClust._uiDisplayName);
          });
          if (dc1.length > 0) {
            dc1[0]['_groupLength'] = groupLength1 + groupLength2;
            dc1.map(function (dc) { dc['dc_name'] = 'DC1'; });
          }
          if (dc2.length > 0) {
            dc2.map(function (dc) { dc['dc_name'] = 'DC2'; });
          }
          clusteData = [].concat(dc1);
          clusteData = clusteData.concat(dc2);
          vm.scenario.totalClusters = clusteData.concat(vm.scenario.totalClusters);
          if (clusteData.length > 0 && workload.wl_name === clusteData[0]._wlName) {
            clustersToAdd = clusteData;
          }

          wlData['clusterList'] = [clust1];
          if (clust2.length > 0) {
            wlData['clusterList'].push(clust2);
          }


        })

        clustersToAdd.map(function (cluster) {
          utilService.deleteItemByPropVal(vm.scenario.totalClusters, '_uiDisplayName', cluster._uiDisplayName);
        });
        vm.scenario.totalClusters = clustersToAdd.concat(vm.scenario.totalClusters);
        // var cluster = vm.scenario.totalClusters.splice(clusterIndex, 1)[0];
        // var clustersToAdd = [cluster];
        // if(cluster.isPartOfReplicationPair) {
        //   var replicationIndex = clusterIndex + (cluster.isFirtsClusterInGroup ? +1 : -1);
        //   replicationIndex = replicationIndex - 1;  
        //   var replicationCluster = vm.scenario.totalClusters.splice(replicationIndex, 1)[0];

        //   if(cluster.isFirtsClusterInGroup) {
        //     clustersToAdd.push(replicationCluster);  
        //   } else {
        //     clustersToAdd.unshift(replicationCluster);
        //   }

        // }


        // updatine cluster index to the workload as the order changed
        vm.scenario.totalClusters.forEach(function (cluster, newIndex) {
          cluster.workloads.forEach(function (workload) {
            workload._uiClusterIndex = newIndex;
          });
        })

        vm.selectCluster(primaryCluster, 0, true, vm.selectedWorkload);

      };

      function resetScroll(elem) {
        var $elem = $(elem);
        $elem.find('.mCSB_container').animate({ 'top': '0px' }, 300);
        $elem.find('.mCSB_dragger').animate({ 'top': '0px' }, 300);
      }

      vm.selectCluster = function (cluster, clusterIndex, sortWorkloads, workloadToSelect) {
        vm.cluster = cluster;
        vm.clusterIndex = clusterIndex;
        vm.clusterDisplayName = (cluster.isStretchCluster && !cluster.isFirtsClusterInGroup) ? cluster._uiPairDisplayName : cluster._uiDisplayName;
        vm.viewObject = vm.cluster;
        vm.viewObject.utilization.map(function (util) {
          util.chartData = util.chartData.map(function (chart) {
            if (isNaN(chart)) {
              chart = 0;
            }
            return chart;
          });
          if (util.status === false) {
            util.wl_util = 0;
            util.site_ft_util = 0;
            util.ft_util = 0;
          }
        })
        var worklaodsOfSelectedCluster;
        if (!vm.cluster.isEpicCluster) {
          worklaodsOfSelectedCluster = utilService.filteredList(vm.totalWorkloads, function (wl) {
            return wl._uiPrimaryCluster && wl._uiPrimaryCluster._uiDisplayName === vm.clusterDisplayName;
          });
        } else {
          worklaodsOfSelectedCluster = utilService.filteredList(vm.totalWorkloads, function (wl) {
            return wl.wl_name === vm.cluster._wlName;
          });
        }
        vm.selectedWorkload = workloadToSelect || worklaodsOfSelectedCluster[0];

        if (sortWorkloads) {
          sortWorkloadsBySelectedCluster(vm.clusterDisplayName);
        }
        updateQuickEditData();

        // this is to move the clusters container to top only if user selects cluster by click
        if (workloadToSelect) {
          resetScroll('.scroll_container');
        }
        resetScroll('.workloadOuter_Container');


      };

      vm.selectResult = function (resultName) {
        vm.testData.hasSizingErrorClosed = false;
        $timeout(function () {
          vm.closeMask();
        }, 100)
        if (resultName !== 'Results') {
          updateScenarioToUI(null, resultName);
          toggleNonFlashNodesForResult();
        } else {
          vm.scenario.currentResult = 'Results';
          var compCalc = ((100 - vm.scenario.aggregate.settings.cluster_properties.compression_factor) / 100);
          var dedupeCalc = ((100 - vm.scenario.aggregate.settings.cluster_properties.dedupe_factor) / 100);
          var compData = vm.scenario.sizing_calculator.disk_capacity.usable / compCalc;
          vm.tooltipDataComp = vm.scenario.sizing_calculator.disk_capacity.usable + "" + vm.scenario.sizing_calculator.disk_capacity.usable_unit + " after " + vm.scenario.aggregate.settings.cluster_properties.compression_factor + "% compression becomes " + vm.scenario.sizing_calculator.disk_capacity.usable + " / " + compCalc.toFixed(1) + " = " + compData.toFixed(1) + vm.scenario.sizing_calculator.disk_capacity.usable_unit;
          vm.tooltipDataDedup = compData.toFixed(1) + "" + vm.scenario.sizing_calculator.disk_capacity.usable_unit + " after " + vm.scenario.aggregate.settings.cluster_properties.dedupe_factor + "% dedupe becomes " + compData.toFixed(1) + " / " + dedupeCalc.toFixed(1) + " = " + vm.scenario.sizing_calculator.disk_capacity.effective + vm.scenario.sizing_calculator.disk_capacity.usable_unit;

          // show cpu in results page
          var dupCpu = angular.copy(vm.scenario.aggregate.settings.node_properties.cpu);
          if (dupCpu instanceof Array) {
            var val = dupCpu.shift();
            val = val.split(' ')[0] + ' (';
            dupCpu.pop();
            dupCpu.pop();
            vm.scenario.aggregate.settings.node_properties.cpu_label = val + dupCpu.join(', ') + ')';
          }

          // show ram in results page
          var dupRam = angular.copy(vm.scenario.aggregate.settings.node_properties.ram)
          if (dupRam instanceof Array) {
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
            vm.scenario.aggregate.settings.node_properties.ram_label = val + label;
          }


        }
      };

      function toggleNonFlashNodesForResult() {
        if (vm.scenario.currentResult === 'All-Flash') {
          var nonFlashNodes = utilService.getItemsNotContainsText(vm.filterDetails.nodeTypeData.options, 'HXAF');
          vm.filterDetails.nodeTypeData.hiddenOptions = nonFlashNodes;

          // removing the 1.2TB disk capacity option for All Flash Nodes Results Tab
          vm.filterDetails.diskCapacity.model = utilService.deleteItemByVal(vm.filterDetails.diskCapacity.model, "1.2TB");
          vm.filterDetails.diskCapacity.options = utilService.deleteItemByVal(vm.filterDetails.diskCapacity.options, "1.2TB");
        } else {
          vm.filterDetails.nodeTypeData.hiddenOptions = [];
        }
      }

      /* FILTER NODES RELATED CODE */
      vm.showFilterNodesPopup = function (hypervisorSelected) {
        vm.tempScenario = JSON.parse(JSON.stringify(vm.scenario));
        vm.tempScenario.errors = [];
        updateFilterOptions(vm.tempScenario.aggregate.settings.filters, vm.tempScenario);
        vm.filterDetails.showFilterNodes = true;
        vm.hybirdModel = true;
        vm.moreSelection = true;
        vm.selectionCancel = false;
        $('#lightBox').show();
      };

      vm.hideFilterNodesPopup = function () {
        vm.filterDetails.showFilterNodes = false;
        vm.isTempResultAvailable = false;
        vm.hybirdModel = false;
        vm.moreSelection = false;
        vm.selectionCancel = true;
        vm.isThereUnsavedResults = false;
        vm.tempScenario = {};
        $('#lightBox').hide();
      };
      vm.showFixedPopup = function (hypervisorSelected) {
        // vm.filterDetails.showFixedFilter = true;
        // $('#lightBox').show();

        var prevHypervisor = prevHypervisorOptionVal;

        $uibModal.open({
          templateUrl: 'views/scenario_details/modals/fixed_filter.html',
          backdrop: 'static',
          size: 'sm',
          controller: 'FixedSizingController',
          controllerAs: 'fixedCtrl',
          resolve: {
            scenarioObj: function () {
              var scenario = utilService.getClone(vm.scenario);
              if (hypervisorSelected) {
                scenario.aggregate.settings.hypervisor = hypervisorSelected;
              }
              return scenario;
            },
            fixedConfingFilterData: function () {
              return fixedConfingFilterData;
            }
          }
        }).result.then(function (result) {
          fixedConfingFilterData = result.fixedConfingFilterData;
          var currentResult = angular.copy(vm.scenario.currentResult);
          updateScenarioToUI(result.scenario, result.scenario.settings_json[0].result_name);
          vm.scenario.currentResult = currentResult === 'Results' ? currentResult : vm.scenario.currentResult
          console.log(vm.scenario);
          vm.infoPageFlag = vm.scenario.sizing_type === 'fixed' ? vm.userData.fixed_sizing_desc : vm.userData.optimal_sizing_desc;
          vm.scenario.excludeWls = fixedConfingFilterData.excluded_wls[vm.scenario.aggregate.settings.hypervisor];
          if (!vm.infoPageFlag) {
            $timeout(function () {
              vm.closeMask();
            }, 100);
          } else {
            $('.noResultIndex,.plusBtn').css('pointer-events', 'none');
          }
        }, function (data) {
          console.log("dismissed");
          vm.scenario.aggregate.settings.hypervisor = prevHypervisor;
          if ('escape key press' !== data) {
            fixedConfingFilterData = data;
            vm.scenario.excludeWls = fixedConfingFilterData.excluded_wls[vm.scenario.aggregate.settings.hypervisor];
          }
          vm.infoPageFlag = vm.scenario.sizing_type === 'fixed' ? vm.userData.fixed_sizing_desc : vm.userData.optimal_sizing_desc;
          if (!vm.infoPageFlag) {
            $timeout(function () {
              vm.closeMask();
            }, 100);
          } else {
            $('.noResultIndex,.plusBtn').css('pointer-events', 'none');
          }
        });

      }
      vm.hideFixedPopup = function () {
        vm.filterDetails.showFixedFilter = false;
        $('#lightBox').hide();
      }

      vm.applyFilterNodes = function () {
        var filters = getFilterValuesFromUI();
        updateScenario(filters, function () {
          vm.hideFilterNodesPopup();
        }, null, vm.tempScenario);
      };

      vm.onClosingCustomResultsPopup = function () {
        if (vm.tempScenario.aggregate.error) {
          return vm.hideFilterNodesPopup();
        }


        var versionUpdatePopup;
        if (vm.isThereUnsavedResults) {
          versionUpdatePopup = $uibModal.open({
            templateUrl: 'views/scenario_details/modals/temp_result_save.html',
            backdrop: 'static'
          });

          versionUpdatePopup.result.then(function () {
            //ignore the changes & close filters / custom results popup
            vm.hideFilterNodesPopup();
          }, function () {
            // console.log("Cancel")
            // vm.saveReuslts();
          });
        } else {
          vm.hideFilterNodesPopup();
        }
      };

      function getUnifiedSettings(settings) {
        var lowestCost_settings = utilService.getClone(settings);
        var allFlash_settings = utilService.getClone(settings);
        lowestCost_settings.result_name = 'Lowest_Cost';
        allFlash_settings.result_name = 'All-Flash';
        return [allFlash_settings, lowestCost_settings];
      }

      vm.saveReuslts = function () {
        var dataToSave = ScenarioDataProcessor.getTempScenarioResultToSave(vm.scenario.currentResult, vm.tempScenario.aggregate.settings);
        // dataToSave.settings_json = vm.tempScenario.aggregate.settings;
        // dataToSave.settings_json = getUnifiedSettings(vm.tempScenario.aggregate.settings);
        nodeService.saveResults(vm.scenario.id, dataToSave).then(function (data) {
          ScenarioDataProcessor.updateSettingsOfRawScenarioData(dataToSave.settings_json);
          ScenarioDataProcessor.updateTempDataAsScenarioData();
          updateScenarioToUI(data, vm.scenario.currentResult);
          vm.hideFilterNodesPopup();

          init(true, vm.scenario.currentResult);
        });
      };

      vm.applyTempFilterNodes = function () {


        vm.tempScenario.aggregate.settings.filters = getFilterValuesFromUI(vm.scenario.currentResult);
        // preparing the request object to update req format
        var reqObject = ScenarioDataProcessor.getScenarioInPutRequestFormat(vm.tempScenario);

        reqObject.settings_json = [vm.tempScenario.aggregate.settings];
        vm.isTempResultAvailable = true;

        // removing unwanted Fields
        reqObject.wl_list.map(function (wlData) {
          delete wlData['clusterList'];
          delete wlData['dc_name'];
          delete wlData['concurrent_user_pcnt'];
          delete wlData['num_clusters'];
        });

        /*if the workloads are empty then save the result directly & update the UI & close the filters*/
        if (reqObject.wl_list.length === 0) {
          var rawScenario = ScenarioDataProcessor.getRawScenario();
          utilService.updateItemByProp(rawScenario.settings_json, "result_name", vm.tempScenario.aggregate.settings);
          ScenarioDataProcessor.process(rawScenario, vm.scenario.currentResult, true);
          return vm.saveReuslts();
        }

        return vm.applyFilterNodes();
        reqObject.wl_list = utilService.filteredList(reqObject.wl_list, function (wl) {
          return !((wl.wl_type === 'VDI' || wl.wl_type === 'RDSH') && wl.hasOwnProperty('primary_wl_name'));
        })
        scenarioService.save({ id: vm.scenario.id }, reqObject).$promise.then(function (updatedScenario) {
          addDatacentresEpicWl(updatedScenario);
          vm.isThereUnsavedResults = true;
          /* to preserve the temporary data settings */
          for (var i = 0; i < updatedScenario.settings_json.length; i++) {
            if (updatedScenario.settings_json[i].result_name === vm.tempScenario.currentResult) {
              updatedScenario.settings_json[i] = updatedScenario.temp_settings_json;
            }
          }

          if (updatedScenario.temp_error && updatedScenario.temp_error.length) {
            updatedScenario.temp_error[0].result_name = updatedScenario.temp_error[0].result_name || vm.tempScenario.currentResult;
          }

          vm.testData.hasTempSizingErrorClosed = false;
          vm.tempScenario = ScenarioDataProcessor.process(updatedScenario, vm.tempScenario.currentResult, true);
        }, function () { });
      };

      function getFilterValuesFromUI() {
        var filters = {};
        filters.Node_Type = vm.filterDetails.nodeTypeData.model;
        filters.Compute_Type = vm.filterDetails.computeNodesData.model;
        filters.CPU_Type = vm.filterDetails.cpuTypeData.model;
        filters.Clock = vm.filterDetails.cpuClockData.model;
        filters.RAM_Slots = vm.filterDetails.ramSlotsData.model;
        filters.RAM_Options = vm.filterDetails.ramMemoryData.model;
        filters.Disk_Options = vm.filterDetails.diskCapacity.model;
        filters.GPU_Type = vm.filterDetails.gpuData.model;
        filters.Cache_Options = vm.filterDetails.capacityData.model;
        return filters;
      }

      vm.onClockSelectionChanged = function (event) {
        if (event.changeType === 'EXPLICIT') {
          var filters = getFilterValuesFromUI();
          updateFilterOptions(filters, vm.tempScenario);
        }
      }

      function updateFilterValuesToUI(srcFilters) {
        toggleNonFlashNodesForResult();
        var filters = angular.extend({}, srcFilters);
        vm.filterDetails.nodeTypeData.model = filters.Node_Type;
        vm.filterDetails.computeNodesData.model = filters.Compute_Type;
        vm.filterDetails.cpuClockData.model = filters.Clock;
        vm.filterDetails.cpuTypeData.model = filters.CPU_Type;
        vm.filterDetails.ramSlotsData.model = filters.RAM_Slots;
        vm.filterDetails.ramMemoryData.model = filters.RAM_Options;
        vm.filterDetails.diskCapacity.model = filters.Disk_Options;
        vm.filterDetails.capacityData.modal = filters.Cache_Options;
        vm.filterDetails.gpuData.model = filters.GPU_Type || [];
        $scope.$broadcast("SCENARIO_UPDATED");
      }

      function getFilterOptions() {
        return filtersService.getFilterOptions();
      }

      function updateFilterOptions(filters, scenarioObj) {
        var filtersData = filtersService.getFilters(scenarioObj.aggregate.settings, scenarioObj.currentResult, vm.filterDetails.cpuClockData.model);

        console.log(" filtersData ", filtersData)
        vm.filterDetails.nodeTypeData.options = filtersData.Node_Type;
        vm.filterDetails.computeNodesData.options = filtersData.Compute_Type;
        vm.filterDetails.cpuClockData.options = filtersData.Clock;
        vm.filterDetails.cpuTypeData.options = filtersData.CPU_Type;
        vm.filterDetails.ramSlotsData.options = filtersData.RAM_Slots;
        vm.filterDetails.ramMemoryData.options = filtersData.RAM_Options;
        vm.filterDetails.diskCapacity.options = filtersData.Disk_Options;
        vm.filterDetails.capacityData.options = filtersData.Cache_Options;
        vm.filterDetails.gpuData.options = filtersData.GPU_Type;
        updateFilterValuesToUI(filters);
        toggleNonFlashNodesForResult();
      }

      function getClusterIndexByWorklaodName(wrokloadToBeSelected) {

        var clusterName = wrokloadToBeSelected._uiPrimaryCluster._uiDisplayName;
        for (var i = 0; i < vm.scenario.totalClusters.length; i++) {
          if (vm.scenario.totalClusters[i]._uiDisplayName === clusterName) {
            return i;
          }
        }
        return 0;
      }

      /* SCENARIO RELATED CODE */
      function updateScenarioToUI(scenarioData, resultName) {

        vm.scenario = ScenarioDataProcessor.process(scenarioData, resultName);
        prevNodeChoiceVal = vm.scenario.aggregate.settings.heterogenous;
        prevThresholdVal = vm.scenario.aggregate.settings.threshold;
        prevSizingOptionVal = vm.scenario.aggregate.settings.bundle_only;
        prevDiskOptionVal = vm.scenario.aggregate.settings.disk_option;
        prevHypervisorOptionVal = vm.scenario.aggregate.settings.hypervisor;
        var wrokloadToBeSelected = vm.selectedWorkload || vm.scenario.aggregate.workloads[0];;

        if (wrokloadToBeSelected && vm.scenario.totalClusters.length) {
          wrokloadToBeSelected = utilService.getItemByPropVal(vm.scenario.aggregate.workloads, "wl_name", wrokloadToBeSelected.wl_name)
          vm.clusterIndex = getClusterIndexByWorklaodName(wrokloadToBeSelected);
        }


        vm.toggleView();
        if (wrokloadToBeSelected) {
          vm.selectWorkload(wrokloadToBeSelected);
          sortWorkloadsBySelectedCluster(vm.clusterDisplayName);
        }

        updateFilterOptions(vm.scenario.aggregate.settings.filters, vm.scenario);

        vm.isHyperVSelectionAllowed = !(vm.scenario.aggregate.workloads.some(function (workload) {
          return workload.cluster_type === "stretch" || workload.remote_replication_enabled || workload.gpu_users;
        }));
      }

      function getUserData() {
        nodeService.getUserData().then(function (response) {
          vm.userData = response;
          vm.infoPageFlag = vm.scenario.sizing_type === 'fixed' ? response.fixed_sizing_desc : response.optimal_sizing_desc;
          if (!vm.infoPageFlag) {
            vm.closeMask();
          }
        });
      }

      function getScenarioDetails(skipVersionCheck, currentResult) {
        scenarioService.get({ id: $stateParams.id }).$promise.then(function (response) {
          addDatacentresEpicWl(response);
          if (!skipVersionCheck) {
            checkHXVersion(response);
          }
          updateScenarioToUI(response, currentResult);
          vm.isViewLoaded = true;
          var pageData = appService.getPageData();
          if (pageData.newScen && response.sizing_type === 'fixed') {
            vm.globalSettingModal()
          }
          getUserData();
          if ($('.noResultBoxPopup').is(':visible') && vm.totalWorkloads.length === 0) {
            $('.plusBtn').addClass('maskIcon')
            console.log('inner')
          } else {
            $('.plusBtn').removeClass('maskIcon')
            console.log('outter')
          }
        });

      }

      function addDatacentresEpicWl(res) {
        var datacentres;
        var wlList = res.workload_json ? res.workload_json.wl_list : res.workload_list;
        wlList = wlList || [];
        wlList.map(function (wlData) {
          if (wlData.wl_type === 'EPIC') {
            datacentres = wlData.datacentres;
          }
          if (res.workload_result.length > 0 && res.workload_result[0].hasOwnProperty("clusters")) {
            res.workload_result.map(function (wlRes) {
              wlRes.clusters.map(function (clust) {
                clust.map(function (clustData) {
                  clustData.wl_list.map(function (wl) {
                    if (wl.wl_type === 'EPIC' && wl.wl_name === wlData.wl_name) {
                      wl['datacentres'] = datacentres;
                    }
                  })
                })
              })
            });
          }
        })
      }

      function emitEvent(status, data) {
        $scope.$emit("RESIZE_SCENARIO", { status: status, data: data });
      }

      function checkHXVersion(data) {
        var sizerVersion = 0;
        var serverSizerVersion = appService.getSizerVersion().sizer_version;
        if (data.settings_json) {
          sizerVersion = data.settings_json[0].sizer_version;
        }/*else if(data.workload_result.length){
          sizerVersion = data.workload_result[0].sizer_version;
        }*/

        sizerVersion = parseFloat(sizerVersion || 0);

        if (data.workload_result.length && sizerVersion < serverSizerVersion) {
          $rootScope.root.isCurrentScenarioUptodate = false;

          var versionUpdatePopup = $uibModal.open({
            templateUrl: 'views/scenario_details/modals/version-check.html',
            backdrop: 'static',
            keyboard: false
          });

          versionUpdatePopup.result.then(function () {
            emitEvent("PROGRESS");

            nodeService.resizeScenario(vm.scenario.id, 'scenario-request-resize').then(function (updatedScenario) {
              emitEvent("SUCCESS", updatedScenario);
            }, function (rejection) {
              var errorMsg = rejection.data ? rejection.data.errorMessage : '';
              emitEvent("ERROR");
            });
          }, function () {
            // console.log("Cancel")
          });

        } else {
          $rootScope.root.isCurrentScenarioUptodate = true;
        }

      }

      function updateScenario(filters, successCallback, errorCallback, scenarioObject, isQuickEditSave) {
        var scenarioToUpdate = scenarioObject || vm.scenario;
        scenarioToUpdate.aggregate.settings.filters = getFilterValuesFromUI();
        if (filters) {
          scenarioToUpdate.aggregate.settings.filters = filters;
        }

        // preparing the request object to update req format
        var srcReqObject = ScenarioDataProcessor.getScenarioInPutRequestFormat(scenarioToUpdate);

        /*Following code is for backward compatibility : START*/
        $.each(srcReqObject.wl_list, function (index, workload) {
          if (workload.wl_type === "VDI") {
            workload.clock_per_desktop = workload.clock_per_desktop || workload.clock_per_vcpu;
          }
        })
        /*this is for backward compatibility : END*/

        srcReqObject.overwrite = true;

        var reqObject = JSON.parse(JSON.stringify(srcReqObject));
        reqObject.wl_list.map(function (wlData) {
          delete wlData['clusterList'];
          delete wlData['dc_name'];
          delete wlData['concurrent_user_pcnt'];
          delete wlData['num_clusters'];
        })
        reqObject.wl_list.forEach(function (workload) {
          for (var prop in workload) {
            if (prop.indexOf("_ui") === 0) {
              delete workload[prop];
            }
          }
        });

        if (reqObject.sizing_type === "fixed") {
          delete reqObject.settings_json[0].filters;
        }
        reqObject.wl_list = utilService.filteredList(reqObject.wl_list, function (wl) {
          return !((wl.wl_type === 'VDI' || wl.wl_type === 'RDSH') && wl.hasOwnProperty('primary_wl_name'));
        })
        scenarioService.save({ id: scenarioToUpdate.id }, reqObject).$promise.then(function (updatedScenario) {
          addDatacentresEpicWl(updatedScenario);
          if (successCallback && typeof successCallback === "function") {
            successCallback();
          }
          checkHXVersion(updatedScenario);

          // if it is the cusotmization result
          if (isQuickEditSave) {
            // get the result name that doesn't has the error
            vm.selectedWorkload = null;
            var nonErrorResultName = getNonErrorResult(updatedScenario, scenarioToUpdate.currentResult);
            updateScenarioToUI(updatedScenario, nonErrorResultName);
          } else {
            updateScenarioToUI(updatedScenario, scenarioToUpdate.currentResult);
          }


        }, function () {
          if (errorCallback && typeof errorCallback === "function") {
            errorCallback();
          }
        });
      }


      // 
      nodeService.getCPUModels().then(function (models) {
        appService.setCPUModels(models);
        console.log(models);
      })
      // 

      function init(skipVersionCheck, currentResult) {
        getFilterOptions().then(function () {
          nodeService.getFI_Options().then(function (response) {
            vm.fiPackageOptions = response.map(function (item) {
              return {
                label: item,
                value: item
              }
            });
            getScenarioDetails(skipVersionCheck, currentResult);
          });
        })
      }

      $scope.$on('$viewContentLoaded', function (event, viewConfig) {
        //If timeout is not used, loader message for initial reuqest(scenaio details) will not be visible as the mpl-progressabar not initialized by the time
        $timeout(function () {
          init();
        }, 10)
      });

    }]);

})();

