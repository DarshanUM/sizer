/* window._$clonedFile is using to decide whether to ignore the file selection on edit workload request */;

angular.module('hyperflex')
    .directive('fileUploadOracle', ['$parse', "$http", "$stateParams", "$timeout", "APP_ENV", function ($parse, $http, $stateParams, $timeout, APP_ENV) {

        function isSupportedFileFormat(fileName, supportedFilesFormat) {
            var format = null;
            var fname = fileName.toLowerCase();
            var fileExt = fname.substr(fname.lastIndexOf("."));
            return (supportedFilesFormat.indexOf(fileExt) !== -1)
        }

        /* directive definition */
        return {
            restrict: 'EA',
            templateUrl: "scripts/directives/file-upload-oracle/file-upload-oracle.html",
            scope: {
                onUploadSuccess: "&",
                onUploadError: "&",
            },
            link: function (scope, element, attrs) {
                var vm = scope;
                vm.selectedFile = null;
                vm.isFileSelected = false;
                vm.isFileHasPrasingError = true;
                vm.isFileHasPrased = false;
                vm.disableUPpload = true;
                vm.isInvalidFileFormat = false;
                vm.isBeyondMaxSize = false;
                vm.fileOptions = [
                    {
                        key: "txt",
                        value: "Oracle Database Input"
                    }
                ]

                if (window._$clonedFile) {
                    vm.isFileSelected = true;
                    vm.isFileHasPrasingError = false;
                    vm.isFileHasPrased = true;
                }

                vm.onFileSelectionChanged = function (fileElem) {
                    vm.disableUPpload = false;
                    vm.isFileHasPrasingError = false;
                    vm.isFileHasPrased = false;
                    vm.isInvalidFileFormat = false;
                    vm.isBeyondMaxSize = false;
                    vm.isFileSelected = fileElem.value && fileElem.value.length;// !(!fileElem.value)

                    if (!vm.isFileSelected) {
                        return scope.$apply();
                    } else {
                        vm.selectedFile = fileElem.files[0];
                    }
                    vm.selectedFile = fileElem.files[0];
                    window._$clonedFile = element.find("input")[0].cloneNode();
                    vm.uploadFile()
                    scope.$apply();

                    var fileType = "Oracle Database Input";


                    scope.$emit("FILE_SELECTION_CHANGED", {
                        data: { input_type: fileType }
                    });
                }

                vm.uploadFile = function () {
                    var fd = new FormData();
                    fd.append('file', vm.selectedFile);

                    var config = {
                        url: (APP_ENV.baseUrl + "/hyperconverged/processesxstat"),
                        method: "POST",
                        data: fd,
                        transformRequest: angular.identity,
                        headers: { 'Content-Type': undefined },
                        progressbar: { id: 'file-upload-request' }
                    };

                    $http(config).success(function (response) {
                        processResponse(response);
                    }).error(function (response) {
                        vm.disableUPpload = false;
                        vm.isFileHasPrasingError = true;
                        vm.isFileHasPrased = true;
                        scope.$emit("FORM_UPLOAD_ERROR", {
                            data: response
                        });
                    });
                }

                function processResponse(response) {
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
                        scope.$emit("FORM_UPLOAD_SUCCESS", {
                            data: response.data,
                            hasWarning: true
                        });
                        $timeout(function () {
                            vm.onUploadSuccess(response.data);
                        }, 500);
                    } else if (response.status === "success") {
                        vm.isFileHasPrasingError = false;
                        scope.$emit("FORM_UPLOAD_SUCCESS", {
                            data: response.data
                        });
                        $timeout(function () {
                            vm.onUploadSuccess(response.data);
                        }, 500);
                    }
                }
            } //link function
        };


    }]);