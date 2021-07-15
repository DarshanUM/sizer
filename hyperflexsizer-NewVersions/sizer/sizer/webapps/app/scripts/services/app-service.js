(function () {
  "use strict";

  angular
    .module('hyperflex')
    .service("appService", ["$http", "$q", "$state", "$sessionStorage", function ($http, $q, $state, $sessionStorage) {

      var fn = this;
      var defaultVersionInfo = {
        sizer_version_str: '0',
        hx_version_str: '0',
        hxbench_version_str: '0',
        sizer_version: 0,
        hx_version: 0,
        hxbench_version: 0
      };
      var _cpuModels = [];
      var pageinfo = {
        'currentPage': 0,
        'scenarioMap': {
          'active': {},
          'fav': {},
          'arch': {}
        },
        'scenarioList': [],
        'searchStr': ''
      }
      var _homeInfoDispFlag;

      fn.setUserDetails = function (userData) {
        var userDetails = {};
        userDetails.name = userData.username;
        userDetails.role = userData.role;
        userDetails.id = userData.userId;

        $sessionStorage._userInfo = userDetails;
        $sessionStorage._isUserLoggedIn = true;
        $sessionStorage._token = userData.auth_token;
      };

      fn.setIopsAccessDet = function (iopsAccess) {
        $sessionStorage._iopsAccess = iopsAccess;
      }

      fn.setFeedbackEmail = function (email) {
        $sessionStorage._feedbackEmail = email || _feedbackEmail;
      };

      fn.setSizerVersion = function (data) {
        data.sizer_version_str = data.sizer_version;
        data.hx_version_str = data.hx_version;
        data.hxbench_version_str = data.hxbench_version;
        data.sizer_version = (parseFloat(data.sizer_version) || 0);
        data.hx_version = (parseFloat(data.hx_version) || 0);
        data.hxbench_version = (parseFloat(data.hxbench_version) || 0);
        $sessionStorage._versionInfo = data;
      };

      fn.setRecommendedSettingsAccess = function (shouldEnable) {
        return $sessionStorage._shouldEnableRecommendedSettings = shouldEnable;
      };

      fn.getRecommendedSettingsAccess = function () {
        return $sessionStorage._shouldEnableRecommendedSettings;
      };

      fn.getSizerVersion = function (data) {
        return $sessionStorage._versionInfo || defaultVersionInfo;
      };

      fn.setProfilerInfo = function (data) {
        $sessionStorage._profilerInfo = data;
      };

      fn.getProfilerInfo = function (data) {
        return $sessionStorage._profilerInfo || {};
      };

      fn.getFeedbackEmail = function () {
        return $sessionStorage._feedbackEmail;
      };

      fn.getIopsAccessDet = function () {
        return $sessionStorage._iopsAccess;
      }

      fn.setLAEStatus = function (isLAE) {
        $sessionStorage._isLAE = isLAE || false;
      };

      fn.isLAE = function () {
        return $sessionStorage._isLAE;
      };

      fn.getUserInfo = function () {
        return $sessionStorage._userInfo || {};
      };

      fn.getToken = function () {
        return $sessionStorage._token;
      };

      fn.isUserLoggedIn = function () {
        return $sessionStorage._isUserLoggedIn;
      };

      fn.getScenarioContext = function () {
        return $sessionStorage._scenarioContext;
      };

      fn.setScenarioContext = function (context) {
        $sessionStorage._scenarioContext = context;
      };

      fn.logout = function () {
        $sessionStorage._isUserLoggedIn = false;
        $sessionStorage._isLAE = false
        $sessionStorage._userInfo = {};
        $sessionStorage._token = '';
        $sessionStorage._feedbackEmail = '';
        $sessionStorage._iopsAccess = false;
        $sessionStorage._versionInfo = '';
        $sessionStorage._profilerInfo = '';
        window.sessionStorage.clear();
        fn.gotoView("login");
      };

      fn.gotoView = function (viewName, viewData) {
        $state.go(viewName, viewData);
      };

      fn.processRequest = function (config) {
        var deferred = $q.defer();
        $http(config).success(function (response) {
          deferred.resolve(response);
        }).error(function (response) {
          deferred.reject(response);
        });

        return deferred.promise;
      };

      fn.getCPUModels = function () {
        return _cpuModels;
      };

      fn.setCPUModels = function (cpuModels) {
        return _cpuModels = cpuModels;
      };

      fn.setHomeDispFlag = function (dispFlag) {
       _homeInfoDispFlag = dispFlag;
      }
      
      fn.getHomeDispFlag = function () {
        return _homeInfoDispFlag;
      }
      fn.setPageData = function (pageInfo) {
        pageinfo = pageInfo;
      }

      fn.getPageData = function () {
        return pageinfo;
      }

    }]); //appService

})();
