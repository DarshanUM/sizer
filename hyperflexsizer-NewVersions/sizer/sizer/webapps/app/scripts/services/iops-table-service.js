(function () {
    'use strict';

    angular
        .module('hyperflex')
        .service('IopsTableService', ['appService', 'APP_ENV', 'REQUEST_TYPE', function (appService, APP_ENV, REQUEST_TYPE) {

            var fn = this;

            fn.getIopsData = function (progressBarId) {
                var config = {
                    url: APP_ENV.baseUrl + "/hyperconverged/hxperfnumbers",
                    method: "GET",
                    progressbar: { id: progressBarId || 'iops-table-request' }
                };
                return appService.processRequest(config);
            }

        }])

})();
