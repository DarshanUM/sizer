(function() {
  'use strict';

  angular
    .module('hyperflex')
    .service('shareScenarioService', ['appService', 'APP_ENV', 'REQUEST_TYPE', function(appService, APP_ENV, REQUEST_TYPE) {

      var fn = this;

      fn.getUsers = function() {
        var config = {
          url: (APP_ENV.baseUrl + "/hyperconverged/users"),
          method: "GET",
          progressbar: {id:"get-users-request"}
        };
        return appService.processRequest(config);
      };

      fn.getSharedUsers = function(scenarioId){
        var config = {
          url: (APP_ENV.baseUrl + "/hyperconverged/scenarios/"+ scenarioId +"/shares"),
          method: "GET",
          progressbar: {id:'shared-users-list'}
        };
        return appService.processRequest(config);
      }

      fn.save = function(scenarioId, userslist, progressBarId) {
        var config = {
          url: (APP_ENV.baseUrl + "/hyperconverged/scenarios/"+ scenarioId +"/shares"),
          method: "POST",
          data: userslist,
          /*headers: {
            "contentType": "application/json"
          },*/
          progressbar: {id:progressBarId || 'share-scenario-request'}
        };
        return appService.processRequest(config);
      };

      fn.getNodesList = function() {
        var config = {
          url: (APP_ENV.baseUrl + "/hyperconverged/Node/nodelist/"),
          method: "GET",
          /*headers: {
            "contentType": "application/json"
          },*/
          progressbar: {id:'nodelist-request-query'},
          requestId: REQUEST_TYPE.NODE_QUERY
        };
        return appService.processRequest(config);
      };

      fn.getTrainingsVideosList = function() {
        var config = {
          url: (APP_ENV.baseUrl + "/help/videos"),
          method: "GET",
          progressbar: {id:'get-training-videos'}
        };
        return appService.processRequest(config);
      };

      fn.getFilterOptions = function() {
        var config = {
          url: (APP_ENV.baseUrl + "/hyperconverged/Node/filterlist/"),
          method: "GET"
        };
        return appService.processRequest(config);
      };

      fn.getProfilerInfo = function() {
        var config = {
          url: (APP_ENV.baseUrl + "/hyperconverged/profilerinfo"),
          method: "GET"
        };
        return appService.processRequest(config);
      };

      fn.cloneScenario = function(scenarioId, scenarioData) {
        var config = {
          url: (APP_ENV.baseUrl + "/hyperconverged/scenarios/"+ scenarioId +"/clone"),
          method: "POST",
          data: scenarioData,
          progressbar: {id:'clone-scenario-request-query'},          
          requestId: REQUEST_TYPE.SCENARIO_CLONE
        };
        return appService.processRequest(config);
      };

      fn.saveResults = function(scenarioId, scenarioResults) {
        var config = {
          url: (APP_ENV.baseUrl + "/hyperconverged/results/result_detail/"+ scenarioId),
          method: "PUT",
          data: scenarioResults,
          progressbar: {id:'save-results-request'}
        };
        return appService.processRequest(config);
      };

      fn.sendFeedback = function(data) {
        var config = {
          url: (APP_ENV.baseUrl + "/email"),
          method: "POST",
          data: data,
          progressbar: {id:'feedback-submit-request'}
        };
        return appService.processRequest(config);
      };

      fn.downloadScenarioReport = function(scenarioId, resultName) {

        var reqData = {
          type: "PPT",
          download: "True",
          email: "False",
          nodetype: resultName
        }

        var config = {
          url: (APP_ENV.baseUrl + "/hyperconverged/scenarios/"+ scenarioId +"/report"),
          method: "POST",
          data: reqData,
          progressbar: {id:'scenario-report-download'}
        };
        return appService.processRequest(config);
      };

      fn.downloadBOM = function(scenarioId, resultName) {

        var reqData = {
          type: "XLSX",
          download: "True",
          email: "False",
          nodetype: resultName
        }

        var config = {
          url: (APP_ENV.baseUrl + "/hyperconverged/scenarios/"+ scenarioId +"/bom"),
          method: "POST",
          data: reqData,
          progressbar: {id:'scenario-report-download'}
        };
        return appService.processRequest(config);
      };

    }])

})();
