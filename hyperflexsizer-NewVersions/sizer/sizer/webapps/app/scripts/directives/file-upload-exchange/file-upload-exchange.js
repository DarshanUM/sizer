/* window._$clonedFile is using to decide whether to ignore the file selection on edit workload request */;

angular.module('hyperflex')
  .directive('fileUploadExchange', ['$parse', "$http", "$timeout", "APP_ENV" , function ($parse, $http, $timeout, APP_ENV) {

    function isSupportedFileFormat(fileName, supportedFilesFormat){
      var format = null;
      var fname = fileName.toLowerCase();
      var fileExt = fname.substr( fname.lastIndexOf(".") );
      return ( supportedFilesFormat.indexOf(fileExt) !== -1 )
    }

    /* directive definition */
    return {
      restrict: 'EA',
      templateUrl: "scripts/directives/file-upload-exchange/file-upload-exchange.html",
      scope: {
        onUploadSuccess: "&",
        onUploadError: "&"
      },
      link: function(scope, element, attrs) {
        var vm = scope;
        vm.filetypeInput = "xlsm";
        vm.tooltip = "Supported XLSM formats: Exchange workload files generated by HX Workload Profiler";
        vm.fileAccept = ".xlsm";
        vm.maxFileSize = 1024 * 1024 * 5;//units will be in bytes (5 MB)
        vm.supportedFilesFormat = [".xlsm"];
        vm.selectedFile = null;
        vm.isFileSelected = false;
        vm.isFileHasPrasingError = true;
        vm.isFileHasPrased = false;
        vm.disableUPpload = true;
        vm.isInvalidFileFormat = false;
        vm.isBeyondMaxSize = false;
        vm.fileOptions = [
          {
            key: "xlsm",
            value: "Exchange Workload"
          }
        ]

        if(window._$clonedFile){
          // vm.disableUPpload = false;
          vm.isFileSelected = true;
          vm.isFileHasPrasingError = false;
          vm.isFileHasPrased = true;
          // element.find("input")[0].replaceWith( window._$clonedFile )
        }

        vm.onFileSelectionChanged = function(fileElem){
          vm.disableUPpload = false;
          vm.isFileHasPrasingError = false;
          vm.isFileHasPrased = false;
          vm.isInvalidFileFormat = false;
          vm.isBeyondMaxSize = false;
          vm.isFileSelected =  fileElem.value && fileElem.value.length;// !(!fileElem.value)

          if(!vm.isFileSelected){
            return scope.$apply();
          }else{
            vm.selectedFile = fileElem.files[0];
            if( !isSupportedFileFormat(vm.selectedFile.name, vm.supportedFilesFormat) ){
              vm.isInvalidFileFormat = true;
              scope.$emit( "FORM_UPLOAD_ERROR", {
                data: {}
              });
              return scope.$apply();
            }else if( vm.selectedFile.size > vm.maxFileSize ){
              vm.isBeyondMaxSize = true;
              scope.$emit( "FORM_UPLOAD_ERROR", {
                data: {}
              });
              return scope.$apply();
            }

          }
          vm.selectedFile = fileElem.files[0];
          window._$clonedFile = element.find("input")[0].cloneNode();
          vm.uploadFile()
          scope.$apply();

          var fileType = "Exchange Workload";


          scope.$emit( "FILE_SELECTION_CHANGED", {
            data: { input_type: fileType }
          });
        }

        vm.onClick = function(e){
          /*this is to clear the values on click & force the user to select the file with browse dialog box*/
          // $timeout(function(){
          //   e.target.value = "";
          //   $(e.target).trigger("change");
          // })
        };

        vm.uploadFile = function(){
          var fd = new FormData();
          fd.append('file', vm.selectedFile);

          var config = {
            url: (APP_ENV.baseUrl + "/hyperconverged/processesxstat"),
            method: "POST",
            data: fd,
            transformRequest: angular.identity,
            headers: {'Content-Type': undefined},
            progressbar: {id:'file-upload-request'}
          };     

          $http(config).success(function(response) {
            // if( typeof vm.onUploadSuccess === "function"){
              // scope.onUploadSuccess( {data: response});              
            // }
            processResponse(response);
          }).error(function(response) {
            // if( typeof vm.onUploadError === "function"){
            //   scope.onUploadError( {data: response});
            // }
            vm.disableUPpload = false;
            vm.isFileHasPrasingError = true;
            vm.isFileHasPrased = true;
            scope.$emit( "FORM_UPLOAD_ERROR", {
              data: response
            });
          });
        }

        vm.tooltipData = [
          "Error: No benchmark data for CPU: Intel E5-2650 in line 2 ",
          "Error: No benchmark data for CPU: Intel E5-2650 V4 in line 5 "
        ];

        function processResponse(response){
          vm.hasError = false;
          vm.hasWarning = false;            
          vm.disableUPpload = false;
          vm.isFileHasPrasingError = false;
          vm.isFileHasPrased = true;

          if(response.status === "error"){            
            vm.isFileHasPrasingError = true;
            vm.hasError = true;
            vm.tooltipData = response.Msg || []
            scope.$emit( "FORM_UPLOAD_ERROR", {
              data: response
            });
          }else if(response.status === "warning"){
            vm.hasWarning = true;
            vm.tooltipData = response.Msg || []          
            vm.isFileHasPrasingError = true;
            scope.$emit( "FORM_UPLOAD_SUCCESS", {
              data: response.data,
              hasWarning: true
            });
          }else if(response.status === "success"){
            vm.isFileHasPrasingError = false;
            scope.$emit( "FORM_UPLOAD_SUCCESS", {
              data: response.data
            });
          }


        }


      } //link function
    };


  }]);