angular.module('hyperflex')
  .directive('dynamicContent', ["$templateRequest", "$uibModal", "$sce", "$compile", "$timeout", function ($templateRequest, $uibModal, $sce, $compile, $timeout) {

    function loadTemplate(url) {
      var templateUrl = $sce.getTrustedResourceUrl(url);
      return $templateRequest(templateUrl);
    }

    /* directive definition */
    return {
      restrict: 'E',
      scope: {
        field: '=',
        workload: '='
      },
      link: function (scope, element, attrs) {
        var vm = scope;
        var $numberInput;
        var url = 'scripts/directives/dynamic-content/templates/' + attrs.type + '.html';
        loadTemplate(url).then(function (template) {
          var linkFn = $compile(template);
          var content = linkFn(scope);
          if (vm.field.type == "number") {
            $numberInput = content.find("input[type=number]");
          }
          if (vm.field.type == "dynamic-text") {
            var diskData = vm.field.diskModel !== 'compression_saved' ? 100.0 : vm.workload[vm.field.diskModel]
            if (vm.field.model !== 'combined_compr_dedup') {
              vm.workload[vm.field.model] = diskData - (diskData * (vm.workload[vm.field.factorModel] / 100));
              vm.field.dynamicMsg = ((vm.field.tooltip.replace('dynamicText', (isNaN(diskData) ? '--' : parseFloat(diskData).toFixed(1) + ' GB'))).replace('dynamicText1', (vm.workload[vm.field.factorModel] === null || vm.workload[vm.field.factorModel] === undefined) ? '--' : vm.workload[vm.field.factorModel])).replace('dynamicText2', (isNaN(vm.workload[vm.field.model]) ? '--' : parseFloat(vm.workload[vm.field.model]).toFixed(1) + ' GB'));
            } else {
              var x = ((diskData - vm.workload[vm.field.factorModel]) / diskData) * 100;
              vm.field.dynamicMsg = (isNaN(x) ? '--' : parseFloat(x).toFixed(1)) + '% (' + (isNaN(diskData / vm.workload[vm.field.factorModel]) ? '--' : parseFloat(diskData / vm.workload[vm.field.factorModel]).toFixed(2)) + ' : 1)';
              /* vm.field.dynamicText1 = x + "%";
              vm.field.dynamicText2 = parseFloat(diskData / vm.workload[vm.field.factorModel]).toFixed(2) + ' : 1'; */
            }
          }
          if (vm.field.className) {
            element.addClass(vm.field.className);
          }
          element.append(content);
          $timeout(function () {
            checkForNumericInputValidation();
          })

        }, function () {
          // An error has occurred
        });


        vm.tooltipMessage = getTooltipMessage(vm.field.tooltip, vm.workload[vm.field.modelName]);

        if ('RAW_FILE' === vm.workload.wl_type && 'vcpus_per_core' === vm.field.modelName) {
          vm.field.readonly = false;
          if (!vm.workload[vm.field.modelName]) {
            vm.workload[vm.field.modelName] = 1;
          }
        }

        function getTooltipMessage(tooltip, fieldValue) {
          if (!tooltip || !tooltip.message) return "";
          var tooltipData = tooltip.message;
          if (!tooltipData) return tooltipData;
          return (typeof tooltipData === "string") ? tooltipData : tooltipData[fieldValue];
        }

        vm.setModelVal = function (val) {
          var prevVal = vm.workload[vm.field.modelName];
          vm.workload[vm.field.modelName] = val;
          if (prevVal != val) {
            vm.onChange()
          }
        };

        vm.onFileUploaded = function (data) {
          if (vm.workload.wl_type === 'ORACLE') {
            checkForNumericInputValidation();
          }
        }

        // CUSTOM CODE
        // SHOULD HAVE BEEN HANDLED OUT SIDE THIS CONTROLLER
        vm.onFileInputClick = function (event) {
          var isFileInput = !vm.workload.isFileInput;
          if ((vm.workload.wl_type === "RAW" || vm.workload.wl_type === "RAW_FILE") && window._mpl_fileUploadData && !isFileInput) {
            event.stopPropagation();
            event.stopImmediatePropagation();

            $uibModal.open({
              templateUrl: 'scripts/directives/file-upload/cluster_confirm.html',
              backdrop: 'static',
              size: 'sm'
            }).result.then(function (result) {
              // on confirm
              vm.workload.isFileInput = !vm.workload.isFileInput;
              vm.onChange(event);
            }, function () {
              // dismissed
            });

          } else {
            vm.workload.isFileInput = !vm.workload.isFileInput;
            vm.onChange(event);
          }
        }

        vm.onClick = function () {
          if (vm.field.events && vm.field.events.click) {
            scope.$emit(vm.field.events.click, {
              prop: vm.field.modelName,
              type: vm.field.type
            });
          }
        };

        vm.onChange = function (event) {
          if (vm.field.events && vm.field.events.change) {
            scope.$emit(vm.field.events.change, {
              field: vm.field
            });
            vm.tooltipMessage = getTooltipMessage(vm.field.tooltip, vm.workload[vm.field.modelName]);
          }
          checkForNumericInputValidation();
        };

        vm.onBlur = function () {
          if (vm.field.events && vm.field.events.blur) {
            scope.$emit(vm.field.events.blur, {
              field: vm.field
            });
          }
        }

        vm.onSearchSelectionChanged = function (value) {
          vm.workload[vm.field.modelName] = value;
          vm.field.hasError = value === undefined || value === null || value === '';
          scope.$emit("WORKLOAD_FIELD_VALIDATION", {
            field: vm.field
          });
          vm.onChange();
        }

        vm.epicDCvalidation = function (column, row) {
          if (column.readonly) return;
          var min, max, val, workloadData;
          column.isInvalidDecimal = column.outOfRangeError = false;
          workloadData = vm.workload['datacentres'].filter(function (wlData) {
            return wlData.dc_name === row.name;
          })[0];
          val = workloadData[column.modelName];

          if (val === null || val === undefined || val === "") {
            column.outOfRangeError = true;
          } else {
            min = column.min;
            max = column.max;
            val = parseFloat(val);
            column.value = val;
            column.outOfRangeError = column.hasError = (val < min || val > max);
          }
          scope.$emit("WORKLOAD_FIELD_VALIDATION", {
            type: 'epic'
          });
        }

        vm.splunkValidation = function (column, row) {
          if (column.readonly) return;
          var min, max, val, workloadData;
          column.isInvalidDecimal = column.outOfRangeError = false;
          /* workloadData = vm.workload[row.value].filter(function (wlData) {
            return wlData.dc_name === row.name;
          })[0]; */
          val = vm.workload[row.value][column.modelName];

          if (val === null || val === undefined || val === "") {
            column.outOfRangeError = column.hasError = true;
          } else {
            min = column.min;
            max = column.max;
            val = parseFloat(val);
            column.value = val;
            column.outOfRangeError = column.hasError = (val < min || val > max);
          }
          scope.$emit("WORKLOAD_FIELD_VALIDATION", {
            field: vm.field
          });

        }

        function checkForNumericInputValidation() {
          /* if (vm.workload.wl_type === 'ORACLE' && vm.field.type === 'workload-input-type') {
            val1 = vm.workload['db_size'];
            val2 = vm.workload['metadata_size'];
            if (val1 === null || val1 === undefined || val1 === "" || val2 === null || val2 === undefined || val2 === "") {
              column.outOfRangeError = true;
            }
            scope.$emit("WORKLOAD_FIELD_VALIDATION", {
              field: vm.field
            });
          } */
          if (vm.field.type == "number") {
            checkForValidity();
            scope.$emit("WORKLOAD_FIELD_VALIDATION", {
              field: vm.field
            });
          }
        }

        function hasDecimalData(val) {
          return parseInt(val) != val;
        }

        function isInValidDecimal(val) {
          var reg = /^\d*.?\d$/;
          return !reg.test(val);
        }

        function checkForValidity() {
          if (vm.field.readonly) return;
          var min, max, val;
          vm.isInvalidDecimal = vm.outOfRangeError = false;
          val = $numberInput.get(0).value;// || vm.workload[vm.field.modelName];

          if (val === null || val === undefined || val === "") {
            vm.outOfRangeError = true;
          } else {
            min = vm.field.min;
            max = vm.field.max;
            val = parseFloat(val);
            vm.field.value = val;
            vm.outOfRangeError = vm.field.hasError = (val < min || val > max);
          }

          val = parseFloat(val);
          vm.isInvalidDecimal = (
            val &&
            (!vm.field.isDecimal && hasDecimalData(val)) ||
            (vm.field.isDecimal && isInValidDecimal(val))
          );

          vm.field.hasError = vm.outOfRangeError || vm.isInvalidDecimal;
        }

      } //link function

    };


  }]);
