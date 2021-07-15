angular.module('hyperflex')
  .directive('intraTypeContent', ["$templateRequest", "$uibModal", "$sce", "$compile", "$timeout", function ($templateRequest, $uibModal, $sce, $compile, $timeout) {

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
        vm.selectedItem = vm.workload.infra_type;
        var url = 'scripts/directives/dynamic-content/vdi-infra/' + attrs.type + '.html';
        loadTemplate(url).then(function (template) {
          var linkFn = $compile(template);
          var content = linkFn(scope);
          element.append(content);
          vm.selected();
          vm.countCheck();
          $timeout(function () {
            checkForNumericInputValidation();
          })
        }, function () {
        });

        vm.onChange = function (event, row) {
          vm.countCheck();
          checkForNumericInputValidation(event, row);
        };

        vm.countCheck = function(){
          vm.countFlag = false;
          angular.forEach(vm.workload[vm.selectedItem], function (value, key) {
            if (value['num_vms'] === 0) {
              vm.countFlag = true;
            }
          })
        }

        vm.selected = function () {
          vm.workload['infra_type'] = vm.selectedItem;
          scope.$emit("WORKLOAD_FIELD_CHANGED", {
            type: 'vdi_infra',
            field: vm.field.fields[vm.selectedItem]
          });
        }


        function checkForNumericInputValidation(column, row) {
          if (column) {
            if (column.type == "number") {
              checkForValidity(column, row);
              scope.$emit("WORKLOAD_FIELD_VALIDATION", {
                type: 'vdi_infra',
                item: vm.selectedItem
              });
            }
          }
        }

        function hasDecimalData(val) {
          return parseInt(val) != val;
        }

        function isInValidDecimal(val) {
          var reg = /^\d*.?\d$/;
          return !reg.test(val);
        }

        function checkForValidity(column, row) {
          if (column.readonly) return;
          var min, max, val;
          column.isInvalidDecimal = column.outOfRangeError = false;
          val = vm.workload[vm.selectedItem][row.value][column.modelName];

          if (val === null || val === undefined || val === "") {
            column.outOfRangeError = column.hasError = true;
          } else {
            min = column.min;
            max = column.max;
            val = parseFloat(val);
            column.value = val;
            column.outOfRangeError = column.hasError = (val < min || val > max);
          }

          /* val = parseFloat(val);
          vm.isInvalidDecimal = (
            val &&
            (!column.isDecimal && hasDecimalData(val)) ||
            (column.isDecimal && isInValidDecimal(val))
          );

          column.hasError = column.outOfRangeError || column.isInvalidDecimal; */
        }

      } //link function

    };


  }]);
