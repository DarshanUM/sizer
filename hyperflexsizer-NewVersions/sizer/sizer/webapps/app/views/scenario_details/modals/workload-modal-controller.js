(function () {
  "use strict";

  angular
    .module('hyperflex')
    .controller("WorkloadModalController", ["$scope", "$filter", "$uibModal", "$uibModalInstance", "appService", "utilService", "scenarioService", "mplprogService", "ScenarioDataProcessor", "workloadData", "srcWorkload", "scenario", "modalTitle", function ($scope, $filter, $uibModal, $uibModalInstance, appService, utilService, scenarioService, mplprogService, ScenarioDataProcessor, workloadData, srcWorkload, scenario, modalTitle) {
      var vm = this;
      var isEditRequest = srcWorkload ? true : false;
      var isAddRequest = srcWorkload ? false : true;
      var workloadIndex = getWorkloadIndex(scenario.aggregate.workloads, srcWorkload, 'wl_name');
      var defaultWorkloadType = "VDI";
      if (scenario.aggregate.settings.node_properties && scenario.aggregate.settings.node_properties.workload_options) {
        if (scenario.aggregate.settings.node_properties.workload_options.indexOf(defaultWorkloadType) === -1) {
          defaultWorkloadType = scenario.aggregate.settings.node_properties.workload_options[0];
        }
      }

      vm.scenario = scenario;
      vm.workloadFields = workloadData[defaultWorkloadType];
      vm.workloadDefaults = {};
      vm.steps = workloadData.steps;
      vm.isWorkloadFormInvalid;
      vm.errorStepIndex;
      vm.currentTab = 0;
      vm.isEditRequest = isEditRequest;
      vm.currentStep = vm.isEditRequest ? 2 : 1;
      vm.modalTitle = modalTitle;
      vm.workload = {
        wl_type: srcWorkload ? srcWorkload.wl_type : defaultWorkloadType
      };

      vm.workloadsList = (function () {
        var reqObject = ScenarioDataProcessor.getScenarioInPutRequestFormat(scenario);
        if (srcWorkload) {
          removeItemByProp(reqObject.wl_list, srcWorkload, 'wl_name');
        }
        return reqObject.wl_list;
      }());

      vm.deleteWorkload = function (workloadToDelete) {
        // removing the item from request object & submit
        var reqObject = ScenarioDataProcessor.getScenarioInPutRequestFormat(scenario);
        reqObject.overwrite = true;
        removeItemByProp(reqObject.wl_list, workloadToDelete, 'wl_name');
        submitWorkload(scenario.id, reqObject);
      };

      vm.cloneWorkload = function (workloadToClone) {
        // removing the item from request object & submit
        if ($scope.cloneWorkloadForm.$valid) {
          console.log(" valid ");
          var reqObject = ScenarioDataProcessor.getScenarioInPutRequestFormat(scenario);
          reqObject.overwrite = true;
          reqObject.wl_list.unshift(workloadToClone);
          submitWorkload(scenario.id, reqObject);
        } else {
          console.log(" invalid ");
        }

      };
      vm.selectTab = function (index) {
        var valid = index < this.currentTab;
        if (valid) {
          this.currentTab = index;
        }
      }



      vm.saveWorkload = function (workloadToSave) {
        // return console.log( workloadToSave );
        // adding the item from request object & submit
        var reqObject = ScenarioDataProcessor.getScenarioInPutRequestFormat(scenario);
        /*reqObject.settings_json.fault_tolerance = workloadToSave.fault_tolerance;
        reqObject.settings_json.filters.Compute_Type = reqObject.settings_json.filters.Compute_Type || [];*/
        //incase of edit, add the workload in same index
        // return console.log(reqObject);
        if (vm.workload.wl_type === 'BULK') {
          reqObject.wl_list = reqObject.wl_list.concat(vm.workloadList);
        }
        if (isEditRequest && workloadIndex != -1) {
          reqObject.wl_list.splice(workloadIndex, 1);
          reqObject.wl_list.unshift(workloadToSave);
        }
        //incase of new workload, add the workload in at the last
        else if (vm.workload.wl_type !== 'BULK') {
          reqObject.wl_list.unshift(workloadToSave);
        }
        reqObject.overwrite = true;
        if (workloadToSave.wl_type === "VDI") {
          if (!workloadToSave["vdi_directory"]) {
            vm.workload["disk_per_desktop"] = 0;
            vm.workload["user_iops"] = 0;
          }
        }
        if (workloadToSave.wl_type === "RDSH") {
          if (!workloadToSave["rdsh_directory"]) {
            vm.workload["hdd_per_user"] = 0;
            vm.workload["user_iops"] = 0;
          }
        }
        if (workloadToSave.wl_type === "DB" || workloadToSave.wl_type === "ORACLE") {
          if (workloadToSave['db_type'] === "OLAP") {
            delete workloadToSave.avg_iops_per_db;
          } else if (workloadToSave['db_type'] === "OLTP") {
            delete workloadToSave.avg_mbps_per_db;
          }
        }
        /* if (workloadToSave.wl_type === "ORACLE") {
          vm.workload['num_db_instances'] = 1;
          vm.workload['profile_type'] = "Custom";
        } */
        if (workloadToSave.wl_type === "VDI_INFRA") {
          if (!workloadToSave.vm_details) {
            updateVdiInfraWorkload(true, workloadToSave.infra_type);
          }
          if (workloadToSave.infra_type === 'citrix') {
            workloadToSave.vm_details = workloadToSave['citrix'];
          } else {
            workloadToSave.vm_details = workloadToSave['horizon'];
          }
          delete workloadToSave.citrix;
          delete workloadToSave.horizon;
        }
        if (workloadToSave.wl_type === "EPIC") {
          workloadToSave['cluster_type'] = 'normal';
          delete workloadToSave['clusterList'];
          delete workloadToSave['concurrent_user_pcnt'];
          delete workloadToSave['num_clusters'];
          delete workloadToSave['dc_name'];
        }
        if (workloadToSave.wl_type === 'SPLUNK') {
          workloadToSave['cluster_type'] = 'normal';
          workloadToSave['storage_acc'] = {};
          workloadToSave['storage_acc']['hot'] = workloadToSave['hot'];
          if (workloadToSave.acc_type === "hx+splunk_smartstore") {
            workloadToSave['storage_acc']['warm'] = workloadToSave['warm'];
            delete workloadToSave['app_rf'];
          } else {
            workloadToSave['storage_acc']['cold'] = workloadToSave['cold'];
            workloadToSave['storage_acc']['frozen'] = workloadToSave['frozen'];
          }
          workloadToSave['vm_details'] = {
            'admin': workloadToSave.admin,
            'indexer': workloadToSave.indexer,
            'search': workloadToSave.search
          }
          delete workloadToSave['hot'];
          delete workloadToSave['warm'];
          delete workloadToSave['cold'];
          delete workloadToSave['frozen'];
          delete workloadToSave['admin'];
          delete workloadToSave['indexer'];
          delete workloadToSave['search'];
          delete workloadToSave['app_rf_dup'];
        }
        if (workloadToSave.wl_type === "VEEAM") {
          workloadToSave['cluster_type'] = 'normal';
        }

        if (workloadToSave.wl_type === "AIML" && !workloadToSave.enablestorage) {
          workloadToSave['disk_per_ds'] = 0;
        }

        submitWorkload(scenario.id, reqObject);
      };

      /* Form Field Events */
      $scope.$on("WORKLOAD_FIELD_CLICKED", function ($event, eventData) {
        if (eventData.type === "edit_btn") {
          enableReadOnlyFormFields();
        }
        if (eventData.type === "setting_btn") {
          showAdvancedSettings();
        }
      });

      function ToggleIOPS_MBPS(modelName) {
        var iopsField = getFieldByModelName('avg_iops_per_db', true);
        var mbpsField = getFieldByModelName('avg_mbps_per_db', true);
        if (vm.workload[modelName] === "OLAP") {
          iopsField.hidden = true;
          mbpsField.hidden = false;
        } else if (vm.workload[modelName] === "OLTP") {
          mbpsField.hidden = true;
          iopsField.hidden = false;
        }
      }

      $scope.$on("FILE_SELECTION_CHANGED", function ($event, eventData) {
        var i, field, srcField;
        srcField = getFieldByModelName("isFileInput");
        vm.workload.input_type = eventData.data.input_type;
        if (srcField && srcField.dependantFields && srcField.dependantFields.length) {
          for (i = 0; i < srcField.dependantFields.length; i++) {
            field = getFieldByModelName(srcField.dependantFields[i]);
            vm.workload[field.modelName] = null;
          }
        }

        srcField.hasError = false;
        srcField.isFileInputProcessed = false;
        checkFormValidity();
        $scope.$apply();

      });

      function updateMinMaxUnits(modelName) {
        var fieldName = modelName.replace('_unit', '');
        var fieldToUpdateMinMax = getFieldByModelName(fieldName, true);
        var unit = vm.workload[modelName];
        var config = vm.workloadDefaults[fieldName];
        if (fieldToUpdateMinMax && config) {
          fieldToUpdateMinMax.min = $filter("storageUnit")(config.min, unit, 'GB');
          fieldToUpdateMinMax.max = $filter("storageUnit")(config.max, unit, 'GB');
        }
      }


      $scope.$on("WORKLOAD_FIELD_CHANGED", function ($event, eventData) {

        if (utilService.endsWith(eventData.field.modelName, '_unit')) {
          if (vm.workload.wl_type === 'SPLUNK') {
            updateSplunkVmCount();
          }
          return updateMinMaxUnits(eventData.field.modelName);
        }


        switch (eventData.field.modelName) {
          case "wl_type": {
            onWorkloadTypeChanged(eventData);
            replicationFactorMsg();
            break;
          }
          case "input_mode": {
            onOracleInputModeChange();
            break;
          }
          case "container_type": {
            if (vm.workload.container_type && isCustomProfile(vm.workload.container_type)) {
              updateWorkloadOnProfileTypeChange(true);
              updateFormFieldsPropValue('readonly', false);
            } else {
              updateWorkloadOnProfileTypeChange(true);
              updateFormFieldsPropValue('readonly', true);
            }
            break;
          }
          case "broker_type":
          case "input_type":
          case "expected_util":
          case "profile_type": {
            if (vm.workload.wl_type !== 'SPLUNK') {
              if (vm.workload.profile_type && isCustomProfile(vm.workload.profile_type)) {
                updateWorkloadOnProfileTypeChange(true);
                updateFormFieldsPropValue('readonly', false);
              } else {
                updateWorkloadOnProfileTypeChange(true);
                updateFormFieldsPropValue('readonly', true);
              }
            } else {
              updateMaxVolSplunk();
            }
            break;
          }

          case "db_type": {
            ToggleIOPS_MBPS(eventData.field.modelName);
          }
          case "os_type":
          case "provisioning_type": {
            if (vm.workload.profile_type && isCustomProfile(vm.workload.profile_type)) {

            } else {
              updateWorkloadOnProfileTypeChange(true);
            }
            break;
          }

          case "replication_factor": {
            replicationFactorMsg();
          }
          case "fault_tolerance": {
            checkForReplicationFactorValidity();
            break;
          }
          case "isFileInput": {
            updateInputTypeContent(eventData);
            break;
          }
          case "replication_amt": {
            if (vm.workload.wl_type === "DB" || vm.workload.wl_type === "ORACLE" || vm.workload.wl_type === "VSI") {
              validateReplDr();
            }
            // checkForReplicationAmountValidity(eventData.field);
            break;
          }
          case "num_vms":
          case "num_db_instances": {
            if (vm.workload.wl_type === "DB" || vm.workload.wl_type === "ORACLE" || vm.workload.wl_type === "VSI") {
              validateReplDr();
            }
            // checkForReplicationAmountValidity( getFieldByModelName("replication_amt") );
            break;
          }
          case "remote_replication_enabled": {
            if (isEditRequest) {
              vm.workload.replication_amt = srcWorkload.replication_amt;
            }
            toggleRemoteFields(eventData.field);
            // setTimeout(toggleRemoteFields, 10)
            if (vm.workload.wl_type === "DB" || vm.workload.wl_type === "ORACLE" || vm.workload.wl_type === "VSI") {
              validateReplDr();
            }
            break;
          }
          case "gpu_users": {
            toggleVideoRAMOptionsField();
            break;
          }
          case "cpu_attribute": {
            toggleCpuUnitSelection(eventData.field);
            break;
          }
          case "enablestorage": {
            toggleHDDSizer();
          }
          case "cluster_type": {
            toggleClusterTypeDependentFields(eventData.field);
            replicationFactorMsg();
            break;
          }
          case "dedupe_factor": {
            dynamicTextUpdate(eventData.field);
            break;
          }
          case "compression_factor": {
            dynamicTextUpdate(eventData.field);
            break;
          }
          case "citrix": {
            updateVdiInfraWorkload(true, eventData.field.modelName);
            checkVdiInfraFormValidity(eventData.field.modelName);
            break;
          }
          case "horizon": {
            updateVdiInfraWorkload(true, eventData.field.modelName);
            checkVdiInfraFormValidity(eventData.field.modelName);
            break;
          }
          case "cpu": {
            switch (vm.workload["cpu"]){
              case 'Intel Platinum 8168': vm.workload["guests_per_host"] = 10; break;
              case 'Intel Gold 6150': vm.workload["guests_per_host"] = 12; break;
              case 'Intel Platinum 8268': vm.workload["guests_per_host"] = 14; break;
              case 'Intel Gold 6254': vm.workload["guests_per_host"] = 10; break;
            }
            // vm.workload["guests_per_host"] = vm.workload["cpu"] === "Intel 6150" ? 12 : 10;
            break;
          }
          case "acc_type": {
            changeStorageAccFields();
            break;
          }
          case "daily_data_ingest":
          case "max_vol_ind": {
            updateSplunkVmCount();
            break;
          }
          case "rdsh_directory": {
            updateRdshCheckboxFields();
            break;
          }
          case "vdi_directory": {
            updateVdiCheckboxFields()
          }

        }
      });

      function validateReplDr() {
        vm.workloadFields.steps[2].fields.map(function (field) {
          if (field.type === 'error-message') {
            var num_inst = vm.workload.wl_type === 'DB' || vm.workload.wl_type === "ORACLE" ? vm.workload.num_db_instances : vm.workload.num_vms;
            var num_dr = parseInt(Math.ceil(num_inst * vm.workload.replication_amt / 100))
            if (vm.workload.remote_replication_enabled && num_dr > 1500) {
              field.hidden = false;
              field.hasError = true;
            } else {
              field.hidden = true;
              field.hasError = false;
            }
          }
        });
        checkFormValidity()
      }

      function replicationFactorMsg() {
        vm.workloadFields.steps[2].fields.map(function (field) {
          if (field.model === 'warning_cont') {
            if (vm.workload.cluster_type === 'normal' && vm.workload["replication_factor"] === 2) {
              field.hidden = false;
            } else {
              field.hidden = true;
            }
          }
        });
      }

      function updateRdshCheckboxFields() {
        if (vm.workload["rdsh_directory"]) {
          vm.workloadFields.steps[1].fields.map(function (field) {
            if (field.modelName === 'user_iops' || field.modelName === 'hdd_per_user' || field.modelName === "hdd_per_user_unit") {
              field.hidden = false;
            }
          });
          vm.workloadFields.steps[2].fields.map(function (field) {
            if (field.modelName === 'compression_factor' || field.modelName === 'dedupe_factor') {
              field.readonly = false;
            }
          });
        } else {
          vm.workloadFields.steps[1].fields.map(function (field) {
            if (field.modelName === 'user_iops' || field.modelName === 'hdd_per_user' || field.modelName === "hdd_per_user_unit") {
              field.hidden = true;
            }
          });
          vm.workloadFields.steps[2].fields.map(function (field) {
            if (field.modelName === 'compression_factor' || field.modelName === 'dedupe_factor') {
              field.readonly = true;
            }
          });
        }
      }

      function onOracleInputModeChange() {
        if (vm.workload['input_mode'] === 'Manual') {
          vm.workloadFields.steps[1].fields.map(function (field) {
            if (field.modelName === 'isFileInput') {
              field.hidden = true;
            } else if (field.modelName === 'num_db_instances' || field.modelName === 'profile_type') {
              field.hidden = false;
            }
          });
        } else {
          vm.workloadFields.steps[1].fields.map(function (field) {
            if (field.modelName === 'num_db_instances' || field.modelName === 'profile_type') {
              field.hidden = true;
            } else if (field.modelName === 'isFileInput') {
              field.hidden = false;
            }
          });
        }
      }

      function updateVdiCheckboxFields() {
        if (vm.workload["vdi_directory"]) {
          vm.workloadFields.steps[1].fields.map(function (field) {
            if (field.modelName === 'user_iops' || field.modelName === 'disk_per_desktop' || field.modelName === "disk_per_desktop_unit") {
              field.hidden = false;
            }
          });
          vm.workloadFields.steps[2].fields.map(function (field) {
            if (field.modelName === 'compression_factor' || field.modelName === 'dedupe_factor') {
              field.readonly = false;
            }
          });
        } else {
          vm.workloadFields.steps[1].fields.map(function (field) {
            if (field.modelName === 'user_iops' || field.modelName === 'disk_per_desktop' || field.modelName === "disk_per_desktop_unit") {
              field.hidden = true;
            }
          });
          vm.workloadFields.steps[2].fields.map(function (field) {
            if (field.modelName === 'compression_factor' || field.modelName === 'dedupe_factor') {
              field.readonly = true;
            }
          });
        }
      }

      function updateMaxVolSplunk() {
        vm.workload["max_vol_ind_unit"] = 'GB';
        switch (vm.workload['profile_type']) {
          case 'Enterprise Security': {
            vm.workload["max_vol_ind"] = 100;
            break;
          }
          case 'App for VMWare': {
            vm.workload["max_vol_ind"] = 260;
            break;
          }
          case 'IT Service Intelligence': {
            vm.workload["max_vol_ind"] = 200;
            vm.workload["daily_data_ingest"] = 150;
            break;
          }
          case 'ITOA (IT Operations Analytics)': {
            vm.workload["max_vol_ind"] = 300;
            vm.workload["daily_data_ingest"] = 250;
            break;
          }
        }
        updateSplunkVmCount();
        updateMinMaxUnits('daily_data_ingest_unit');
        updateMinMaxUnits('max_vol_ind_unit');
      }

      function updateSplunkVmCount() {
        var injest, vol;
        injest = $filter("storageUnit")(vm.workload["daily_data_ingest"], 'TB', vm.workload["daily_data_ingest_unit"]);
        if (isNaN(injest)) {
          injest = vm.workload["daily_data_ingest"];
        }
        vol = $filter("storageUnit")(vm.workload["max_vol_ind"], 'TB', vm.workload["max_vol_ind_unit"]);
        if (isNaN(vol)) {
          vol = vm.workload["max_vol_ind"];
        }
        vm.workload['indexer']['num_vms'] = Math.ceil(injest / vol);
        vm.workload['search']['num_vms'] = Math.ceil(vm.workload['indexer']['num_vms'] / 8);
        updateFormFieldsPropValue('readonly', true);
      }

      function changeStorageAccFields() {
        if (vm.workload.acc_type === "hx+splunk_smartstore") {
          vm.workloadFields.steps[1].fields.map(function (field) {
            if (field.modelName === 'warm') {
              field.hidden = false;
            } else if (field.modelName === 'cold' || field.modelName === 'frozen') {
              field.hidden = true;
            } else if (field.modelName === 'hot') {
              field.readonly = true;
              vm.workload[field.modelName] = 1;
            } else if (field.modelName === 'app_rf') {
              field.hidden = true;
            } else if (field.modelName === 'app_rf_dup') {
              field.hidden = false;
              field.readonly = true;
            } else if (field.modelName === 'appRepInfo') {
              field.hidden = false;
            }
          });
        } else {
          vm.workloadFields.steps[1].fields.map(function (field) {
            if (field.modelName === 'warm') {
              field.hidden = true;
            } else if (field.modelName === 'cold' || field.modelName === 'frozen') {
              field.hidden = false;
            } else if (field.modelName === 'hot') {
              field.readonly = false;
            } else if (field.modelName === 'app_rf') {
              field.hidden = false;
            } else if (field.modelName === 'app_rf_dup') {
              field.hidden = true;
            } else if (field.modelName === 'appRepInfo') {
              field.hidden = true;
            }
          });
        }
      }

      function dynamicTextUpdate(eventData) {
        vm.workloadFields.steps[2].fields.forEach(function (fieldData) {
          if (fieldData.type === 'dynamic-text') {
            var diskData = fieldData.diskModel !== 'compression_saved' ? 100.0 : vm.workload[fieldData.diskModel]
            if (fieldData.model !== 'combined_compr_dedup') {
              vm.workload[fieldData.model] = diskData - (diskData * (vm.workload[fieldData.factorModel] / 100));
              fieldData.dynamicMsg = ((fieldData.tooltip.replace('dynamicText', (isNaN(diskData) ? '--' : parseFloat(diskData).toFixed(1) + ' GB'))).replace('dynamicText1', (vm.workload[fieldData.factorModel] === null || vm.workload[fieldData.factorModel] === undefined) ? '--' : vm.workload[fieldData.factorModel])).replace('dynamicText2', (isNaN(vm.workload[fieldData.model]) ? '--' : parseFloat(vm.workload[fieldData.model]).toFixed(1) + ' GB'));
            } else {
              var x = ((diskData - vm.workload[fieldData.factorModel]) / diskData) * 100
              fieldData.dynamicMsg = (isNaN(x) ? '--' : parseFloat(x).toFixed(1)) + '% (' + (isNaN(diskData / vm.workload[fieldData.factorModel]) ? '--' : parseFloat(diskData / vm.workload[fieldData.factorModel]).toFixed(2)) + ' : 1)';
              /* fieldData.dynamicText1 = x + '%';
              fieldData.dynamicText2 = parseFloat(diskData / vm.workload[fieldData.factorModel]).toFixed(2) + ' : 1'; */
            }
          }
        })
      }

      function updateInputTypeContent(eventData) {
        toggleRawWorkloadProfileInputs(eventData.field);

        window._mpl_fileUploadData = null;
        eventData.field.hasError = false;
        eventData.field.isFileInputProcessed = false;

        /* for backend reporting purpose */
        vm.workload.input_type = vm.workload.isFileInput ? vm.workload.input_type : "Manual";

        checkFormValidity();
        /*this is for backend use to decide whether to show warning while generating report*/
        delete vm.workload["hasWarning"]
      }

      function toggleClusterTypeDependentFields(field) {
        field = field || getFieldByModelName("cluster_type");
        if (!field) return;
        var clusterType = vm.workload[field.modelName];
        var rfField = getFieldByModelName("replication_factor");
        var ftField = getFieldByModelName("fault_tolerance");
        var replicationField = getFieldByModelName("remote_replication_enabled");
        if (clusterType === 'stretch') {
          rfField.readonly = true;
          ftField.readonly = true;
          replicationField && (replicationField.readonly = true);
          vm.workload[rfField.modelName] = 2;
          vm.workload[ftField.modelName] = 0;
          vm.workload['remote_replication_enabled'] = false;
        } else {
          rfField.readonly = false;
          ftField.readonly = false;
          replicationField && (replicationField.readonly = false);
        }
        checkForReplicationFactorValidity();
        toggleRemoteFields();
      }

      function toggleCpuUnitSelection(field) {
        field = field || getFieldByModelName("cpu_attribute");
        var val = vm.workload[field.modelName];
        var coresField = getFieldByModelName("vcpus");
        var clocksField = getFieldByModelName("cpu_clock");
        if (val === "vcpus") {
          coresField.hidden = false;
          clocksField.hidden = true;
          if (!vm.workload.isFileInput) {
            coresField.value = (vm.workload.vcpus == 0) ? vm.workload.vcpus : vm.workload.vcpus || coresField.defaultValue;
            vm.workload.vcpus = coresField.value;
          }

        } else if (val === "cpu_clock") {
          coresField.hidden = true;
          clocksField.hidden = false;
          if (!vm.workload.isFileInput) {
            clocksField.value = (vm.workload.cpu_clock == 0) ? vm.workload.cpu_clock : vm.workload.cpu_clock || clocksField.defaultValue;
            vm.workload.cpu_clock = clocksField.value;
          }
        }
        coresField.hasError = false;
        clocksField.hasError = false;
        checkFormValidity();
      }

      function toggleVideoRAMOptionsField() {
        var videoRAMOptionsField = getFieldByModelName("video_RAM");
        if (videoRAMOptionsField) {
          videoRAMOptionsField.hidden = !vm.workload.gpu_users;
        }
      }

      function toggleHDDSizer() {
        var hddSizerOptionsField = getFieldByModelName("disk_per_ds");
        var hddSizerUnitOptionsField = getFieldByModelName("disk_per_ds_unit")
        if (hddSizerOptionsField && hddSizerUnitOptionsField) {
          hddSizerOptionsField.hidden = !vm.workload.enablestorage;
          hddSizerUnitOptionsField.hidden = !vm.workload.enablestorage;
        }
      }

      function toggleGPUOptionsField() {
        var isHypervSelected = (vm.scenario.aggregate.settings.hypervisor === "hyperv");
        if (isHypervSelected) {
          var gpu_usersOptionsField = getFieldByModelName("gpu_users");
          if (gpu_usersOptionsField) {
            vm.workload.gpu_users = false;
            gpu_usersOptionsField.readonly = true;
          }
        }
      }

      function toggleRemoteFields(remoteField) {
        var remoteField = getFieldByModelName("remote");
        var replicationAmtField = getFieldByModelName("replication_amt");
        var shouldHide = vm.workload.remote_replication_enabled ? false : true;
        if (remoteField && replicationAmtField) {
          remoteField.hidden = shouldHide;
          replicationAmtField.hidden = shouldHide;
        }

        if (replicationAmtField) {
          vm.workload.replication_amt = vm.workload.replication_amt || 100;//100 is the default value, (::TODO:: essentially it should be taken from json file)
          replicationAmtField.hasError = false;
        }

        // to disable / enable cluster type input filed
        // var clusterTypeField = getFieldByModelName("cluster_type");
        // if(clusterTypeField) {
        //   clusterTypeField.readonly = vm.workload.remote_replication_enabled;
        // }

        checkFormValidity();
      }

      function checkForReplicationAmountValidity(formField) {

        var dependantProp;
        var errorMessage = "Value should be less than ";
        switch (vm.workload.wl_type) {
          case "VSI":
            dependantProp = "num_vms";
            errorMessage += "Number of VMs"
            break;
          case "DB":
          case "ORACLE":
            dependantProp = "num_db_instances";
            errorMessage += "Number of Databases"
            break;
          default:
            dependantProp = errorMessage = "";
        }

        if (vm.workload.replication_amt > vm.workload[dependantProp]) {
          formField.hasReplAmntError = true;
          formField.errorMessage = errorMessage;
        } else {
          formField.hasReplAmntError = false;
          formField.errorMessage = "";
        }
      }

      function toggleRawWorkloadProfileInputs(srcField) {
        var i, field, isFileInput, workloadDefaults;
        isFileInput = vm.workload[srcField.modelName];
        if (!isFileInput) {
          workloadDefaults = ScenarioDataProcessor.getDefaultValues(vm.workload);
        } else {
          vm.workload.cpu_attribute = 'vcpus';
        }

        if (vm.isEditRequest && isFileInput === srcWorkload.isFileInput) {
          vm.workload['overhead_percentage'] = (srcWorkload['overhead_percentage'] === undefined) ? vm.workload['overhead_percentage'] : srcWorkload['overhead_percentage'];
        } else {
          vm.workload['overhead_percentage'] = isFileInput ? 10 : 0;
        }

        if (srcField.dependantFields && srcField.dependantFields.length) {
          for (i = 0; i < srcField.dependantFields.length; i++) {
            field = getFieldByModelName(srcField.dependantFields[i]);
            if (field) {
              field.readonly = isFileInput;
            }
            if (vm.workload[srcField.modelName]) {//if the input type is file type
              vm.workload[field.modelName] = isEditRequest ? srcWorkload[field.modelName] : null
            } else {
              vm.workload[field.modelName] = isEditRequest ? srcWorkload[field.modelName] : workloadDefaults[field.modelName].value;
            }
          }
        }
        updateFormFieldsPropValue("readonly", isFileInput);
      }

      function checkForReplicationFactorValidity() {
        var field = getFieldByModelName('replication_factor');
        if (field) {
          if (vm.workload.replication_factor == 2 && vm.workload.fault_tolerance == 2) {
            field.hasError = true;
          } else {
            field.hasError = false;
          }
        }
        checkFormValidity();
        if (field) {

          if (vm.workload.replication_factor == 3 && vm.workload.fault_tolerance == 2) {
            $('.withoutContent').addClass('withContent')
            field.hasInfo = true;
          } else {
            $('.withoutContent').removeClass('withContent')
            field.hasInfo = false;
          }
          if(vm.workload.replication_factor == 2 && vm.workload.fault_tolerance == 2){
            $('.withoutContent').addClass(' withContentError')
          }
          else{
            $('.withoutContent').removeClass(' withContentError')
          }
        }
      }

      function getFieldByModelName(modelName, includeDependentFields) {
        var stepIndex, fieldIndex, currentStep, currentField;
        // updating step fields
        for (stepIndex = 0; stepIndex < vm.workloadFields.steps.length; stepIndex++) {
          currentStep = vm.workloadFields.steps[stepIndex];
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

      function updateWorkloadFielsOracle(data) {
        vm.workload['profile_type'] = 'Custom'
        updateFormFieldsPropValue('readonly', false);
        var fieldIndex, currentStep, currentField;
        currentStep = vm.workloadFields.steps[1];

        if (currentStep.dependentFields) {
          for (fieldIndex = 0; fieldIndex < currentStep.dependentFields.length; fieldIndex++) {
            currentField = currentStep.dependentFields[fieldIndex];
            if (currentField.modelName !== 'db_size_unit') {
              vm.workload[currentField.modelName] = data[currentField.modelName];
              if (currentField.modelName === 'db_size' || currentField.modelName === 'metadata_size') {
                currentField.hasError = true;
                currentField.outOfRangeError = true;
              }
            }
          }
        }
        checkFormValidity();
      }

      function updateWorkloadWithFileUploadData(data) {
        for (var prop in data) {
          if (vm.workload.hasOwnProperty(prop)) {
            if (isNaN(data[prop])) {
              vm.workload[prop] = data[prop];
            } else {
              vm.workload[prop] = parseFloat(data[prop]);
            }
          }
        }
      }

      /*updating workload data from file inputs uploaded from UI*/
      $scope.$on("FORM_UPLOAD_SUCCESS", function ($event, eventData) {

        if (vm.workload.wl_type === "RAW" || vm.workload.wl_type === "RAW_FILE" || vm.workload.wl_type === "AWR_FILE") {
          vm.workload.provisioned = !(!eventData.isProvisioned);
          if (vm.workload.provisioned) {
            updateWorkloadWithFileUploadData(eventData.data.provisioned);
          } else {
            updateWorkloadWithFileUploadData(eventData.data.utilized);
          }
          // this is to update the selection in UI
          if (vm.workload.wl_type !== "AWR_FILE") {
            toggleCpuUnitSelection();
          }
        } else if (vm.workload.wl_type === "ORACLE") {
          updateWorkloadFielsOracle(eventData.data);
        } else {
          updateWorkloadWithFileUploadData(eventData.data);
          if (vm.workload.wl_type === "BULK") {
            vm.workloadList = eventData.data;
          }
        }

        var field = getFieldByModelName("isFileInput");

        if (eventData.data.hasDataInputError) {
          field.hasError = true;
          field.isFileInputProcessed = false;
        } else {
          field.hasError = false;
          field.isFileInputProcessed = true;
        }

        checkFormValidity();

        /*this is for backend use to decide whether to show warning while generating report*/
        if (eventData.hasWarning) {
          vm.workload.hasWarning = true;
        } else {
          delete vm.workload["hasWarning"]
        }
      });

      /*updating workload data from file inputs uploaded from UI*/
      $scope.$on("FORM_UPLOAD_ERROR", function ($event, eventData) {
        var field = getFieldByModelName("isFileInput");
        field.hasError = true;
        field.isFileInputProcessed = false;
        checkFormValidity();
      });

      $scope.$on("WORKLOAD_FIELD_BLUR", function ($event, eventData) {
        if (eventData.field.modelName === "wl_name") {
          checkWorkloadNameValidity(eventData.field);
        }
      });

      $scope.$on("WORKLOAD_FIELD_VALIDATION", function ($event, eventData) {
        if (eventData.type === 'vdi_infra') {
          checkVdiInfraFormValidity(eventData.item);
        } else if (eventData.type === 'epic') {
          checkEpicValidity();
        } else {
          checkFormValidity();
        }
      });

      //VDI INFRA validity
      function checkVdiInfraFormValidity(selectedItem) {
        vm.isWorkloadFormInvalid = getVdiInfraFormValidationStatus(selectedItem);
      }

      //
      function checkFormValidity() {
        vm.isWorkloadFormInvalid = getFormValidationStatus();
      }

      function checkEpicValidity() {
        vm.isWorkloadFormInvalid = getEpicFormValidationstatus();
      }

      function onWorkloadTypeChanged() {
        window._$clonedFile = false;
        window._mpl_fileUploadData = null;
        vm.workload = {
          wl_type: vm.workload.wl_type
        };
        updateWorkloadFormFields();
        udpateWorkloadData();
        updateWorkloadOnProfileTypeChange(false);

        //remove/add the replication factor warning message
        checkForReplicationFactorValidity();
        // show / hide remote replication fields
        toggleRemoteFields();

        //enable the fields by default for custom profile type
        if (vm.workload.profile_type && isCustomProfile(vm.workload.profile_type)) {
          updateFormFieldsPropValue('readonly', false);
        }

        if (vm.workload.wl_type === "DB" || vm.workload.wl_type === "ORACLE" || vm.workload.wl_type === "AWR_FILE") {
          ToggleIOPS_MBPS('db_type');
        }
        if (vm.workload.wl_type === "ORACLE") {
          onOracleInputModeChange();
        }

        if (vm.workload.wl_type === "RAW" || vm.workload.wl_type === "RAW_FILE" || vm.workload.wl_type === "AWR_FILE" || vm.workload.wl_type === "EXCHANGE" || vm.workload.wl_type === "BULK") {
          var field = getFieldByModelName("isFileInput");
          /* for backend reporting purpose */
          vm.workload.input_type = vm.workload.isFileInput ? vm.workload.input_type : "Manual";

          if (field) {
            field.hasError = false;
            field.isFileInputProcessed = false;
            toggleRawWorkloadProfileInputs(field);
            if (isEditRequest) {
              window._$clonedFile = {};
              field.isFileInputProcessed = true;
            }
          }
          checkFormValidity();
        }

        if (vm.workload.wl_type === "VDI") {
          toggleVideoRAMOptionsField();
          toggleGPUOptionsField();
          updateVdiCheckboxFields();
        } else if (vm.workload.wl_type === "RAW" || vm.workload.wl_type === "RAW_FILE") {
          toggleCpuUnitSelection();
        }

        if (vm.workload.wl_type === "RDSH") {
          toggleVideoRAMOptionsField();
          toggleGPUOptionsField();
          updateRdshCheckboxFields();
        }

        if (vm.workload.wl_type === "RAW" || vm.workload.wl_type === "RAW_FILE") {
          updateRAWWorkloadCPUModels();
        }
        if (vm.workload.wl_type === "VDI_INFRA" && vm.isEditRequest) {
          var vmData = JSON.parse(JSON.stringify(vm.workload.vm_details));
          vm.workload.vm_details = {};
          vm.workload[vm.workload.infra_type] = vmData;
        }

        if (vm.workload.wl_type === "SPLUNK") {
          changeStorageAccFields();
          if (!vm.isEditRequest) {
            updateMaxVolSplunk();
          }
        }

        if (vm.workload.wl_type === "SPLUNK" && vm.isEditRequest) {
          angular.forEach(vm.workload['storage_acc'], function (value, key) {
            vm.workload[key] = value;
          });
          angular.forEach(vm.workload['vm_details'], function (value, key) {
            vm.workload[key] = value;
          });
          if (vm.workload['custom_data']) {
            updateFormFieldsPropValue('readonly', false);
          }
        }

        if (vm.workload.wl_type === "EPIC" || vm.workload.wl_type === "SPLUNK" || vm.workload.wl_type === "VEEAM") {
          vm.workload['cluster_type'] = 'normal';
        }

        if (vm.workload.wl_type === "AIML") {
          toggleHDDSizer();
        }


        toggleClusterTypeDependentFields();

        toggleClusterTypeVisibility();

      }

      function updateRAWWorkloadCPUModels() {
        var cpuModels = appService.getCPUModels();
        var cpuModelField = getFieldByModelName("cpu_model");
        if (cpuModelField) {
          cpuModelField.options = cpuModels;
        }
      }

      /*
      Disabled 'Cluster Type' & Replication input field if the scenario is of fixed config sizing
      */
      function toggleClusterTypeVisibility() {
        var isHypervSelected = (vm.scenario.aggregate.settings.hypervisor === "hyperv");

        if (vm.scenario.sizing_type === 'fixed' || isHypervSelected) {
          var clusterTypeField = getFieldByModelName("cluster_type");
          var replicationEnablingField = getFieldByModelName("remote_replication_enabled");



          if (clusterTypeField) {
            clusterTypeField.readonly = true;
            toggleStretchClusterReplicationTooltip(clusterTypeField, isHypervSelected);
          }
          if (replicationEnablingField) {
            replicationEnablingField.readonly = true;
            toggleStretchClusterReplicationTooltip(replicationEnablingField, isHypervSelected);
          }
        }
      }

      function toggleStretchClusterReplicationTooltip(inputField, isHypervSelected) {
        if (isHypervSelected) {
          inputField.tooltip.readonly = "Replication and Stretch Cluster are not supported in Hyper-V clusters";
        }
      }

      function isCustomProfile(profile) {
        return profile.indexOf("Custom") != -1
      }


      onWorkloadTypeChanged();

      function udpateWorkloadData() {
        var defaultWorkload = ScenarioDataProcessor.getDefaultWorkload(vm.workload);
        vm.workload = angular.extend(defaultWorkload, srcWorkload);
        if (isAddRequest) {
          vm.workload.wl_name = getDefaultWorkloadName(vm.workload.wl_type);
        }

      }

      function updateWorkloadFormFields() {
        vm.workloadFields = workloadData[vm.workload.wl_type];
        if (scenario.aggregate.settings.node_properties) {
          var supportedWorkloads = scenario.aggregate.settings.node_properties.workload_options;
          var excludedWls = scenario.excludeWls;
          if (supportedWorkloads && excludedWls) {
            var workloadTypeField = getFieldByModelName('wl_type');
            var workloadTypeOptions = workloadTypeField.options;
            var workloadOption;
            for (var optinIndex = workloadTypeOptions.length - 1; optinIndex > -1; optinIndex--) {
              workloadOption = workloadTypeOptions[optinIndex];
              workloadOption.disabled = (supportedWorkloads.indexOf(workloadOption.value) === -1 || excludedWls.indexOf(workloadOption.value) !== -1);
            }
          }
        }

        vm.isWorkloadFormInvalid = false;
        vm.errorStepIndex = -1;
        updateFormFieldsPropValue('hasError', false);
      }

      // this is enable the form fields to edit and change the profile type of custom
      function updateFormFieldsPropValue(prop, value) {
        var stepIndex, fieldIndex, currentStep, currentField, rowIndex, rowField, colIndex;
        var totalSteps = [].concat(vm.workloadFields.steps);
        var excludedFields = ["cluster_type", "replication_factor", "fault_tolerance", "remote_replication_enabled"];


        for (stepIndex = 1; stepIndex < totalSteps.length; stepIndex++) {
          currentStep = totalSteps[stepIndex];
          for (fieldIndex = 0; fieldIndex < currentStep.fields.length; fieldIndex++) {
            currentField = currentStep.fields[fieldIndex];
            if (currentField[prop] !== undefined && excludedFields.indexOf(currentField.modelName) === -1 && vm.workload.wl_type !== 'SPLUNK') {
              currentField[prop] = value;
            }
            currentField.isNameEmpty = currentField.isDuplicateName = false;
          }

          if (currentStep.dependentFields) {
            for (fieldIndex = 0; fieldIndex < currentStep.dependentFields.length; fieldIndex++) {
              if (vm.workload.wl_type !== 'SPLUNK') {
                currentField = currentStep.dependentFields[fieldIndex];
                if (currentField[prop] !== undefined) {
                  currentField[prop] = value;
                }
              } else {
                if (fieldIndex != 0) {
                  for (rowIndex = 0; rowIndex < currentStep.dependentFields[fieldIndex].rows.length; rowIndex++) {
                    rowField = currentStep.dependentFields[fieldIndex].rows[rowIndex];
                    for (colIndex = 0; colIndex < rowField.columns.length; colIndex++) {
                      if (rowField.columns[colIndex][prop] !== undefined) {
                        rowField.columns[colIndex][prop] = value;
                      }
                    }
                  }
                }
              }
              currentField.isNameEmpty = currentField.isDuplicateName = false;
            }

          }
        }
      }

      function enableReadOnlyFormFields() {
        if (vm.workload.wl_type !== 'SPLUNK') {
          if (vm.workload.wl_type !== "CONTAINER") {
            vm.workload.profile_type = (vm.workload.wl_type === "VDI" || vm.workload.wl_type === "RDSH") ? "Custom User" : "Custom";
          } else {
            vm.workload.container_type = "Custom";
          }
          // this is to update min/max values of form fields
          updateWorkloadOnProfileTypeChange(false);
        } else {
          vm.workload['custom_data'] = true;
        }
        updateFormFieldsPropValue('readonly', false);
      }

      /* ============ ADVANCED SETTINGS CONTENT ============ */

      function checkWorkloadNameValidity(field) {
        field.isNameEmpty = field.isDuplicateName = field.hasError = false;
        if (!vm.workload.wl_name) {
          field.isNameEmpty = true;
          field.isDuplicateName = false;
          field.hasError = true;
        } else if (isDuplicateValue(vm.workloadsList, vm.workload, 'wl_name')) {
          field.isNameEmpty = false;
          field.isDuplicateName = true;
          field.hasError = true;
        }
        checkFormValidity();
      };

      /* Updating the infra fields to default on change */
      function updateVdiInfraWorkload(updateFieldValue, modelName) {
        vm.workloadDefaults = ScenarioDataProcessor.getDefaultValues(vm.workload);
        modelName = modelName || 'citrix';
        var stepIndex, fieldIndex, currentStep, currentField, columnIndex, columnField;
        for (stepIndex = 1; stepIndex < vm.workloadFields.steps.length; stepIndex++) {
          currentStep = vm.workloadFields.steps[stepIndex];
          if (stepIndex === 1) {
            for (fieldIndex = 0; fieldIndex < currentStep.fields[0].fields[modelName].rows.length; fieldIndex++) {
              currentField = currentStep.fields[0].fields[modelName].rows[fieldIndex];
              for (columnIndex = 0; columnIndex < currentField.columns.length; columnIndex++) {
                columnField = currentField.columns[columnIndex];
                if (columnField.modelName && vm.workloadDefaults[currentField.value]) {
                  columnField.min = vm.workloadDefaults[currentField.value][columnField.modelName].min;
                  columnField.max = vm.workloadDefaults[currentField.value][columnField.modelName].max;
                  if (updateFieldValue) {
                    columnField.value = vm.workloadDefaults[currentField.value][columnField.modelName].value;
                    /* if (!vm.workload.vm_details) {
                      vm.workload.vm_details = {};
                    } */
                    if (!vm.workload[modelName]) {
                      vm.workload[modelName] = {};
                    }
                    if (!vm.workload[modelName][currentField.value]) {
                      vm.workload[modelName][currentField.value] = {};
                    }
                    vm.workload[modelName][currentField.value][columnField.modelName] = vm.workload[modelName][currentField.value][columnField.modelName] === undefined ? columnField.value : vm.workload[modelName][currentField.value][columnField.modelName];
                    if (columnField.unit) {
                      vm.workload[modelName][currentField.value][columnField.modelName + '_unit'] = columnField.unit;
                    }
                  }
                }
              }
            }
          } else {
            for (fieldIndex = 0; fieldIndex < currentStep.fields.length; fieldIndex++) {
              currentField = currentStep.fields[fieldIndex];
              if (currentField.modelName && vm.workloadDefaults[currentField.modelName]) {
                currentField.min = vm.workloadDefaults[currentField.modelName].min;
                currentField.max = vm.workloadDefaults[currentField.modelName].max;
                if (updateFieldValue) {
                  currentField.value = vm.workloadDefaults[currentField.modelName].value;
                  vm.workload[currentField.modelName] = vm.workload[currentField.modelName] || currentField.value;
                }
              }
            }
          }
          if (currentStep.dependentFields) {
            for (fieldIndex = 0; fieldIndex < currentStep.dependentFields.length; fieldIndex++) {
              currentField = currentStep.dependentFields[fieldIndex];
              if (currentField.modelName && vm.workloadDefaults[currentField.modelName]) {
                currentField.min = vm.workloadDefaults[currentField.modelName].min;
                currentField.max = vm.workloadDefaults[currentField.modelName].max;
                if (updateFieldValue) {
                  currentField.value = vm.workloadDefaults[currentField.modelName].value;
                  vm.workload[currentField.modelName] = currentField.value;
                }
              }
            }
          }
        }
      }

      // this is to set the fields to default values
      function updateWorkloadOnProfileTypeChange(updateFieldValue) {
        vm.workloadDefaults = ScenarioDataProcessor.getDefaultValues(vm.workload);
        var stepIndex, fieldIndex, currentStep, currentField, rowIndex, rowField, colIndex, colField;

        // updating step fields
        if (vm.workload.wl_type !== 'VDI_INFRA') {
          for (stepIndex = 1; stepIndex < vm.workloadFields.steps.length; stepIndex++) {
            currentStep = vm.workloadFields.steps[stepIndex];
            for (fieldIndex = 0; fieldIndex < currentStep.fields.length; fieldIndex++) {
              currentField = currentStep.fields[fieldIndex];
              if (currentField.modelName === 'datacentres') {
                currentField.fields.map(function (field, index) {
                  var dcData = {};
                  dcData[field.modelName] = field.name;
                  field.column.map(function (col) {
                    if (col.modelName && vm.workloadDefaults[currentField.modelName][field.name][col.modelName]) {
                      dcData[col.modelName] = vm.workload[currentField.modelName][index][col.modelName] || vm.workloadDefaults[currentField.modelName][field.name][col.modelName].value;
                      col.min = vm.workloadDefaults[currentField.modelName][field.name][col.modelName].min;
                      col.max = vm.workloadDefaults[currentField.modelName][field.name][col.modelName].max;
                      col.value = vm.workloadDefaults[currentField.modelName][field.name][col.modelName].value;
                    }
                  });
                  if (updateFieldValue) {
                    vm.workload[currentField.modelName].push(dcData);
                  }
                });
              } else if (currentField.modelName && vm.workloadDefaults[currentField.modelName]) {
                currentField.min = vm.workloadDefaults[currentField.modelName].min;
                currentField.max = vm.workloadDefaults[currentField.modelName].max;
                if (updateFieldValue) {
                  currentField.value = vm.workloadDefaults[currentField.modelName].value;
                  vm.workload[currentField.modelName] = currentField.value;
                }
              }
            }
            if (currentStep.dependentFields) {
              for (fieldIndex = 0; fieldIndex < currentStep.dependentFields.length; fieldIndex++) {
                currentField = currentStep.dependentFields[fieldIndex];
                if (vm.workload.wl_type !== 'SPLUNK') {
                  if (currentField.modelName && vm.workloadDefaults[currentField.modelName]) {
                    currentField.min = vm.workloadDefaults[currentField.modelName].min;
                    currentField.max = vm.workloadDefaults[currentField.modelName].max;
                    if (updateFieldValue) {
                      currentField.value = vm.workloadDefaults[currentField.modelName].value;
                      vm.workload[currentField.modelName] = currentField.value;
                    }
                  }
                } else {
                  if (fieldIndex != 0) {
                    for (rowIndex = 0; rowIndex < currentField.rows.length; rowIndex++) {
                      rowField = currentField.rows[rowIndex];
                      for (colIndex = 0; colIndex < rowField.columns.length; colIndex++) {
                        colField = rowField.columns[colIndex]
                        if (colField.modelName && vm.workloadDefaults[rowField.value][colField.modelName]) {
                          colField.min = vm.workloadDefaults[rowField.value][colField.modelName].min;
                          colField.max = vm.workloadDefaults[rowField.value][colField.modelName].max;
                          // if (updateFieldValue) {
                          if (!vm.workload[rowField.value]) {
                            vm.workload[rowField.value] = {};
                          }
                          colField.value = vm.workloadDefaults[rowField.value][colField.modelName].value;
                          vm.workload[rowField.value][colField.modelName] = colField.value;
                          // }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        } else {
          updateVdiInfraWorkload(updateFieldValue);
        }
      }

      function getVdiInfraFormValidationStatus(selectedItem) {
        var stepIndex, fieldIndex, currentStep, currentField, columnIndex, columnField, vm_count = 0;

        var totalSteps = [].concat(vm.workloadFields.steps);
        for (stepIndex = 1; stepIndex < totalSteps.length; stepIndex++) {
          currentStep = totalSteps[stepIndex];
          if (stepIndex === 1) {
            for (fieldIndex = 0; fieldIndex < currentStep.fields[0].fields[selectedItem].rows.length; fieldIndex++) {
              currentField = currentStep.fields[0].fields[selectedItem].rows[fieldIndex];
              for (columnIndex = 0; columnIndex < currentField.columns.length; columnIndex++) {
                columnField = currentField.columns[columnIndex];
                if (!columnField.hidden && columnField.hasError) {
                  vm.errorStepIndex = stepIndex;
                  return true;
                }
                if (columnField.modelName === 'num_vms') {
                  vm_count += columnField.value;
                }
              }
            }
          } else {
            for (fieldIndex = 0; fieldIndex < currentStep.fields.length; fieldIndex++) {
              currentField = currentStep.fields[fieldIndex];
              if (!currentField.hidden && currentField.hasError) {
                vm.errorStepIndex = stepIndex;
                return true;
              }
            }
          }
          if (currentStep.dependentFields) {
            for (fieldIndex = 0; fieldIndex < currentStep.dependentFields.length; fieldIndex++) {
              currentField = currentStep.dependentFields[fieldIndex];
              if (!currentField.hidden && currentField.hasError) {
                vm.errorStepIndex = stepIndex;
                return true;
              }
            }
          }
        }
        if (vm_count < 1) {
          return true;
        }
      }

      //epic workload validation
      function getEpicFormValidationstatus() {
        var stepIndex, fieldIndex, currentStep, currentField, colIndex, colField, index;
        var userEpicFlag = 0;
        var totalSteps = [].concat(vm.workloadFields.steps);

        for (stepIndex = 1; stepIndex < totalSteps.length; stepIndex++) {
          currentStep = totalSteps[stepIndex];
          for (fieldIndex = 0; fieldIndex < currentStep.fields.length; fieldIndex++) {
            currentField = currentStep.fields[fieldIndex];
            if (currentField.modelName === 'datacentres') {
              for (colIndex = 0; colIndex < currentField.fields.length; colIndex++) {
                colField = currentField.fields[colIndex];
                for (index = 0; index < colField.column.length; index++) {
                  var col = colField.column[index];
                  if (col.modelName === 'concurrent_user_pcnt' && col.value === 0) {
                    userEpicFlag++;
                  }
                  if (!col.hidden && col.hasError) {
                    vm.errorStepIndex = stepIndex;
                    return true;
                  }
                };
              }
              if (userEpicFlag === currentField.fields.length) {
                return true;
              }
            } else {
              if (!currentField.hidden && currentField.hasError) {
                vm.errorStepIndex = stepIndex;
                return true;
              }
            }
          }
          if (currentStep.dependentFields) {
            for (fieldIndex = 0; fieldIndex < currentStep.dependentFields.length; fieldIndex++) {
              currentField = currentStep.dependentFields[fieldIndex];
              if (!currentField.hidden && currentField.hasError) {
                vm.errorStepIndex = stepIndex;
                return true;
              }
            }
          }
        }

        return false;
      }

      // private/internal functions
      function getFormValidationStatus() {
        var stepIndex, fieldIndex, currentStep, currentField, rowIndex, rowField, colIndex, colField;

        var totalSteps = [].concat(vm.workloadFields.steps);

        for (stepIndex = 1; stepIndex < totalSteps.length; stepIndex++) {
          currentStep = totalSteps[stepIndex];
          for (fieldIndex = 0; fieldIndex < currentStep.fields.length; fieldIndex++) {
            currentField = currentStep.fields[fieldIndex];
            if (!currentField.hidden && currentField.hasError) {
              vm.errorStepIndex = stepIndex;
              return true;
            }
          }
          if (currentStep.dependentFields) {
            for (fieldIndex = 0; fieldIndex < currentStep.dependentFields.length; fieldIndex++) {
              currentField = currentStep.dependentFields[fieldIndex];
              if (vm.workload.wl_type !== 'SPLUNK') {
                if (!currentField.hidden && currentField.hasError) {
                  vm.errorStepIndex = stepIndex;
                  return true;
                }
              } else {
                if (fieldIndex != 0) {
                  for (rowIndex = 0; rowIndex < currentField.rows.length; rowIndex++) {
                    rowField = currentField.rows[rowIndex];
                    for (colIndex = 0; colIndex < rowField.columns.length; colIndex++) {
                      colField = rowField.columns[colIndex]
                      if (!colField.hidden && colField.hasError) {
                        vm.errorStepIndex = stepIndex;
                        return true;
                      }
                    }
                  }
                }
              }
            }
          }
        }

        if ((vm.currentStep > 1 && (vm.workload.wl_type === "RAW" || vm.workload.wl_type === "RAW_FILE" || vm.workload.wl_type === "EXCHANGE" || vm.workload.wl_type === "AWR_FILE") || vm.workload.wl_type === "BULK")) {
          var field = getFieldByModelName("isFileInput");
          if (field && vm.workload[field.modelName] && !field.isFileInputProcessed) {
            vm.errorStepIndex = 1;
            return true;
          }
        }

        if (vm.currentStep > 1 && vm.workload.wl_type === "RAW" || vm.workload.wl_type === "RAW_FILE") {

        }

        return false;
      }

      function submitWorkload(scenarioId, srcReqData) {
        var reqData = JSON.parse(JSON.stringify(srcReqData));
        reqData.wl_list.forEach(function (workload) {
          for (var prop in workload) {
            if (prop.indexOf("_ui") === 0) {
              delete workload[prop];
            }
          }
          delete workload['clusterList'];
          if (workload.wl_type === "EPIC") {
            delete workload['concurrent_user_pcnt'];
            delete workload['num_clusters'];
            delete workload['dc_name'];
          }
        });
        reqData.wl_list = utilService.filteredList(reqData.wl_list, function (wl) {
          return !((wl.wl_type === 'VDI' || wl.wl_type === 'RDSH') && wl.hasOwnProperty('primary_wl_name'));
        })
        scenarioService.save({ id: scenarioId }, reqData).$promise.then(function (updatedScenario) {
          $uibModalInstance.close(updatedScenario);
        }, function () {
          // error in saving workload
        });
      }

      function removeItemByProp(list, item, prop) {
        for (var i = 0; i < list.length; i++) {
          if (list[i][prop] == item[prop]) {
            list.splice(i, 1);
            return i;
          }
        }
      }

      function replaceItemByProp(list, item, prop) {
        for (var i = 0; i < list.length; i++) {
          if (list[i][prop] == item[prop]) {
            list[i] = item;
            return i;
          }
        }
      }

      function isDuplicateValue(list, item, prop) {
        var value = item[prop].toLocaleLowerCase();
        for (var i = 0; i < list.length; i++) {
          if (list[i][prop].toLocaleLowerCase() == value) {
            return true;
          }
        }
        return false;
      }

      function getWorkloadIndex(list, item, prop) {
        if (item && prop) {
          var value = item[prop].toLocaleLowerCase();
          for (var i = 0; i < list.length; i++) {
            if (list[i][prop].toLocaleLowerCase() == value) {
              return i;
            }
          }
        }
        return -1;
      }

      function getDefaultWorkloadName(wlType) {
        if (!wlType) {
          return '';
        }

        var seperator = "-";

        var wlName, str, numPartOfNames = [];
        for (var i = 0; i < vm.workloadsList.length; i++) {
          if (vm.workloadsList[i].wl_type == wlType) {
            str = vm.workloadsList[i].wl_name.split(seperator);
            if (str.length > 1) {
              str = str[str.length - 1];
              if (!isNaN(str)) {
                numPartOfNames.push(parseInt(str));
              }
            }
          }
        }

        //sort the elements
        numPartOfNames.sort(function (a, b) { return a - b; });
        switch (wlType) {
          case "ROBO":
            wlName = "Edge"; break;
          case "EXCHANGE":
            wlName = "MS_EXCHANGE"; break;
          case "DB":
            wlName = "MSSQL"; break;
          default:
            wlName = wlType;
        }
        wlName = wlName + seperator + ((numPartOfNames[numPartOfNames.length - 1] || 0) + 1);

        return wlName;
      }

      $scope.$on('$destroy', function () {
        window._mpl_fileUploadData = null;
      })

    }]);

})();
