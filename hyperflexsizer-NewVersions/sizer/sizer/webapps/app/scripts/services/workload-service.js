(function () {
  'use strict';

  angular
    .module('hyperflex')
    .service('workloadService', ['$q', 'appService', 'APP_ENV', 'REQUEST_TYPE', function ($q, appService, APP_ENV, REQUEST_TYPE) {

      var fn = this;
      fn.fields = {};

      (function () {
        var promise1 = getWorkloadFields("default_values");
        var promise2 = getWorkloadFields("vdi");
        var promise3 = getWorkloadFields("vdi_infra");
        var promise4 = getWorkloadFields("vsi");
        var promise5 = getWorkloadFields("raw");
        var promise6 = getWorkloadFields("db");
        var promise7 = getWorkloadFields("robo");
        var promise8 = getWorkloadFields("oracle");
        var promise9 = getWorkloadFields("exchange");
        var promise10 = getWorkloadFields("epic_hyperspace");
        var promise11 = getWorkloadFields("splunk");
        var promise12 = getWorkloadFields("veeam");
        var promise13 = getWorkloadFields("bulk");
        var promise14 = getWorkloadFields('rdsh');
        var promise15 = getWorkloadFields('container');
        var promise16 = getWorkloadFields("raw_file");
        var promise17 = getWorkloadFields("aiml");
        var promise18 = getWorkloadFields("awr-file");

        promise1.then(function (data) {
          fn.defaultValues = data;
        }, function () {
          alert("Unable to load workload defautl values");
        });

        promise2.then(function (data) {
          fn.fields["VDI"] = data;
        }, function () {
          alert("Unable to load VDI workload form fields");
        });

        promise3.then(function (data) {
          fn.fields["VDI_INFRA"] = data;
        }, function () {
          alert("Unable to load VDI infra workload form fields");
        });

        promise4.then(function (data) {
          fn.fields["VSI"] = data;
        }, function () {
          alert("Unable to load VSI workload form fields");
        });

        promise5.then(function (data) {
          fn.fields["RAW"] = data;
        }, function () {
          alert("Unable to load RAW workload form fields");
        });

        promise6.then(function (data) {
          fn.fields["DB"] = data;
        }, function () {
          alert("Unable to load DB workload form fields");
        });

        promise7.then(function (data) {
          fn.fields["ROBO"] = data;
        }, function () {
          alert("Unable to load ROBO workload form fields");
        });

        promise8.then(function (data) {
          fn.fields["ORACLE"] = data;
        }, function () {
          alert("Unable to load Oracle workload form fields");
        });

        promise9.then(function (data) {
          fn.fields["EXCHANGE"] = data;
        }, function () {
          alert("Unable to load Exchange workload form fields");
        });

        promise10.then(function (data) {
          fn.fields["EPIC"] = data;
        }, function () {
          alert("Unable to load Epic Hyperspace form fields");
        });

        promise11.then(function (data) {
          fn.fields["SPLUNK"] = data;
        }, function () {
          alert("Unable to load Splunk Workload form fields");
        });

        promise12.then(function (data) {
          fn.fields["VEEAM"] = data;
        }, function () {
          alert("Unable to load veeam Workload form fields");
        });

        promise13.then(function (data) {
          fn.fields["BULK"] = data;
        }, function () {
          alert("Unable to load BULK Workload form fields");
        });

        promise14.then(function (data) {
          fn.fields["RDSH"] = data;
        }, function () {
          alert("Unable to load RDSH Workload form fields");
        });

        promise15.then(function (data) {
          fn.fields["CONTAINER"] = data;
        }, function () {
          alert("Unable to load CONTAINER Workload form fields");
        });

        promise16.then(function (data) {
          fn.fields["RAW_FILE"] = data;
        }, function () {
          alert("Unable to load FILE Workload form fields");
        });

        promise17.then(function (data) {
          fn.fields["AIML"] = data;
        }, function () {
          alert("Unable to load AIML Workload form fields");
        });

        promise18.then(function (data) {
          fn.fields["AWR_FILE"] = data;
        }, function () {
          alert("Unable to load AWR Workload form fields");
        });

        // $q.all([promise1, promise2, promise3, promise4, promise5, promise6, promise7, promise8, promise9]).then(function(){
        //   console.log("all files loaded");
        //   console.log( fn.fields );
        // });

      }());

      function getWorkloadFields(workloadFileName) {
        var config = {
          url: ("." + "/" + APP_ENV.workload_url[workloadFileName]),
          method: "GET"
        };
        return appService.processRequest(config);
      };

    }]); //service

})();
