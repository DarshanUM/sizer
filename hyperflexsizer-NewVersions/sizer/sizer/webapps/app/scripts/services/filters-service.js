(function () {
  'use strict';

  angular
    .module('hyperflex')
    .service('filtersService', ['$q', 'appService', 'utilService', 'APP_ENV', 'REQUEST_TYPE', function ($q, appService, utilService, APP_ENV, REQUEST_TYPE) {

      var fn = this;
      var _filtersData = {};

      // fetch data from API
      fn.getFilterOptions = function () {
        var deferred = $q.defer();
        var config = {
          url: (APP_ENV.baseUrl + "/hyperconverged/Node/filterlist/"),
          method: "GET",
          progressbar: { id: 'filters-get-request' }
        };
        appService.processRequest(config).then(function (data) {
          _filtersData = data;
          deferred.resolve();
        }, function (error) {
          deferred.reject(error);
        });
        return deferred.promise;
      };

      fn.getFilters = function (settings, resultName, clockSpeed) {
        var includesList = [];
        var filtersData = utilService.getClone(_filtersData);
        // result name
        if (resultName === 'All-Flash') {
          includesList.push('all-flash');
        } else if (resultName === 'All NVMe') {
          includesList.push('all-nvme');
        } else { // lowest cost
          includesList.push('hybrid');
        }

        // hardware acceleration
        if (settings.hercules_conf === 'forced') {
          includesList.push('hercules_avail');
        }

        // hyperflex boost
        if (settings.hx_boost_conf === 'forced') {
          includesList.push('hx_boost_avail');
        }

        // sizing option
        if (settings.bundle_only === 'bundle') {
          includesList.push('bundle');
        } else if (settings.bundle_only === 'cto') {
          includesList.push('cto');
        } else {
          // for bundle & cto
          // can be either 'bundle' or 'cto'
        }

        // server type
        switch (settings.server_type) {
          case 'M4':
            includesList.push('M4_server'); break;
          case 'M5':
            includesList.push('M5_server'); break;
          default: // ALL
          // can be either 'M4_server' or 'M5_server'
          // not required to search for specific as it can be of any server type
        }
        switch (settings.cpu_generation) {
          case 'sky':
            includesList.push('sky'); break;
          case 'cascade':
            includesList.push('cascade'); break;
          case 'recommended':
            includesList.push('recommended'); break;

        }
        // disk options
        switch (settings.disk_option) {
          case 'SED':
            includesList.push('sed'); break;
          /* case 'NVMe':
            includesList.push('nvme'); break;
          case 'COLDSTREAM':
            includesList.push('coldstream'); break; */
          case 'LFF':
            includesList.push('lff'); break;
          case 'FIPS':
            includesList.push('fips'); break;
        }

        // disk options
        switch (settings.cache_option) {
          case 'SED':
            includesList.push('ssd-sed'); break;
          case 'NVMe':
            includesList.push('nvme'); break;
          case 'Optane':
            includesList.push('coldstream'); break;
        }

        // modular lan
        if (settings.modular_lan === '40G_VIC') {
          includesList.push('40g_vic');
        }

        // hypervisor
        includesList.push(settings.hypervisor);

        // Clock Speed filters to be applied for cpu options
        if (clockSpeed && clockSpeed.length) {
          filtersData.CPU_Type = utilService.filteredList(filtersData.CPU_Type, function (cpuTypeOption) {
            return clockSpeed.indexOf(cpuTypeOption.clock_speed) !== -1;
          });
        }
        var filters = getFiltersObject(filtersData, includesList);
        return filters;
      };

      function getFiltersObject(srcData, includesList) {
        return Object.keys(srcData).reduce(function (result, dataCategory) {
          result[dataCategory] = getFilters(srcData[dataCategory], includesList);
          return result;
        }, {});
      }

      function getFilters(dataList, includesList) {
        return utilService.filteredList(dataList, function (dataItem) {
          return utilService.hasAllItemsInList(dataItem.tags, includesList)
        }).map(function (dataItem) {
          return dataItem.name;
        });
      }

    }]);

})();
