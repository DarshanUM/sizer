(function () {
  'use strict';

  angular
    .module('hyperflex')
    .service('nodeService', ['appService', 'APP_ENV', 'REQUEST_TYPE', function (appService, APP_ENV, REQUEST_TYPE) {

      var fn = this;

      fn.getSizerVersion = function () {
        var config = {
          url: (APP_ENV.baseUrl + "/hyperconverged/version"),
          method: "GET"
        };
        return appService.processRequest(config);
      };

      fn.getCPUModels = function (progressBarId) {
        var config = {
          url: (APP_ENV.baseUrl + "/hyperconverged/cpumodels"),
          method: "GET",
          progressbar: { id: progressBarId || 'get-cpu-models' }
        };
        return appService.processRequest(config);
      };

      fn.resizeScenario = function (scenarioId, progressBarId) {
        var config = {
          url: (APP_ENV.baseUrl + "/hyperconverged/scenarios/" + scenarioId + "/resize"),
          method: "POST",
          /*headers: {
            "contentType": "application/json"
          },*/
          progressbar: { id: progressBarId || 'scenario-request-resize' }
        };
        return appService.processRequest(config);
      };

      fn.getNodesList = function () {
        var config = {
          url: (APP_ENV.baseUrl + "/hyperconverged/Node/nodelist/"),
          method: "GET",
          /*headers: {
            "contentType": "application/json"
          },*/
          progressbar: { id: 'nodelist-request-query' },
          requestId: REQUEST_TYPE.NODE_QUERY
        };
        return appService.processRequest(config);
      };

      fn.getTrainingsVideosList = function () {
        var config = {
          url: (APP_ENV.baseUrl + "/help/videos"),
          method: "GET",
          progressbar: { id: 'get-training-videos' }
        };
        return appService.processRequest(config);
      };

      fn.getFilterOptions = function () {
        var config = {
          url: (APP_ENV.baseUrl + "/hyperconverged/Node/filterlist/"),
          method: "GET"
        };
        return appService.processRequest(config);
      };

      fn.getFI_Options = function () {
        var config = {
          url: (APP_ENV.baseUrl + "/hyperconverged/Node/filist/"),
          method: "GET",
          progressbar: { id: 'fi_packages-get-request' }

        };
        return appService.processRequest(config);
      };

      fn.getProfilerInfo = function () {
        var config = {
          url: (APP_ENV.baseUrl + "/hyperconverged/profilerinfo"),
          method: "GET"
        };
        return appService.processRequest(config);
      };

      fn.getProfilerDownloadPath = function () {
        var config = {
          url: (APP_ENV.baseUrl + "/hyperconverged/downloadprofiler"),
          method: "POST",
          progressbar: { id: 'profiler-ova-download' }
        };
        return appService.processRequest(config);
      };

      fn.getHXBenchDownloadPath = function () {
        var config = {
          url: (APP_ENV.baseUrl + "/hyperconverged/downloadbench"),
          method: "POST",
          progressbar: { id: 'hxbench-ova-download' }
        };
        return appService.processRequest(config);
      };

      fn.cloneScenario = function (scenarioId, scenarioData) {
        var config = {
          url: (APP_ENV.baseUrl + "/hyperconverged/scenarios/" + scenarioId + "/clone"),
          method: "POST",
          data: scenarioData,
          progressbar: { id: 'clone-scenario-request-query' },
          requestId: REQUEST_TYPE.SCENARIO_CLONE
        };
        return appService.processRequest(config);
      };

      fn.getUserData = function () {
        var config = {
          url: (APP_ENV.baseUrl + "/userdata"),
          method: "GET",
          progressbar: { id: 'userdata-request-query' },
          requestId: REQUEST_TYPE.USERDATA
        };
        return appService.processRequest(config);
      }

      fn.userDataPost = function (req) {
        var config = {
          url: (APP_ENV.baseUrl + "/userdata"),
          method: "POST",
          data: req,
          progressbar: { id: 'userdata-request-query' },
          requestId: REQUEST_TYPE.USERDATA
        };
        return appService.processRequest(config);
      }

      fn.getScenarioById = function (id) {
        var config = {
          url: (APP_ENV.baseUrl + "/hyperconverged/scenario?id=" + id),
          method: "GET",
          progressbar: { id: 'scenario-request-query' },
          requestId: REQUEST_TYPE.SCENARIO_GET
        };
        return appService.processRequest(config);
      }

      fn.bulkDelete = function (scenarioList) {
        var config = {
          url: (APP_ENV.baseUrl + "/hyperconverged/scenarios"),
          method: "DELETE",
          data: scenarioList,
          progressbar: { id: 'clone-scenario-request-query' },
          requestId: REQUEST_TYPE.SCENARIO_CLONE
        };
        return appService.processRequest(config);
      };

      fn.autoArchive = function (payload) {
        var config = {
          url: (APP_ENV.baseUrl + "/hyperconverged/scenarios/autoarchive"),
          method: "PATCH",
          data: payload,
          progressbar: { id: 'clone-scenario-request-query' },
          requestId: REQUEST_TYPE.SCENARIO_CLONE
        };
        return appService.processRequest(config);
      }

      fn.saveResults = function (scenarioId, scenarioResults) {
        var config = {
          url: (APP_ENV.baseUrl + "/hyperconverged/results/result_detail/" + scenarioId),
          method: "PUT",
          data: scenarioResults,
          progressbar: { id: 'save-results-request' }
        };
        return appService.processRequest(config);
      };

      fn.sendFeedback = function (data) {
        var config = {
          url: (APP_ENV.baseUrl + "/email"),
          method: "POST",
          data: data,
          progressbar: { id: 'feedback-submit-request' }
        };
        return appService.processRequest(config);
      };

      fn.downloadScenarioReport = function (scenarioId, resultName, fiPackagesCount, fiPackageName, language, slides) {

        var reqData = {
          type: "PPT",
          download: "True",
          email: "False",
          nodetype: resultName,
          fipackage_count: fiPackagesCount,
          fipackage_name: fiPackageName,
          language: language,
          slides: slides
        }

        var config = {
          url: (APP_ENV.baseUrl + "/hyperconverged/scenarios/" + scenarioId + "/report"),
          method: "POST",
          data: reqData,
          progressbar: { id: 'scenario-report-download' }
        };
        return appService.processRequest(config);
      };

      fn.downloadFixedConfigScenarioReport = function (reqData) {
        var config = {
          url: (APP_ENV.baseUrl + "/hyperconverged/fixed_config_report"),
          method: "POST",
          data: reqData,
          progressbar: { id: 'fixed-config-sizing-scenario-report-download' }
        };
        return appService.processRequest(config);
      };

      fn.downloadBOM = function (scenarioId, resultName, fiPackagesCount, fiPackageName) {

        var reqData = {
          type: "XLSX",
          download: "True",
          email: "False",
          nodetype: resultName,
          fipackage_count: fiPackagesCount,
          fipackage_name: fiPackageName
        }

        var config = {
          url: (APP_ENV.baseUrl + "/hyperconverged/scenarios/" + scenarioId + "/bom"),
          method: "POST",
          data: reqData,
          progressbar: { id: 'scenario-report-download' }
        };
        return appService.processRequest(config);
      };


    }])

})();
