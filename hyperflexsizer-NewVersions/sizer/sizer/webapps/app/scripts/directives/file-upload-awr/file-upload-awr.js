/* window._$clonedFile is using to decide whether to ignore the file selection on edit workload request */;
/* window._mpl_fileUploadData is using to decide whether to ignore the file selection on edit workload request */;

angular.module('hyperflex')
  .directive('fileUploadAwr', ['$parse', "$http", "$sce", "$timeout", "APP_ENV", '$uibModal', function ($parse, $http, $sce, $timeout, APP_ENV, $uibModal) {

    function isSupportedFileFormat(fileName, supportedFilesFormat) {
      var format = null;
      var fname = fileName.toLowerCase();
      var fileExt = fname.substr(fname.lastIndexOf("."));
      return (supportedFilesFormat.indexOf(fileExt) !== -1)
    }

    /* directive definition */
    return {
      restrict: 'EA',
      templateUrl: "scripts/directives/file-upload-awr/file-upload-awr.html",
      scope: {
        onUploadSuccess: "&",
        onUploadError: "&",
        isProvisioned: "="
      },
      link: function (scope, element, attrs) {
        var vm = scope;
        vm.filetypeInput = "txt";
        vm.txtFileAccept = ".txt";
        vm.htmlFileAccept = ".html";
        vm.supportedFilesFormat = [".txt", ".html"];
        vm.selectedFile = null;
        vm.isFileSelected = false;
        vm.isFileHasPrasingError = true;
        vm.isFileHasPrased = false;
        vm.disableUPpload = true;
        vm.isInvalidFileFormat = false;
        vm.isBeyondMaxSize = false;
        vm.data = { 'isProvisioned': (vm.isProvisioned || false) }
        vm.fileUploadResponse;

        vm.tooltipContent = $sce.trustAsHtml("'Provisioned' will size for the provisioned CPU/Memory/Disk capacity of Hosts & VMs. <br> ‘Utilized’ will size for the actual utilized CPU/Memory/Disk capacity of Hosts & VMs; Utilized will usually be less than provisioned");

        vm.onInputFileTypeChanged = function () {
          if (vm.fileUploadResponse) {
            vm.confirmDialog().result.then(function (result) {
              vm.isFileSelected = false;
              vm.hasError = false;
              vm.hasWarning = false;
              vm.onClusterSelectionChanged({});
              vm.fileUploadResponse = null;
              clearFileData();
              $('#file_input').val(null);
            }, function () {

            });;
          }

        };

        vm.onFileSelectionChanged = function (fileElem) {
          vm.disableUPpload = false;
          vm.isFileHasPrasingError = false;
          vm.isFileHasPrased = false;
          vm.isInvalidFileFormat = false;
          vm.isBeyondMaxSize = false;
          vm.isFileSelected = fileElem.value && fileElem.value.length;// !(!fileElem.value)
          vm.hasError = false;
          vm.hasWarning = false;

          if (!vm.isFileSelected) {
            return scope.$apply();
          } else {
            vm.selectedFile = fileElem.files[0];
            if (!isSupportedFileFormat(vm.selectedFile.name, vm.supportedFilesFormat)) {
              vm.isInvalidFileFormat = true;
              scope.$emit("FORM_UPLOAD_ERROR", {
                data: {}
              });
              return scope.$apply();
            }  /* else if ((vm.filetypeInput == "csv" && vm.selectedFile.size > vm.maxCSVFileSize) ||
              (vm.filetypeInput == "xls" && vm.selectedFile.size > vm.maxXLSFileSize)
            ) {
              vm.isBeyondMaxSize = true;
              scope.$emit("FORM_UPLOAD_ERROR", {
                data: {}
              });
              return scope.$apply();
            } */

          }
          vm.selectedFile = fileElem.files[0];
          window._$clonedFile = element.find("input")[0].cloneNode();
          vm.uploadFile()
          scope.$apply();


          scope.$emit("FILE_SELECTION_CHANGED", {
            data: { input_type: "txt" }
          });
        }

        vm.onClick = function (e) {
        };


        vm.confirmDialog = function () {
          return $uibModal.open({
            templateUrl: 'scripts/directives/file-upload/cluster_confirm.html',
            backdrop: 'static',
            size: 'sm',
            controller: 'WorkloadController',
            resolve: {
            }
          })
        }



        vm.onBasisSizingChanged = function () {
          if (vm.fileUploadResponse) {
            processResponse(vm.fileUploadResponse);
          }
        };

        vm.uploadFile = function () {
          var fd = new FormData();
          fd.append('file', vm.selectedFile);
          var URL = APP_ENV.baseUrl + "/hyperconverged/processesxstat";
          var config = {
            url: URL,
            method: "POST",
            data: fd,
            transformRequest: angular.identity,
            headers: { 'Content-Type': undefined },
            progressbar: { id: 'file-upload-request' }
          };

          $http(config).success(function (response) {
            saveFileData(response);
            vm.fileUploadResponse = response;
            processResponse(response);
            scope.$broadcast('SCENARIO_UPDATED');
          }).error(function (response) {
            clearFileData();
            vm.disableUPpload = false;
            vm.isFileHasPrasingError = true;
            vm.isFileHasPrased = true;

            scope.$emit("FORM_UPLOAD_ERROR", {
              data: response
            });
          });
        }

        vm.tooltipData = [
          "Error: No benchmark data for CPU: Intel E5-2650 in line 2 ",
          "Error: No benchmark data for CPU: Intel E5-2650 V4 in line 5 "
        ];

        /* function getClusterAggregate(clusterData) {
          return Object.keys(clusterData).reduce(function (hostData, hostName) {
            if (hostData.provisioned) {
              Object.keys(hostData.provisioned).forEach(function (propName) {
                hostData.provisioned[propName] += clusterData[hostName].provisioned[propName];
                hostData.utilized[propName] += clusterData[hostName].utilized[propName];
              })
              return hostData;
            } else {
              return clusterData[hostName];
            }
          }, {});
        } */

        /* function limitToFixedDecimal(data) {
          Object.keys(data).forEach(function (propName) {
            data[propName] = data[propName].toFixed(1);
          })
        } */

        function getDataForSelectedClusters(response) {
          var result;

          var aggregateResult = JSON.parse(JSON.stringify(response.data));

          ['provisioned', 'utilized'].forEach(function (propName) {
            // limitToFixedDecimal(aggregateResult[propName]);

            if (aggregateResult[propName].ram_per_db > 1024) {
              aggregateResult[propName].ram_per_db = (aggregateResult[propName].ram_per_db / 1024).toFixed(1);
              aggregateResult[propName].ram_per_db_unit = 'TiB'
            } else {
              aggregateResult[propName].ram_per_db_unit = 'GiB'
            }
            aggregateResult[propName].vcpus_per_core = 1;

          });
          result = aggregateResult;

          saveFileData(response);

          return result;
        }

        function saveFileData(response) {
          window._mpl_fileUploadData = {
            selectedFile: vm.selectedFile,
            response: response,
          };
        }

        function clearFileData() {
          window._mpl_fileUploadData = null;
        }

        function processResponse(response, selectedOptions) {
          vm.hasError = false;
          vm.hasWarning = false;
          vm.disableUPpload = false;
          vm.isFileHasPrasingError = false;
          vm.isFileHasPrased = true;

          if (response.status === "error") {
            vm.isFileHasPrasingError = true;
            vm.hasError = true;
            vm.tooltipData = response.Msg || []
            scope.$emit("FORM_UPLOAD_ERROR", {
              data: response
            });
          } else if (response.status === "warning") {
            vm.hasWarning = true;
            vm.tooltipData = response.Msg || []
            vm.isFileHasPrasingError = true;

            var aggregateData = getDataForSelectedClusters(vm.fileUploadResponse);
            scope.$emit("FORM_UPLOAD_SUCCESS", {
              data: aggregateData,
              hasWarning: true,
              isProvisioned: vm.data.isProvisioned
            });
          } else if (response.status === "success") {
            var aggregateData = getDataForSelectedClusters(vm.fileUploadResponse);
            vm.isFileHasPrasingError = false;
            scope.$emit("FORM_UPLOAD_SUCCESS", {
              data: aggregateData,
              isProvisioned: vm.data.isProvisioned
            });
          }


        }


        // initialize the data if file data exists
        if (window._mpl_fileUploadData) {
          vm.isFileSelected = true;
          vm.isFileHasPrasingError = false;
          vm.isFileHasPrased = true;

          vm.fileUploadResponse = window._mpl_fileUploadData.response;
          vm.onClusterSelectionChanged({ selectedOptions: window._mpl_fileUploadData.selectedClusters });
        }


      } //link function
    };


  }]);
