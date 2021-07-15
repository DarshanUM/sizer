angular.module('hyperflex')
  .directive('mplPagination', [ 'utilService', function(utilService) {

    var defaultConfig = {
      itemsPerPage: 0,
      currentPage: 1,
      totalPages: 0,
      totalItems: 0,
      labels: {
        first: "First",
        last: "Last",
        next: "Next",
        previous: "Previous"
      }
    };

  	/* directive definition */
    return {
      restrict: 'E',
      templateUrl: "scripts/directives/pagination/pagination.html",
      scope: {
      	config: "=",
        onChange: "&"
      },
      link: function(scope, element, attrs) {
    
        var vm = scope;
        vm.currentPage = 1;

        function init() {
          vm.config = vm.config || {};
          Object.keys(defaultConfig).forEach(function(key) {
            vm.config[key] = vm.config[key] || defaultConfig[key];
          })
          // var config = angular.extend({}, defaultConfig, vm.config);

          vm.config.totalPages = Math.ceil( vm.config.totalItems / vm.config.itemsPerPage );
          if (vm.config.currentPage > vm.config.totalPages) {
            vm.config.currentPage = vm.config.totalPages;
          }
          vm.currentPage = vm.config.currentPage;
          vm.setPage(vm.config.currentPage);
        }

        vm.setPage = function(pageNum) {
          vm.currentPage = pageNum;
          vm.config.currentPage = vm.currentPage;
          if (typeof vm.onChange === "function") {
            scope.onChange();
          }
        };

        vm.onPageChanged = function(event) {
          // console.log('event ', event);
          var keyCode = event.keyCode || event.which;
          if (keyCode > 48 && keyCode < 58) {
            // accept numeric input
          } else if (keyCode === 8){//backspace

          } else if (keyCode === 13){//enter
            var pageNum = parseInt(vm.currentPage);
            if(pageNum > vm.config.totalPages ) {
              vm.currentPage = vm.config.totalPages;
            }
            if (vm.currentPage != vm.config.currentPage) {
              vm.setPage( vm.currentPage );
            }
          } else {
            event.preventDefault();
            return false;
          }

        };

        scope.$watch( 'config', function(newVal, oldVal){
          init(newVal);
        });
        
      } //link function

    };

  }]);
