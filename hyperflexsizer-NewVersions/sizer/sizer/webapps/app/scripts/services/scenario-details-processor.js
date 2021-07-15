(function () {
  "use strict";

  angular
    .module('hyperflex')
    .service("ScenarioDataProcessor", ["appService", "workloadService", "utilService", "FEATURES", function (appService, workloadService, utilService, FEATURES) {
      // internal/private variables
      var fn = this;
      var defaultThrshold = 1;
      var defaultHeterogenous = false;
      var defaultDiscountBundle = 0;
      var defaultDiscountCto = 0;
      var defaultWrokloadType = "VDI";
      var defaultProfileType = "Task Worker";
      var defaultProvisioningType = "Pooled Desktops";
      // var defaultResultName = "Lowest_Cost";//"All-Flash";
      var defaultOSType = "win_7";
      var rawScenarioData = {};
      var rawTempScenarioData = {};
      var chartColorsMapping = {
        wl_util: "#6cc04a",
        ft_util: "#EB6D00",
        site_ft_util: "#0778f9",
        free_util: "#c4c4c4"
      };



      function getDefaultScenario() {
        return {
          id: '',
          name: '',
          currentResult: '',
          totalResults: [],
          aggregate: {
            settings: {},
            workloads: [],
            utilization: [],
            nodesList: [],
            capex: '',
            totalNodesCount: 0,
            error: {}
          },
          clusters: [],
          isHavingStretchCluster: false,
          totalClusters: [],
          excludeWls: [],
          sizing_type: 'optimal'
        };
      }

      function getDuplicate(data) {
        return JSON.parse(JSON.stringify(data));
      }

      fn.getRawScenario = function () {
        return rawScenarioData;
      };

      fn.updateSettingsOfRawScenarioData = function (settingsJSON) {
        rawScenarioData.settings_json = settingsJSON;
      }

      fn.updateTempDataAsScenarioData = function () {
        rawScenarioData = rawTempScenarioData;
        rawScenarioData.temp_result = rawScenarioData.temp_result || [];
        // updating workload results with temp results
        for (var i = 0; i < rawScenarioData.temp_result.length; i++) {
          utilService.updateItemByProp(rawScenarioData.workload_result, "result_name", rawScenarioData.temp_result[i]);
        }
      }

      function getDefaultResult(data) {
        var settings = data.settings_json || [];
        var errors = data.errors || [];
        // if data has errors & not all the results has error, then result that does not have the error is the default one
        if ((data.errors && data.errors.length) && settings.length !== errors.length) {
          for (var i = 0; i < settings.length; i++) {
            // if current result is not in errors then return that result name as the default one
            if (!utilService.getItemByPropVal(errors, "result_name", settings[i].result_name)) {
              return settings[i].result_name;
            }
          }
        }

        return data.settings_json[0].result_name;
      }

      fn.process = function (data, result_name, isTempararyData) {
        var workloadResultsList, workloadResult, settingsJson, defaultScenario, scenario, errorJson;
        result_name = result_name || getDefaultResult(data);//defaultResultName

        if (isTempararyData) {
          workloadResultsList = [];
          data.temp_result = data.temp_result || [];
          data.temp_result.forEach(function (result) {
            workloadResultsList.push(result instanceof Array ? result[0] : result);
          });
          data.temp_result = workloadResultsList;
          data.temp_error = data.temp_error || [];

          var actualErrorJson = null;
          if (result_name === "All-Flash") {
            actualErrorJson = utilService.getItemByPropVal(data.errors, "result_name", "Lowest_Cost");
            if (actualErrorJson) {
              data.temp_error.push(actualErrorJson)
            }
          } else if (result_name === "Lowest_Cost") {
            actualErrorJson = utilService.getItemByPropVal(data.errors, "result_name", "All-Flash");
            if (actualErrorJson) {
              data.temp_error.push(actualErrorJson)
            }
          }

          data.errors = data.temp_error;
          rawTempScenarioData = getDuplicate(data);
        } else {
          if (data) {
            rawScenarioData = getDuplicate(data);
          } else {
            data = rawScenarioData;
          }
          workloadResultsList = data.workload_result;
        }


        workloadResult = utilService.getItemByPropVal(workloadResultsList, "result_name", result_name);
        errorJson = utilService.getItemByPropVal(data.errors, "result_name", result_name);
        settingsJson = utilService.getItemByPropVal(data.settings_json, "result_name", result_name);
        settingsJson.bundle_only = (settingsJson.bundle_only == undefined) ? 'ALL' : settingsJson.bundle_only;
        settingsJson.cpu_generation = (settingsJson.cpu_generation == undefined) ? 'recommended' : settingsJson.cpu_generation;
        settingsJson.sed_only = (settingsJson.sed_only == undefined) ? false : settingsJson.sed_only;
        settingsJson.disk_option = settingsJson.disk_option || (settingsJson.sed_only ? "SED" : "ALL");
        settingsJson.cache_option = settingsJson.cache_option || (settingsJson.sed_only ? "SED" : "ALL");
        settingsJson.modular_lan = settingsJson.modular_lan ? settingsJson.modular_lan : "ALL";
        settingsJson.hypervisor = FEATURES.isHypervisorEnabled ? (settingsJson.hypervisor ? settingsJson.hypervisor : "esxi") : "esxi";
        // setting software license to 1 year by default
        settingsJson.license_yrs = (settingsJson.license_yrs == undefined) ? 1 : settingsJson.license_yrs;
        settingsJson.hercules_conf = (settingsJson.hercules_conf == undefined) ? 'enabled' : settingsJson.hercules_conf;
        settingsJson.hx_boost_conf = (settingsJson.hx_boost_conf == undefined) ? 'enabled' : settingsJson.hx_boost_conf;
        settingsJson.server_type = settingsJson.server_type ? settingsJson.server_type : "M5";
        settingsJson.single_cluster = (settingsJson.single_cluster == undefined) ? false : settingsJson.single_cluster;

        defaultScenario = getDefaultScenario();
        scenario = angular.extend({}, defaultScenario, { currentResult: result_name });

        if (data.settings_json) {
          data.settings_json.sort(function (set1, set2) {
            if (set2.result_name < set1.result_name)
              return -1
            if (set2.result_name > set1.result_name)
              return 1
            return 0
          });
          data.settings_json.forEach(function (setting) {
            scenario.totalResults.push(setting.result_name);
          });
        }
        if (workloadResult && workloadResult.result_name === "Fixed Config" && workloadResult.hasOwnProperty('sizing_calculator')) {
          scenario.totalResults.push('Results');
          scenario['sizing_calculator'] = workloadResult.sizing_calculator;
        } else if (data.sizing_type === 'fixed' && (workloadResultsList.length === 1 && workloadResultsList[0].hasOwnProperty('sizing_calculator'))) {
          scenario.totalResults.push('Results');
          scenario['sizing_calculator'] = workloadResultsList[0].sizing_calculator;
        }

        if (!data) {
          return scenario;
        }

        // basic scenario details
        scenario.id = data.id;
        scenario.name = data.name;
        scenario.sizing_type = data.sizing_type || defaultScenario.sizing_type;
        scenario.aggregate.error = errorJson;
        scenario.aggregate.settings = settingsJson || {};
        scenario.aggregate.settings.threshold = (scenario.aggregate.settings.threshold != undefined) ? scenario.aggregate.settings.threshold : defaultThrshold;
        scenario.aggregate.settings.heterogenous = (scenario.aggregate.settings.heterogenous != undefined) ? scenario.aggregate.settings.heterogenous : defaultHeterogenous;
        scenario.aggregate.settings.bundle_discount_percentage = (scenario.aggregate.settings.bundle_discount_percentage != undefined) ? scenario.aggregate.settings.bundle_discount_percentage : defaultDiscountBundle;
        scenario.aggregate.settings.cto_discount_percentage = (scenario.aggregate.settings.cto_discount_percentage != undefined) ? scenario.aggregate.settings.cto_discount_percentage : defaultDiscountCto;

        var workloadsListInOriginalOrder = (data.workload_json && data.workload_json.wl_list) ?
          data.workload_json.wl_list : data.workload_list || [];
        var workloadNamesInOriginalOrder = workloadsListInOriginalOrder.map(function (workload) {
          return workload.wl_name;
        });

        if (workloadResult) {

          scenario.clustersGroups = getClustersGroups(workloadResult, scenario.aggregate.settings.dr_enabled);
          scenario.totalClusters = getTotalClusters(scenario.clustersGroups);
          // scenario.aggregate.utilization = processUtilizations(workloadResult.summary_info.Utilization);
          // scenario.aggregate.capex = workloadResult.summary_info.capex;
          scenario.aggregate.rackUnits = workloadResult.summary_info.rack_units;
          scenario.aggregate.numOfFTNodes = workloadResult.summary_info.num_ft_nodes;
          //processing aggregate nodes
          for (var i = 0; i < scenario.clusters.length; i++) {
            scenario.aggregate.nodesList = scenario.aggregate.nodesList.concat(scenario.clusters[i].nodesList);
            scenario.aggregate.workloads = scenario.aggregate.workloads.concat(scenario.clusters[i].workloads);
            scenario.aggregate.totalNodesCount += scenario.clusters[i].totalNodesCount;
          }

          for (var i = 0; i < scenario.clustersGroups.length; i++) {
            for (var j = 0; j < scenario.clustersGroups[i].length; j++) {
              scenario.aggregate.nodesList = scenario.aggregate.nodesList.concat(scenario.clustersGroups[i][j].nodesList);
              scenario.aggregate.totalNodesCount += scenario.clustersGroups[i][j].totalNodesCount;
            }
          }
          scenario.aggregate.workloads = getTotalUniqueWorkloads(scenario.clustersGroups);
          scenario.aggregate.nodesList = processAggregateNodes(scenario.aggregate.nodesList);

          scenario.aggregate.workloads.map(function (wls) {
            if ((wls.wl_type === 'VDI' || wls.wl_type === 'RDSH') && wls.hasOwnProperty('primary_wl_name')) {
              var index = workloadNamesInOriginalOrder.indexOf(wls.primary_wl_name)
              if (workloadNamesInOriginalOrder.indexOf(wls.wl_name) === -1) {
                workloadNamesInOriginalOrder.splice(index + 1, 0, wls.wl_name);
              }
            }
          });
          setWorkloadsInOriginalOrder(scenario, workloadNamesInOriginalOrder);
        } else if (scenario.aggregate.error) {
          scenario.aggregate.workloads = workloadsListInOriginalOrder;
        }

        scenario.isHavingStretchCluster = scenario.aggregate.workloads.some(function (workload) {
          return workload.cluster_type === 'stretch';
        });

        scenario.isHavingEpicWorkload = scenario.aggregate.workloads.some(function (workload) {
          return workload.wl_type === 'EPIC';
        });

        var wlLength = utilService.filteredList(scenario.aggregate.workloads, function (wl) {
          return !((wl.wl_type === 'VDI' || wl.wl_type === 'RDSH') && wl.hasOwnProperty('primary_wl_name'));
        });
        scenario.aggregate.wlLength = wlLength.length
        return scenario;
      };

      function setWorkloadsInOriginalOrder(scenario, workloadNames) {
        var workloadsList = scenario.aggregate.workloads;
        var newList = [];
        var nameIndexDict = {};
        workloadsList.forEach(function (wl, wlIndex) {
          nameIndexDict[wl.wl_name] = wlIndex;
        });
        workloadNames.forEach(function (wlName, wlIndex) {
          newList[wlIndex] = workloadsList[nameIndexDict[wlName]];
        });
        scenario.aggregate.workloads = newList;
      }

      fn.getTempScenarioResultToSave = function (resultName, currentResultSettings) {
        var settings_json = utilService.getItemByPropVal(rawTempScenarioData.settings_json, "result_name", resultName);
        var result_json = utilService.getItemByPropVal(rawTempScenarioData.temp_result, "result_name", resultName);
        var temp_error = utilService.getItemByPropVal(rawTempScenarioData.temp_error, "result_name", temp_error);

        settings_json = rawScenarioData.settings_json.map(function (settings) {
          var newSettings = getDuplicate(currentResultSettings);
          newSettings.result_name = settings.result_name;
          return newSettings;
        });

        return {
          'settings_json': settings_json,
          'result_json': (result_json || {}),
          'error_json': (temp_error || {})
        }
      };

      fn.getScenarioInPutRequestFormat = function (scenarioDeatilsObj) {
        var reqObject = {
          username: appService.getUserInfo().name,
          model_list: [],
          model_choice: "None",
          name: scenarioDeatilsObj.name,
          settings_json: [],
          wl_list: [],
          sizing_type: scenarioDeatilsObj.sizing_type
        };

        var settingsList = getDuplicate(rawScenarioData.settings_json);
        var currentSetting = scenarioDeatilsObj.aggregate.settings;
        settingsList = utilService.updateItemByProp(settingsList, "result_name", currentSetting);
        reqObject.settings_json = settingsList;
        reqObject.wl_list = getDuplicate(scenarioDeatilsObj.aggregate.workloads);

        reqObject.settings_json = reqObject.settings_json.map(function (settings) {
          var newSettings = getDuplicate(currentSetting);
          newSettings.result_name = settings.result_name;
          return newSettings;
        });

        return reqObject;
      };

      fn.getDefaultWorkload = function (srcWorkload) {
        var wlType, totalSteps, stepIndex, fieldIndex, currentStep, currentField, workloadFields, workloadDefaults, workload = {};

        // getting defaults
        wlType = srcWorkload.wl_type || getDefaultWorkloadType();
        workloadDefaults = fn.getDefaultValues(srcWorkload);

        workloadFields = workloadService.fields[wlType];

        totalSteps = [].concat(workloadFields.steps);

        for (stepIndex = 1; stepIndex < totalSteps.length; stepIndex++) {
          currentStep = totalSteps[stepIndex];
          for (fieldIndex = 0; fieldIndex < currentStep.fields.length; fieldIndex++) {
            currentField = currentStep.fields[fieldIndex];
            if (currentField.modelName) {
              if (currentField.modelName === 'datacentres') {
                workload[currentField.modelName] = [];
                currentField.fields.map(function (field) {
                  var dcData = {};
                  dcData[field.modelName] = field.name;
                  field.column.map(function (col) {
                    if (col.modelName && workloadDefaults[currentField.modelName][field.name][col.modelName]) {
                      dcData[col.modelName] = workloadDefaults[currentField.modelName][field.name][col.modelName].value;
                    }
                  });
                  workload[currentField.modelName].push(dcData);
                });
              } else {
                workload[currentField.modelName] = workloadDefaults[currentField.modelName] ? workloadDefaults[currentField.modelName].value : currentField.value;
              }
            }
          }
          if (currentStep.dependentFields) {
            for (fieldIndex = 0; fieldIndex < currentStep.dependentFields.length; fieldIndex++) {
              currentField = currentStep.dependentFields[fieldIndex];
              if (currentField.modelName) {
                workload[currentField.modelName] = workloadDefaults[currentField.modelName] ? workloadDefaults[currentField.modelName].value : currentField.value;
              }
            }
          }
        }
        workload.wl_type = wlType;
        return workload;
      };

      fn.getDefaultValues = function (workload) {
        var workloadDefaults, wlType, profileType, provisioningType, osType, dbType, infraType, brokerType, containerType;
        var input_src, exp_util;
        wlType = workload.wl_type || getDefaultWorkloadType();
        profileType = workload.profile_type || getDefaultProfileType(wlType);
        profileType = profileType.replace(" ", "_").toUpperCase();

        if (wlType === "VDI") {
          provisioningType = workload.provisioning_type || getDefaultProvisioningType(wlType);
          provisioningType = provisioningType.replace(" ", "_").toUpperCase();
          osType = workload.os_type || getDefaultOSType(wlType);
          osType = osType.replace(" ", "_").toUpperCase();
        } else if (wlType === "VDI_INFRA") {
          infraType = workload.infra_type || "citrix";
          workload.infra_type = infraType;
        } else if (wlType === "DB" || wlType === "ORACLE" || wlType === "AWR_FILE") {
          dbType = workload.db_type || getDefaultDBType(wlType);
        } else if (wlType === "RDSH") {
          brokerType = workload.broker_type || "citrix";
        } else if (wlType === "CONTAINER") {
          containerType = workload.container_type || getDefaultProfileType(wlType);
          containerType = containerType.replace(" ", "_").toUpperCase();
        } else if (wlType === "AIML") {
          input_src = workload.input_type || "Text Input";
          exp_util = workload.expected_util || "PoC";
        }

        var workloadDefaults;

        switch (wlType) {
          case "VDI":
            workloadDefaults = workloadService.defaultValues[wlType][profileType][provisioningType][osType];
            break;
          case "VDI_INFRA":
            workloadDefaults = workloadService.defaultValues[wlType][infraType];
            break;
          case "VSI":
            workloadDefaults = workloadService.defaultValues[wlType][profileType];
            break;
          case "RAW_FILE":
          case "RAW":
            workloadDefaults = workloadService.defaultValues[wlType] || {};
            break;
          case "EXCHANGE":
            workloadDefaults = workloadService.defaultValues[wlType] || {};
            break;
          case "DB":
            workloadDefaults = workloadService.defaultValues[wlType][dbType][profileType];
            break;
          case "ORACLE":
            workloadDefaults = workloadService.defaultValues[wlType][dbType][profileType];
            break;
          case "ROBO":
            workloadDefaults = workloadService.defaultValues[wlType][profileType];
            break;
          case "EPIC":
            workloadDefaults = workloadService.defaultValues[wlType] || {};
            break;
          case "VEEAM":
            workloadDefaults = workloadService.defaultValues[wlType] || {};
            break;
          case "SPLUNK":
            workloadDefaults = workloadService.defaultValues[wlType] || {};
            break;
          case "BULK":
            workloadDefaults = workloadService.defaultValues[wlType] || {};
            break;
          case "RDSH":
            workloadDefaults = workloadService.defaultValues[wlType][profileType][brokerType] || {};
            break;
          case "CONTAINER":
            workloadDefaults = workloadService.defaultValues[wlType][containerType];
            break;
          case "AIML":
            workloadDefaults = workloadService.defaultValues[wlType][input_src][exp_util];
            break;
          case "AWR_FILE":
            workloadDefaults = workloadService.defaultValues[wlType][dbType];
            break;
        }
        return workloadDefaults;
      }

      function getDefaultWorkloadType() {
        return defaultWrokloadType;
      }

      function getDefaultProfileType(wlType) {
        var workloadFields = workloadService.fields[wlType];
        var stepIndex, fieldIndex, currentStep, currentField;
        for (stepIndex = 0; stepIndex < workloadFields.steps.length; stepIndex++) {
          currentStep = workloadFields.steps[stepIndex];
          for (fieldIndex = 0; fieldIndex < currentStep.fields.length; fieldIndex++) {
            currentField = currentStep.fields[fieldIndex];
            if (currentField.modelName == 'profile_type' || currentField.modelName == 'container_type') {
              return currentField.value;
            }
          }
        }
        return defaultProfileType;
      }

      function getDefaultDBType(wlType) {
        var workloadFields = workloadService.fields[wlType];
        var stepIndex, fieldIndex, currentStep, currentField;
        for (stepIndex = 0; stepIndex < workloadFields.steps.length; stepIndex++) {
          currentStep = workloadFields.steps[stepIndex];
          for (fieldIndex = 0; fieldIndex < currentStep.fields.length; fieldIndex++) {
            currentField = currentStep.fields[fieldIndex];
            if (currentField.modelName == 'db_type') {
              return currentField.value;
            }
          }
        }
        return defaultProfileType;
      }

      function getDefaultProvisioningType(wlType) {
        var workloadFields = workloadService.fields[wlType];
        var stepIndex, fieldIndex, currentStep, currentField;
        for (stepIndex = 0; stepIndex < workloadFields.steps.length; stepIndex++) {
          currentStep = workloadFields.steps[stepIndex];
          for (fieldIndex = 0; fieldIndex < currentStep.fields.length; fieldIndex++) {
            currentField = currentStep.fields[fieldIndex];
            if (currentField.modelName == 'provisioning_type') {
              return currentField.value;
            }
          }
        }
        return defaultProvisioningType;
      }

      function getDefaultOSType(wlType, profileType) {
        var workloadFields = workloadService.fields[wlType];
        var stepIndex, fieldIndex, currentStep, currentField;
        for (stepIndex = 0; stepIndex < workloadFields.steps.length; stepIndex++) {
          currentStep = workloadFields.steps[stepIndex];
          for (fieldIndex = 0; fieldIndex < currentStep.fields.length; fieldIndex++) {
            currentField = currentStep.fields[fieldIndex];
            if (currentField.modelName == 'os_type') {
              return currentField.value;
            }
          }
        }
        return defaultOSType;
      }

      function getTotalUniqueWorkloads(clustersGroups) {
        var uniqueWrokloads = [];
        var result;

        clustersGroups.forEach(function (group, gIndex) {
          group.forEach(function (cluster, cIndex) {
            cluster.workloads.forEach(function (workload, wIndex) {
              var currentWorkload = workload;

              result = utilService.getItemByPropVal(uniqueWrokloads, 'wl_name', workload.wl_name);

              currentWorkload = result || workload;
              if (workload.wl_type === 'EPIC') {
                currentWorkload = workload;
              }

              // Primary Cluster 
              if ((currentWorkload.cluster_type === 'stretch' && cIndex === 0) ||
                !currentWorkload.remote_replication_enabled || ((currentWorkload.remote && cIndex == 1) || (!currentWorkload.remote && cIndex == 0)) ||
                currentWorkload.wl_type === 'EPIC') {
                currentWorkload._uiPrimaryCluster = {
                  _uiDisplayName: cluster._uiDisplayName,
                  isPartOfReplicationPair: cluster.isPartOfReplicationPair
                };
              }
              // Secondary(DR) Cluster
              else {
                currentWorkload._uiSecondayCluster = {
                  _uiDisplayName: cluster._uiDisplayName,
                  isPartOfReplicationPair: cluster.isPartOfReplicationPair
                };
              }

              if (result === null) {
                uniqueWrokloads.push(currentWorkload);
              }

            })
          })
        });
        return uniqueWrokloads;
      }



      function getTotalClusters(clustersGroups) {
        var _totalClusters = [];

        clustersGroups.forEach(function (group, gIndex) {
          group.forEach(function (cluster, cIndex) {
            cluster.isFirtsClusterInGroup = (cIndex == 0);
            cluster.clustersLengthInGroup = group.length;
            cluster.isStretchCluster = isStretchCluster(cluster);
            cluster.isEpicCluster = isEpicCluster(cluster);
            if (cluster.isEpicCluster) {
              cluster._clusterGroup = gIndex;
            }
            _totalClusters.push(cluster);
          });
        });

        return _totalClusters;
      }

      function isEpicCluster(cluster) {
        return cluster.workloads.some(function (wlData) {
          return wlData.wl_type === 'EPIC';
        })
      }

      function isStretchCluster(cluster) {
        return cluster.workloads.some(function (workload) {
          return workload.cluster_type === 'stretch';
        });
      }

      var _gClusterIndex;
      function getClustersGroups(srcWorkloadResult, drEnabled) {
        var _clustersGroups = [];
        var workloads = [];
        _gClusterIndex = 0;
        for (var i = 0; i < srcWorkloadResult.clusters.length; i++) {
          _clustersGroups[i] = processGroupClusters(srcWorkloadResult.clusters[i], drEnabled);
        }
        return _clustersGroups;
      }

      function processGroupClusters(srcClusterGroup, drEnabled) {
        var _clusterGrp = [];
        for (var i = 0; i < srcClusterGroup.length; i++) {
          _clusterGrp[i] = processCluster(srcClusterGroup[i], drEnabled);
          _clusterGrp[i].isRemoteCluster = (i == 1);
          _clusterGrp[i].isPartOfReplicationPair = (srcClusterGroup.length > 1)
        }

        // This is to add the pair cluster name to each cluster of the pair
        if (srcClusterGroup.length > 1) {
          _clusterGrp[0]._uiPairDisplayName = _clusterGrp[1]._uiDisplayName;
          _clusterGrp[1]._uiPairDisplayName = _clusterGrp[0]._uiDisplayName
        }
        return _clusterGrp;
      }



      function processCluster(cluster, drEnabled) {
        var clusterObject = {}, currentCluster, nodeDetails, accessoryDetails;
        currentCluster = cluster;
        clusterObject._uiDisplayName = "Cluster " + (_gClusterIndex + 1);
        // clusterObject.capex = currentCluster.pricing[0].value[1].tag_val;
        clusterObject.settings = currentCluster.settings || {};
        clusterObject.settings = currentCluster.settings;
        clusterObject.settings.threshold = (clusterObject.settings.threshold != undefined) ? clusterObject.settings.threshold : defaultThrshold;
        clusterObject.settings.heterogenous = (clusterObject.settings.heterogenous != undefined) ? clusterObject.settings.heterogenous : defaultHeterogenous;
        // clusterObject.workloads = currentCluster.wl_list;
        clusterObject.workloads = addClusterIndextoWorkload(currentCluster, _gClusterIndex);
        clusterObject.utilization = processUtilizations(currentCluster.Utilization, drEnabled);
        clusterObject.herculesConf = false;
        clusterObject.hxBoostConf = false;
        currentCluster.node_info.map(function (node) {
          clusterObject.herculesConf = clusterObject.herculesConf || node.hercules_conf;
          clusterObject.hxBoostConf = clusterObject.hxBoostConf || node.hx_boost_conf;
        });
        nodeDetails = processNodes(currentCluster.node_info, clusterObject.herculesConf, clusterObject.hxBoostConf);
        clusterObject.nodesList = nodeDetails.nodesList;
        clusterObject.totalNodesCount = nodeDetails.totalNodesCount;
        clusterObject.numOfFTNodes = nodeDetails.totalFTNodes;
        clusterObject.required_hxdp = parseFloat(currentCluster.required_hxdp) || 0;

        if (currentCluster.accessories && currentCluster.accessories.length) {
          accessoryDetails = processAccessories(currentCluster.accessories);
          clusterObject.nodesList = clusterObject.nodesList.concat(accessoryDetails.nodesList);
          // clusterObject.totalNodesCount += accessoryDetails.totalNodesCount;
          // clusterObject.numOfFTNodes += accessoryDetails.totalFTNodes;  
        }


        clusterObject.rackUnits = currentCluster.rack_units;
        clusterObject.rfLabel = getRFLable(currentCluster);
        clusterObject.nplusLabel = getNplusLable(currentCluster);
        clusterObject.nodesList = processAggregateNodes(clusterObject.nodesList);


        _gClusterIndex++;
        return clusterObject;
      }

      function getRFLable(cluster) {
        var rf = '';
        switch (cluster.settings.replication_factor) {
          case 0:
            rf = "None"; break;
          case 2:
            rf = "RF 2"; break;
          case 3:
            rf = "RF 3"; break;
        }
        return rf;
      }

      function getNplusLable(cluster) {
        var nplus = '';
        switch (cluster.settings.fault_tolerance) {
          case 0:
            nplus = "None"; break;
          case 1:
            nplus = "N+1"; break;
          case 2:
            nplus = "N+2"; break;
        }
        return nplus;
      }

      function addClusterIndextoWorkload(cluster, clusterIndex) {
        var workloads = cluster.wl_list;
        for (var i = 0; i < workloads.length; i++) {
          workloads[i]._uiClusterIndex = clusterIndex;
        }
        return workloads;
      }

      function processNodes(nodesList, herculasData, hxBoostData) {
        var nodeObject, currentNode, totalNodesCount = 0, totalFTNodes = 0, nodes = [];
        for (var j = 0; j < nodesList.length; j++) {
          currentNode = nodesList[j];
          nodeObject = {};
          nodeObject.type = currentNode.model_details.type;
          nodeObject.name = currentNode.model_details.name;
          nodeObject.description = getDescription(currentNode, herculasData, hxBoostData);
          nodeObject.numOfNodes = currentNode.num_nodes;
          nodeObject.numOfFTNodes = currentNode.num_ft_nodes || 0;
          nodes.push(nodeObject);
          totalNodesCount += nodeObject.numOfNodes;
          totalFTNodes += nodeObject.numOfFTNodes;
        }

        return {
          nodesList: nodes,
          totalNodesCount: totalNodesCount,
          totalFTNodes: totalFTNodes
        };
      }

      function processAccessories(nodesList) {
        var nodeObject, currentNode, totalNodesCount = 0, totalFTNodes = 0, nodes = [];
        for (var j = 0; j < nodesList.length; j++) {
          currentNode = nodesList[j];
          nodeObject = {};
          nodeObject.type = currentNode.type || "Accessories";
          nodeObject.name = currentNode.part_name;
          nodeObject.description = currentNode.part_description;
          nodeObject.numOfNodes = currentNode.count;
          nodeObject.numOfFTNodes = currentNode.num_ft_nodes || 0;
          nodes.push(nodeObject);
          totalNodesCount += nodeObject.numOfNodes;
          totalFTNodes += nodeObject.numOfFTNodes;
        }

        return {
          nodesList: nodes,
          totalNodesCount: totalNodesCount,
          totalFTNodes: totalFTNodes
        };
      }

      function filterArray(arr, callback) {
        var list = [];
        for (var i = 0; i < arr.length; i++) {
          if (callback(arr[i])) {
            list.push(arr[i]);
          }
        }
        return list;
      }

      function getDescription(node, herculasData, hxBoostData) {
        var desc = "", descList = node.model_details.node_description;
        var seperator = ' &nbsp; | &nbsp; ';
        var descKeys = ["CPU", "RAM", "HDD", "SSD", "GPU_USERS"];
        if (descList instanceof Array) {
          desc = filterArray(descList, function (descItem) {
            return descItem;
          }).join(seperator);
        } else {
          desc = filterArray(descKeys.map(function (key) {
            var str = descList[key];
            if (str && !node.model_details[key + '_AVAILABILITY']) {
              str += '<sup> *</sup>';
            }
            if(str && key === "SSD" && hxBoostData) {
              str += ' | HyperFlex Boost'
            }
            if (str && key === "SSD" && herculasData) {
              str += ' | HyperFlex Acceleration Engine';
            }
            return str;
          }), function (item) {
            return item != undefined;
          }).join(seperator);
        }


        desc += (seperator) + node.model_details.rack_space + " RU";
        desc += node.mod_lan ? (seperator) + node.mod_lan : "";
        return desc;
      }

      function processAggregateNodes(aggNodes) {
        var nodesList = [], propsToMatch = ["name", "description"];
        var currentNode, nodeIdex;
        for (var i = 0; i < aggNodes.length; i++) {
          currentNode = angular.extend({}, aggNodes[i]);
          nodeIdex = indexOf(nodesList, currentNode, propsToMatch);
          if (nodeIdex === -1) {
            nodesList.push(currentNode);
          } else {
            nodesList[nodeIdex].numOfNodes += currentNode.numOfNodes
          }
        }

        //Display the GPU nodes at last
        nodesList.sort(function (nodeA, nodeB) {
          var isNodeA_has_GPU = nodeA.name.indexOf("GPU") !== -1 ? 1 : 0;
          var isNodeB_has_GPU = nodeB.name.indexOf("GPU") !== -1 ? 1 : 0;
          return isNodeA_has_GPU - isNodeB_has_GPU;
        });
        return nodesList;
      }

      function indexOf(list, item, props) {
        for (var i = 0; i < list.length; i++) {
          if (areAllPropsSame(item, list[i], props)) {
            return i;
          }
        }
        return -1;
      }

      function areAllPropsSame(itemA, itemB, props) {
        for (var j = 0; j < props.length; j++) {
          if (itemA[props[j]] != itemB[props[j]]) {
            return false;
          }
        }
        return true;
      }

      function processUtilizations(utlizationArray, drEnabled) {
        var chartDetails;
        for (var i = 0; i < utlizationArray.length; i++) {
          chartDetails = getChartData(utlizationArray[i], drEnabled);
          utlizationArray[i].chartData = chartDetails.chartData;
          utlizationArray[i].chartColors = chartDetails.chartColors;
          utlizationArray[i].utilization = utlizationArray[i].chartData[0];
        }
        return utlizationArray;
      }


      function getChartData(srcUtilization, drEnabled) {
        var total = 100;
        var utilVal;
        var utilDetails = [
          {
            "prop": "wl_util",
            "value": srcUtilization.wl_util
          },
          {
            "prop": "ft_util",
            "value": srcUtilization.ft_util
          },
          {
            "prop": "site_ft_util",
            "value": srcUtilization.site_ft_util
          }
        ];

        // if dr is not enabled removing 'site_ft_util' from utilization chart
        if (!drEnabled) {
          utilDetails.length = utilDetails.length - 1;
        }

        for (var i = 0; i < utilDetails.length; i++) {
          utilVal = utilDetails[i].value;
          utilDetails[i].value = Math.round(utilVal < 0 ? 0 : utilVal > 100 ? 100 : utilVal);
        }

        utilDetails.sort(function (utilA, utilB) {
          return utilA.value - utilB.value
        });

        /* [::START] composing final chart data & colors to required in UI */
        var chartData = [utilDetails[0].value];
        var chartColors = [chartColorsMapping[utilDetails[0].prop]];
        for (var i = 1; i < utilDetails.length; i++) {
          chartData.push(utilDetails[i].value - utilDetails[i - 1].value);
          chartColors.push(chartColorsMapping[utilDetails[i].prop]);
        }
        // adding remaining/empty/unused percentage value
        chartData.push(100 - utilDetails[utilDetails.length - 1].value);
        chartColors.push(chartColorsMapping.free_util);
        /* [::END] composing final chart data & colors to required in UI */

        return {
          chartData: chartData,
          chartColors: chartColors
        };
      }

    }]);

})();
