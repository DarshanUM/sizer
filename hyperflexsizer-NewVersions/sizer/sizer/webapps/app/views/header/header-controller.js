(function () {
  "use strict";

  angular
    .module('hyperflex')
    .controller('NavbarController', ['$scope', '$uibModal', 'APP_ENV', 'HX_ANALYTICS_EVENTS', 'appService', 'nodeService', '$location', function ($scope, $uibModal, APP_ENV, HX_ANALYTICS_EVENTS, appService, nodeService, $location) {
      var vm = this;
      vm.userInfo = appService.getUserInfo();
      vm.iopsAccess = appService.getIopsAccessDet();
      vm.feedbackEmail = appService.getFeedbackEmail();

      var versionInfo = appService.getSizerVersion();
      vm.sizerVersion = versionInfo.sizer_version_str;
      vm.hxVersion = versionInfo.hx_version_str;
      vm.shouldEnableRecommendedSettingsTab = appService.getRecommendedSettingsAccess();

      vm.helpLink = window.location.protocol + '//' + window.location.host + window.location.pathname + '#/help'
      vm.profilerUrl = appService.getProfilerInfo().profiler_url;

      // var l = window.location;
      // vm.helpLink =  l.protocol + '//' +  l.hostname + ':' + l.port + l.pathname + '#/help'
      vm.gotoHomePage = function () {
        ($scope.root.currentState === "scenario") ?
          $scope.$emit('REFRESH_HOME_PAGE') :
          appService.gotoView("scenario");
      };
      vm.hxBench = function () {
        $location.url('/hx_bench');

      }
      vm.hxprofiler = function () {
        $location.url('/hx_profiler');

      }
      vm.downloadProfiler = function (event) {
        event.preventDefault();
        // window.open(vm.profilerUrl, "_blank");
        // vm.profilerUrl = "https://cisco.box.com/shared/static/enye0doxzebp3yf5kwrxvtrzjq02qctf.ova";
        // window.open(vm.profilerUrl, "_blank", "location=no,toolbar=no,scrollbars=no,resizable=no");
        // console.log("downloadProfiler " , event)
        nodeService.getProfilerDownloadPath().then(function (filePath) {
          // var ovaFilePath = (APP_ENV.baseUrl + "/hyperconverged/downloadprofiler/") + filePath;
          var ovaFilePath = filePath;
          var link = angular.element('#hidden-profiler_download-trigger').attr('href', ovaFilePath).get(0).click();

          // Google analytics :: Tracking the count of profiler ova downloads 
          ga('send', 'event', {
            eventCategory: HX_ANALYTICS_EVENTS.CATEGORY.DOWNLOADS.UI_LABEL,
            eventAction: HX_ANALYTICS_EVENTS.CATEGORY.DOWNLOADS.ACTIONS.HX_PROFILER_OVA,
            eventLabel: HX_ANALYTICS_EVENTS.CATEGORY.DOWNLOADS.LABELS.HX_PROFILER_OVA,
            transport: 'beacon'
          });

        });
      }

      vm.downloadHXBench = function (event) {
        event.preventDefault();
        // window.open(vm.profilerUrl, "_blank");
        // vm.profilerUrl = "https://cisco.box.com/shared/static/enye0doxzebp3yf5kwrxvtrzjq02qctf.ova";
        // window.open(vm.profilerUrl, "_blank", "location=no,toolbar=no,scrollbars=no,resizable=no");
        // console.log("downloadProfiler " , event)
        nodeService.getHXBenchDownloadPath().then(function (filePath) {
          // var ovaFilePath = (APP_ENV.baseUrl + "/hyperconverged/downloadprofiler/") + filePath;
          var ovaFilePath = filePath;
          var link = angular.element('#hidden-hxbench_download-trigger').attr('href', ovaFilePath).get(0).click();

          // Google analytics :: Tracking the count of profiler ova downloads 
          ga('send', 'event', {
            eventCategory: HX_ANALYTICS_EVENTS.CATEGORY.DOWNLOADS.UI_LABEL,
            eventAction: HX_ANALYTICS_EVENTS.CATEGORY.DOWNLOADS.ACTIONS.HX_BENCH_OVA,
            eventLabel: HX_ANALYTICS_EVENTS.CATEGORY.DOWNLOADS.LABELS.HX_BENCH_OVA,
            transport: 'beacon'
          });

        });
      }

      // vm.ovaPopup = function(){ 
      //       var modelWhatsnew = $uibModal.open({
      //           templateUrl: 'views/header/modals/ovamodal.html',
      //           backdrop: 'static',
      //           size: 'sm',
      //           scope: $scope,
      //           controller: 'NavbarController',
      //           resolve: { }
      //       });

      // }

      vm.navigateRefresh = function () {
        var pageData = {
          'currentPage': 0,
          'scenarioMap': {
            'active': {},
            'fav': {},
            'arch': {}
          },
          'scenarioList': [],
          'searchStr': ''
        }
        appService.setPageData(pageData);
        appService.gotoView('scenario');
      }

      vm.whatsnewPopup = function () {
        console.log('in')
        var modelWhatsnew = $uibModal.open({
          templateUrl: 'views/header/modals/whatsnew.html',
          backdrop: 'static',
          size: 'md',
          scope: $scope,
          controller: 'NavbarController',
          resolve: {}
        });

      }

    }]);

})();
