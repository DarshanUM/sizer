(function () {
  "use strict";

  angular
    .module('hyperflex')
    .controller("ScenarioController", ["$window", "$timeout", "$scope", "$uibModal", "appService", "utilService", "scenarioService", "nodeService", "shareScenarioService", function ($window, $timeout, $scope, $uibModal, appService, utilService, scenarioService, nodeService, shareScenarioService) {
      var vm = this;
      var defaultScenarioContext = "ACTIVE";
      vm.recentScenario = [];
      vm.scenarios = [];
      vm.scenarioUI = [];
      vm.sharedScenarios = [];
      vm.favScenarios = [];
      vm.archScenarios = [];
      vm.currentTab = 'active';
      vm.searchStr = '';
      vm.currentOwnership = "";
      vm.areScenariosLoading = true;
      vm.mainContainerHeight = window.innerHeight - 180;
      vm.selectedUsers = []
      vm.markFavActive = false;
      vm.unmarkFavActive = false;
      vm.favLen = 0;
      vm.genLen = 0;
      vm.userData = {};
      vm.numPages = 0;
      vm.startRange = 0;
      vm.endRange = 4;
      vm.currentPage = 0;
      vm.jumpToPage = vm.currentPage + 1;
      vm.noShowFlag = false;
      vm.homeScreenDisp = false;
      vm.scenarioMap = {
        'active': {},
        'fav': {},
        'arch': {}
      }
      vm.tabSelected = {
        'active': { 'scenarios': [], 'total': 0 },
        'fav': { 'scenarios': [], 'total': 0 },
        'arch': { 'scenarios': [], 'total': 0 }
      };

      function init() {
        vm.currentOwnership = appService.getScenarioContext() || defaultScenarioContext;
        vm.areScenariosLoading = true;
        var pageData = appService.getPageData();
        vm.currentPage = pageData.currentPage;
        vm.jumpToPage = vm.currentPage + 1;
        vm.scenarioMap = pageData.scenarioMap;
        vm.searchStr = pageData.searchStr;
        switch (vm.currentOwnership) {
          case 'ACTIVE': {
            vm.scenarios = settingsToScenario(pageData.scenarioList);
            break;
          }
          case 'FAVORITE': {
            vm.favScenarios = settingsToScenario(pageData.scenarioList);
            break;
          }
          case 'ARCHIVE': {
            vm.archScenarios = settingsToScenario(pageData.scenarioList);
            break;
          }
        }
        if (pageData.searchStr !== '') {
          getUserData();
          vm.searchList();
          vm.lengthCheck();
        } else {
          if (pageData.scenarioList.length > 0) {
            getUserData('pageCheck');
          } else {
            getUserData('init');
          }
        }
        if (vm.currentOwnership == "SIZING") {
          vm.addScenario_Sizing = true;
        } else {
          vm.addScenario_Sizing = false;
        }

        $('.inner_Container').scroll(function () {
          if ($(this).scrollTop() > 20) {
            $('.divided_shadow').show()
          } else {
            $('.divided_shadow').hide()
          }
        });



        $('#achiveDate').datetimepicker({ format: 'DD/MM/YYYY' });

        // document.getElementById('todayDate').value = null;



        $(window).resize(function () {
          var but_left = $('.add_scenation_button').offset().left;
          var hx_left = $('.hx_class').offset().left;
          $('.add_scenation_text').css({ 'left': but_left - 50, 'top': '85px' })
          $('.sizing_text').css({ 'left': but_left - 50, 'top': '2px' })
          $('.hx_text').css({ 'left': hx_left - 20, 'top': '0px' })

          if ($(window).width() > 2000) {
            $('.man_view img').css('width', '100%')
            $('.add_scenation_text').css({ 'left': but_left - 50, 'top': '85px' })
          } else {
            $('.man_view img').css('width', '150px')
          }
        })
        /* setTimeout(function () {
          slickCarousel();
        },4500); */

      }

      function slickCarousel() {
        console.log('slick');

        $("#recent_scenario_slider").not('.slick-initialized').slick({
          dots: false,
          // lazyLoad: 'ondemand',
          infinite: false,
          speed: 300,
          slidesToShow: 4,
          slidesToScroll: 4,
          responsive: [
            {
              breakpoint: 1024,
              settings: {
                slidesToShow: 3,
                slidesToScroll: 3,
                infinite: true,
                dots: true
              }
            },
            {
              breakpoint: 600,
              settings: {
                slidesToShow: 2,
                slidesToScroll: 2
              }
            },
            {
              breakpoint: 480,
              settings: {
                slidesToShow: 1,
                slidesToScroll: 1
              }
            }
          ]
        });
        $('#recent_scenario_slider .slick-prev').html('<i class="fa fa-angle-left"></i>');
        $('#recent_scenario_slider .slick-next').html('<i class="fa fa-angle-right"></i>');
        $("#recent_scenario_slider").slick('slickRemove');

      }

      function getUserData(init) {
        nodeService.getUserData().then(function (response) {
          vm.userData = response;
          vm.scenPerPage = (response.scenario_per_page).toString();
          var dispFlag = appService.getHomeDispFlag()
          vm.homeScreenDisp = dispFlag;
          if (dispFlag === undefined) {
            vm.homeScreenDisp = response.home_page_desc;
          }
          vm.disclaimerFlag = response.home_disclaimer;
          // vm.numPages = Math.ceil(vm.userData.scenario_count.active / vm.userData.scenario_per_page);
          if (vm.disclaimerFlag) {
            vm.disclaimerPopup();
          } else {
            if (init === 'init') {
              getScenarios();
            } else if (init === 'pageCheck') {
              vm.areScenariosLoading = false;
              vm.paginationCheck()
              vm.lengthCheck();
            }
          }
        });
      }

      function getScenarios() {
        appService.setScenarioContext(vm.currentOwnership);
        switch (vm.currentOwnership) {
          case 'FAVORITE': {
            vm.currentTab = 'fav';
            break;
          }
          case 'ACTIVE': {
            vm.currentTab = 'active';
            break;
          }
          case 'ARCHIVE': {
            vm.currentTab = 'arch';
            break;
          }

        }
        scenarioService.query({ 'scen_page_limit': 5, 'scen_page_offset': vm.startRange + 1, 'scen_tab': vm.currentOwnership }).$promise.then(function (data) {
          vm.scenarioMap[vm.currentTab][vm.startRange + '-' + vm.endRange] = true;
          vm.areScenariosLoading = false;
          var scenarioList = settingsToScenario(data);
          var startIndex = vm.startRange * vm.scenPerPage;
          if ('ACTIVE' === vm.currentOwnership) {
            for (var i = 0; i < data.length; i++) {
              vm.scenarios[startIndex + i] = data[i];
            }
            // vm.scenarios = settingsToScenario(data);
            // vm.scenarioUI = vm.scenarios;
          } else if ('FAVORITE' === vm.currentOwnership) {
            // vm.favScenarios = settingsToScenario(data);
            for (var i = 0; i < data.length; i++) {
              vm.favScenarios[startIndex + i] = data[i];
            }
            // vm.scenarioUI = vm.favScenarios;
          } else if ('ARCHIVE' === vm.currentOwnership) {
            // vm.archScenarios = settingsToScenario(data);
            for (var i = 0; i < data.length; i++) {
              vm.archScenarios[startIndex + i] = data[i];
            }
            // vm.scenarioUI = vm.archScenarios;
          } else {
            vm.sharedScenarios = scenarioList;
          }
          if ('SHARED' !== vm.currentOwnership) {
            vm.paginationCheck();
          }
          vm.lengthCheck();
          setTimeout(function () {
            var but_left = $('.add_scenation_button').offset().left;
            var hx_left = $('.hx_class').offset().left;
            $('.add_scenation_text').css({ 'left': but_left - 50, 'top': '85px' })
            $('.sizing_text').css({ 'left': but_left - 50, 'top': '2px' })
            $('.hx_text').css({ 'left': hx_left - 20, 'top': '0px' });
            if ($(window).width() > 2000) {
              $('.man_view img').css('width', '100%')
              $('.add_scenation_text').css({ 'left': but_left - 50, 'top': '85px' })
            } else {
              $('.man_view img').css('width', '150px')
            }
          }, 300)

          /*To scroll the page to top, so that user will see the latest scenario that he interacted*/
          $('.bodyScroll').animate({ scrollTop: 0 }, 'fast');
        });
      }



      /*START:: This check is for backward compatibility*/
      function settingsToScenario(scenarios) {
        var scenario,
          scenarioSizerVersion,
          serverSizerVersion = appService.getSizerVersion().sizer_version;
        /* if ('ACTIVE' === vm.currentOwnership) {
          vm.favScenarios = [];
        }else if ('ARCHIVE' === vm.currentOwnership) {
          vm.archScenarios = [];
        } */

        for (var i = 0; i < scenarios.length; i++) {
          scenario = scenarios[i];
          if (!scenario) {
            continue;
          }
          if (!scenario.settings_json[0].account) {
            scenario.settings_json[0].account = scenario.settings_json.account;
          }
          if (!scenario.settings_json[0].deal_id) {
            scenario.settings_json[0].deal_id = scenario.settings_json.deal_id;
          }
          scenarioSizerVersion = parseFloat(scenario.settings_json[0].sizer_version) || 0;
          /*if no sizer version or client/scenario sizer version is less than server sizer version*/
          if (scenario.wl_count && (!scenarioSizerVersion || scenarioSizerVersion < serverSizerVersion)) {
            scenario.isUptodate = false;
          } else {
            scenario.isUptodate = true;
          }
          if (vm.tabSelected.active.scenarios.indexOf(scenario.id) > -1 || vm.tabSelected.fav.scenarios.indexOf(scenario.id) > -1) {
            scenario.selected = true;
          }
          if (scenario.selected && vm.tabSelected[vm.currentTab].scenarios.indexOf(scenario.id) === -1) {
            vm.tabSelected[vm.currentTab].scenarios.push(scenario.id);
            vm.tabSelected[vm.currentTab].total++;
          }
          if (!scenario.selected && vm.tabSelected[vm.currentTab].scenarios.indexOf(scenario.id) > -1) {
            vm.tabSelected[vm.currentTab].scenarios = utilService.filteredList(vm.tabSelected[vm.currentTab].scenarios, function (scen) {
              return scenario.id !== scen;
            });
            vm.tabSelected[vm.currentTab].total = vm.tabSelected[vm.currentTab].scenarios.length;
          }
          /* var sceneFavCopy = angular.copy(scenario);
          sceneFavCopy.selected = false;
          if ('fav' === sceneFavCopy.scen_label) {
            if (vm.tabSelected.fav.scenarios.indexOf(sceneFavCopy.id) > -1) {
              sceneFavCopy.selected = true;
            }
            // vm.favScenarios.push(sceneFavCopy);
          }
          var scenario = angular.copy(sceneArchCopy); */

        }
        return scenarios;
      }
      /*This check is for backward compatibility ::END*/

      /*This event will be fired from resize-scenario directive on success of resize*/
      $scope.$on("RESIZE_SCENARIO", function (event, data) {
        if ("SUCCESS" === data.status) {
          nodeService.getScenarioById(data.data.id).then(function (response) {
            switch (vm.currentOwnership) {
              case 'ACTIVE': {
                /* vm.scenarios = vm.scenarios.map(function (scen) {
                  if (scen.id === data.id) {
                    scen = data;
                  }
                  return scen;
                }); */
                vm.scenarios = utilService.filteredList(vm.scenarios, function (scen) {
                  if (!scen) {
                    return true;
                  }
                  return scen.id !== response.id;
                });

                vm.scenarios = [response].concat(vm.scenarios);
                vm.scenarios = settingsToScenario(vm.scenarios);
                break;
              }
              case 'FAVORITE': {
                vm.favScenarios = utilService.filteredList(vm.favScenarios, function (scen) {
                  if (!scen) {
                    return true;
                  }
                  return scen.id !== response.id;
                });

                vm.favScenarios = [response].concat(vm.favScenarios);
                vm.favScenarios = settingsToScenario(vm.favScenarios);
                break;
              }
              case 'ARCHIVE': {
                vm.archScenarios = utilService.filteredList(vm.archScenarios, function (scen) {
                  if (!scen) {
                    return true;
                  }
                  return scen.id !== response.id;
                });

                vm.archScenarios = [response].concat(vm.archScenarios);
                vm.archScenarios = settingsToScenario(vm.archScenarios);
                break;
              }
            }
            vm.scenarioMap[vm.currentTab][vm.startRange + '-' + vm.endRange] = false;
            if (vm.searchStr !== '') {
              vm.searchData = vm.searchData.map(function (scen) {
                if (scen.id === response.id) {
                  scen = response;
                }
                return scen;
              })
            }
            vm.paginationCheck();
          })
        }
      });

      vm.logout = function () {

        appService.logout();
        $window.location.href = vm.userData.logout_url;

        /* $uibModal.open({
          templateUrl: 'views/scenario/modals/forbidden.html',
          size: 'md',
          controller: 'ScenarioController',
          controllerAs: 'scenCtrl',
          backdrop: 'static',
          keyboard: false
        }).result.then(function (modalData) {
        }, function (data) {
        }); */
      }

      vm.disclaimerPopup = function () {
        $uibModal.open({
          templateUrl: 'views/scenario/modals/disclaimer.html',
          size: 'md',
          controller: 'ScenarioController',
          controllerAs: 'scenCtrl',
          backdrop: 'static',
          keyboard: false
        }).result.then(function (modalData) {
          if (modalData.confirm) {
            var req = {
              'home_disclaimer': false
            }
            nodeService.userDataPost(req).then(function () {
              vm.disclaimerFlag = false;
              getScenarios()
              console.log('disc change');
            });
          } else {
            vm.logout();
          }
        }, function (data) {
        });
      }

      vm.clearSearch = function () {
        vm.searchStr = '';
        vm.resetPageData();
        vm.searchList();
      }

      vm.searchList = function (event) {
        if (vm.searchStr === '') {
          vm.paginationCheck();
          return;
        }
        if (event) {
          if (event.keyCode !== 13) {
            return;
          } else {
            vm.resetPageData();
          }
        }
        vm.searchData = [];
        scenarioService.query({ 'search': vm.searchStr, 'scen_tab': vm.currentOwnership }).$promise.then(function (data) {
          vm.areScenariosLoading = false;
          vm.searchData = settingsToScenario(data);
          vm.paginationCheck();
        })
      }

      vm.noShowPost = function () {
        vm.homeScreenDisp = false;
        appService.setHomeDispFlag(vm.homeScreenDisp);
        if (vm.noShowFlag) {
          var req = {
            'home_page_desc': false
          }
          nodeService.userDataPost(req).then(function () {
            console.log('No show');
          });
        }
      }

      vm.scenarioPerPageChange = function () {
        var req = {
          'scenario_per_page': parseInt(vm.scenPerPage, 10)
        }
        nodeService.userDataPost(req).then(function (res) {
          vm.paginationCheck();
        });
      }

      vm.prevClick = function () {
        vm.currentPage = vm.currentPage - 1;
        vm.paginationCheck();
      }

      vm.nextClick = function () {
        vm.currentPage = vm.currentPage + 1;
        vm.paginationCheck();
      }

      vm.paginationJump = function () {
        if (vm.jumpToPage < 1 || vm.jumpToPage > vm.numPages) {
          return;
        }
        vm.currentPage = vm.jumpToPage - 1;
        vm.paginationCheck();
      }

      vm.paginationCheck = function () {
        var scenarioList;
        if (vm.searchStr === '') {
          switch (vm.currentOwnership) {
            case 'FAVORITE': {
              vm.numPages = Math.ceil(vm.userData.scenario_count.favorite / vm.scenPerPage);
              break;
            }
            case 'ACTIVE': {
              vm.numPages = Math.ceil(vm.userData.scenario_count.active / vm.scenPerPage);;
              break;
            }
            case 'ARCHIVE': {
              vm.numPages = Math.ceil(vm.userData.scenario_count.archive / vm.scenPerPage);
              break;
            }
          }
          switch (vm.currentOwnership) {
            case 'ACTIVE': {
              scenarioList = vm.scenarios;
              break;
            }
            case 'ARCHIVE': {
              scenarioList = vm.archScenarios;
              break;
            }
            case 'FAVORITE': {
              scenarioList = vm.favScenarios;
              break;
            }
          }
          var idex;
          for (idex = 0; idex < vm.numPages; idex += 5) {
            if (vm.currentPage >= idex && vm.currentPage <= (idex + 4)) {
              vm.startRange = idex;
              vm.endRange = (idex + 4) > vm.numPages ? vm.numPages : idex + 4;
              break;
            }
          }
          if (vm.scenarioMap[vm.currentTab][vm.startRange + '-' + vm.endRange]) {
            vm.scenarioUI = [];
            var i;
            for (i = (vm.currentPage * vm.scenPerPage); i < ((vm.currentPage + 1) * vm.scenPerPage); i++) {
              if (scenarioList[i]) {
                vm.scenarioUI.push(scenarioList[i]);
              }
            }
          } else {
            getScenarios();
          }
        } else {
          vm.numPages = Math.ceil(vm.searchData.length / vm.scenPerPage);
          scenarioList = vm.searchData;
          vm.scenarioUI = [];
          var i;
          for (i = (vm.currentPage * vm.scenPerPage); i < ((vm.currentPage + 1) * vm.scenPerPage); i++) {
            if (scenarioList[i]) {
              vm.scenarioUI.push(scenarioList[i]);
            }
          }
        }
        vm.recentScenario = [];
        for (var i = 0; i < 8; i++) {
          if (vm.scenarios[i]) {
            vm.recentScenario[i] = angular.copy(vm.scenarios[i]);
            delete vm.recentScenario[i].selected;
          }
        }


        // vm.recentScenario = [];
        setTimeout(function () {

          slickCarousel();
          $('#recent_scenario_slider')[0].slick.refresh();
          $('.slick-prev').html('<i class="fa fa-angle-left"></i>');
          $('.slick-next').html('<i class="fa fa-angle-right"></i>');


        }, 500);

        // $(window).resize(function(){
        //   $('.slide_carousel')[0].slick.refresh();
        // });



      }

      vm.lengthCheck = function () {
        vm.lengthHide = false;
        if ('ACTIVE' === vm.currentOwnership && vm.scenarios.length === 0) {
          vm.lengthHide = true;
          /* } else if (vm.currentTab === 'fav' && vm.favScenarios.length === 0) {
            vm.lengthHide = true;
          } */
        } else if ('FAVORITE' === vm.currentOwnership && vm.favScenarios.length === 0) {
          vm.lengthHide = true;
        } else if ('ARCHIVE' === vm.currentOwnership && vm.archScenarios.length === 0) {
          vm.lengthHide = true;
        } else if ('SHARED' === vm.currentOwnership && vm.sharedScenarios.length === 0) {
          vm.lengthHide = true;
        }
      }

      vm.viewScenarioDetails = function (id, newScen) {
        var scenarioList;
        switch (vm.currentOwnership) {
          case 'ACTIVE': {
            scenarioList = vm.scenarios;
            vm.scenarioMap.fav = {};
            vm.scenarioMap.arch = {};
            break;
          }
          case 'FAVORITE': {
            scenarioList = vm.favScenarios;
            vm.scenarioMap.active = {};
            vm.scenarioMap.arch = {};
            break;
          }
          case 'ARCHIVE': {
            scenarioList = vm.archScenarios;
            vm.scenarioMap.fav = {};
            vm.scenarioMap.active = {};
            break;
          }
        }
        var pageData = {
          'currentPage': vm.currentPage,
          'scenarioMap': vm.scenarioMap,
          'scenarioList': scenarioList,
          'searchStr': vm.searchStr
        }
        if (newScen) {
          pageData['newScen'] = true;
        }
        appService.setPageData(pageData);
        appService.gotoView('scenariodetails', { id: id });
      };

      /* vm.changeTab = function (tab) {
        vm.currentTab = tab;
        vm.currentOwnership = (tab === 'arch') ? 'ARCHIVE' : 'ACTIVE';
        vm.scenarioUI = [];
        switch (vm.currentTab) {
          case 'arch': vm.scenarioUI = vm.archScenarios;
            break;
          case 'fav': vm.scenarioUI = vm.favScenarios;
            break;
          case 'active': vm.scenarioUI = vm.scenarios;
            break;
          default: vm.scenarioUI = vm.sharedScenarios;
            break;
        }
        vm.lengthCheck();
        appService.setScenarioContext(vm.currentOwnership);
      }; */

      vm.toggleOwnership = function (ownership) {
        console.log('ownership', ownership.length);
        if (vm.currentOwnership !== ownership) {
          vm.searchStr = '';
          vm.currentOwnership = ownership;
          vm.startRange = 0;
          vm.endRange = 4;
          vm.currentPage = 0;
          vm.jumpToPage = 1;
          // if ('SHARED' === ownership || 'ARCHIVE' === ownership || ('OWNED' === ownership && 0 === vm.scenarios.length)) {
          vm.resetPageData();
          getScenarios();
          console.log(" toggleScenarios ");
          // }
        }
        if (ownership === "SIZING" || 'ACTIVE' === ownership) {
          vm.addScenario_Sizing = false;
        } else {
          vm.addScenario_Sizing = true;
        }
        vm.lengthCheck();
      };

      vm.shareScenarioPopup = function (scenario) {
        $uibModal.open({
          templateUrl: 'views/scenario/modals/share_scenario.html',
          size: 'md',
          controller: 'ScenarioShareController',
          controllerAs: 'shareCtrl',
          backdrop: 'static',
          keyboard: false,
          resolve: {
            scenarioObject: scenario
          }

        }).result.then(function (scenariosList) {
          //refresh the scenarios list
          // getScenarios();
          // appService.gotoView('scenariodetails', { id: data.resp.id });
          // vm.scenarios = settingsToScenario(scenariosList);
          getUserData('init');
        }, function (data) {
          // console.log("fail kjgjj ", data)
        });
      };

      vm.confirmArchive = function (flag, scenario) {
        if (!flag || ((typeof scenario === 'undefined' && 'active' === vm.currentTab && vm.favLen < 1) || (typeof scenario !== 'undefined' && 'fav' !== scenario.scen_label))) {
          vm.archiveScene(flag, scenario);
        } else {
          $uibModal.open({
            templateUrl: 'views/scenario_details/modals/fav_to_archive.html',
            backdrop: 'static',
            size: 'sm',
            controller: 'ScenarioController',
            resolve: {
            }
          }).result.then(function (result) {
            vm.archiveScene(flag, scenario);
          }, function () {
            console.log("dismissed");
          });
        }
      };

      vm.archiveScene = function (flag, scenario) {
        var selScenarios = angular.copy(vm.tabSelected[vm.currentTab]['scenarios']);
        if (typeof scenario !== 'undefined') {
          selScenarios = [scenario.id];
          if (flag) {
            vm.userData.scenario_count.archive++;
            vm.userData.scenario_count.active--;
          } else {
            vm.userData.scenario_count.archive--;
            vm.userData.scenario_count.active++;
          }
        }
        var request = {
          'scen_id_list': selScenarios,
          'move_to': 'archive'
        };
        if (!flag) {
          request.move_to = 'general';
          selScenarios.map(function (id) {
            var archSelExists = vm.tabSelected.arch['scenarios'].indexOf(id);
            if (archSelExists > -1) {
              vm.tabSelected.arch['scenarios'].splice(archSelExists, 1);
              vm.tabSelected.arch.total--;
            }
          });
        } else {
          selScenarios.map(function (id) {
            var favSelExists = vm.tabSelected.fav['scenarios'].indexOf(id);
            if (favSelExists > -1) {
              vm.tabSelected.fav['scenarios'].splice(favSelExists, 1);
              vm.tabSelected.fav.total--;
            }
          });
          selScenarios.map(function (id) {
            var genSelExists = vm.tabSelected.active['scenarios'].indexOf(id);
            if (genSelExists > -1) {
              vm.tabSelected.active['scenarios'].splice(genSelExists, 1);
              vm.tabSelected.active.total--;
            }
          });
        }
        scenarioService.patch({}, request).$promise.then(function (data) {
          //refresh the scenarios list
          vm.areScenariosLoading = false;
          if (typeof scenario === 'undefined') {
            vm.tabSelected[vm.currentTab]['scenarios'] = [];
            vm.tabSelected[vm.currentTab]['total'] = 0;
            if ('active' === vm.currentTab) {
              vm.markFavActive = false;
              vm.unmarkFavActive = false;
              vm.favLen = 0;
              vm.genLen = 0;
            }
          }
          /* if (typeof scenario === 'undefined') {
            getUserData();
          } else { */
          if (typeof scenario === 'undefined') {
            if (vm.searchStr !== '') {
              vm.resetPageData();
              vm.searchList();
            } else {
              vm.resetPageData();
              getUserData('init');
            }
          } else {
            scenario.scen_label = flag ? 'archive' : 'general'
            if (flag) {
              vm.userData.scenario_count.archive++;
              vm.archScenarios.push(scenario);
              vm.userData.scenario_count.active--;
              if (vm.currentOwnership === 'FAVORITE') {
                vm.userData.scenario_count.favorite--;
              }
              vm.scenarios = utilService.filteredList(vm.scenarios, function (scen) {
                if (!scen) {
                  return true;
                }
                return scen.id !== scenario.id;
              })
              vm.favScenarios = utilService.filteredList(vm.favScenarios, function (scen) {
                if (!scen) {
                  return true;
                }
                return scen.id !== scenario.id;
              })
            } else {
              vm.archScenarios = utilService.filteredList(vm.archScenarios, function (scen) {
                if (!scen) {
                  return true;
                }
                return scen.id !== scenario.id;
              })
              vm.userData.scenario_count.active++;
              vm.userData.scenario_count.archive--;
            }
            vm.scenarioMap[vm.currentTab][vm.startRange + '-' + vm.endRange] = false;
            if (vm.searchStr !== '') {
              vm.searchData = utilService.filteredList(vm.searchData, function (scen) {
                if (!scen) {
                  return true;
                }
                return scen.id !== scenario.id;
              })
            }
            vm.paginationCheck();
            console.log(vm.userData);
          }
          // }
          // getScenarios();
        }, function (data) {
          // console.log("fail kjgjj ", data)
        });
      };

      vm.resetPageData = function () {
        var pagedata = {
          'currentPage': 0,
          'scenarioMap': {
            'active': {},
            'fav': {},
            'arch': {}
          },
          'scenarioList': []
        }
        vm.scenarioMap = pagedata.scenarioMap;
        vm.currentPage = pagedata.currentPage;
        vm.startRange = 0;
        vm.endRange = 4;
      }

      vm.toggleFav = function (flag, scenario) {
        var selScenarios = angular.copy(vm.tabSelected[vm.currentTab]['scenarios']);
        if (typeof scenario !== 'undefined') {
          selScenarios = [scenario.id];
        }
        var request = {
          'scen_id_list': selScenarios,
          'move_to': 'fav'
        };
        if (!flag) {
          request.move_to = 'general';
          selScenarios.map(function (id) {
            var favSelExists = vm.tabSelected.fav['scenarios'].indexOf(id);
            if (favSelExists > -1) {
              vm.tabSelected.fav['scenarios'].splice(favSelExists, 1);
              vm.tabSelected.fav.total--;
            }
          });
        } else {
          selScenarios.map(function (id) {
            var archSelExists = vm.tabSelected.arch['scenarios'].indexOf(id);
            if (archSelExists > -1) {
              vm.tabSelected.arch['scenarios'].splice(archSelExists, 1);
              vm.tabSelected.arch.total--;
            }
          });
        }

        scenarioService.patch({}, request).$promise.then(function (data) {
          //refresh the scenarios list
          vm.areScenariosLoading = false;
          if (typeof scenario === 'undefined') {
            vm.tabSelected[vm.currentTab]['scenarios'] = [];
            vm.tabSelected[vm.currentTab]['total'] = 0;
            if ('active' === vm.currentTab) {
              vm.markFavActive = false;
              vm.unmarkFavActive = false;
              vm.favLen = 0;
              vm.genLen = 0;
            }
          }
          if (typeof scenario === 'undefined') {
            vm.resetPageData();
            if (vm.searchStr !== '') {
              vm.searchList();
            } else {
              getUserData('init');
            }
          } else {
            nodeService.getScenarioById(scenario.id).then(function (response) {
              /* vm.scenarios = vm.scenarios.map(function(scen){
                if(scen.id === response.id){
                  scen = response;
                }
                return scen;
              }); */
              vm.scenarios = utilService.filteredList(vm.scenarios, function (scen) {
                if (!scen) {
                  return true;
                }
                return scen.id !== response.id;
              });

              vm.scenarios = [response].concat(vm.scenarios)
              if (flag) {
                vm.userData.scenario_count.favorite++;
              } else {
                vm.userData.scenario_count.favorite--;
              }
              if (vm.currentOwnership === 'FAVORITE') {
                vm.favScenarios = utilService.filteredList(vm.favScenarios, function (scen) {
                  if (!scen) {
                    return true;
                  }
                  return scen.id !== response.id;
                });
              }
              // vm.scenarioMap[vm.currentTab][vm.startRange + '-' + vm.endRange] = false;
              if (vm.searchStr !== '') {
                vm.searchData = vm.searchData.map(function (scen) {
                  if (scen.id === response.id) {
                    scen = response;
                  }
                  return scen;
                })
              }
              vm.paginationCheck();
              console.log(vm.userData);
            })
          }

        }, function (data) {
        });
      };

      vm.activePanel = function (scenario) {
        scenario = utilService.getClone(scenario);
        if (scenario.selected) {
          vm.tabSelected[vm.currentTab]['total']++;
          vm.tabSelected[vm.currentTab]['scenarios'].push(scenario.id);
          if ('fav' === scenario.scen_label && 'active' === vm.currentTab) {
            vm.unmarkFavActive = true;
            vm.favLen++;
          } else if ('fav' !== scenario.scen_label && 'active' === vm.currentTab) {
            vm.markFavActive = true;
            vm.genLen++;
          }
        } else {
          /* vm.tabSelected[vm.currentTab].total--;
          vm.tabSelected[vm.currentTab]['scenarios'] = utilService.filteredList(vm.tabSelected[vm.currentTab]['scenarios'], function (scene) {
            return scene !== scenario.id;
          }); */
          // if ('fav' === vm.currentTab) {
          vm.tabSelected['active']['scenarios'] = utilService.filteredList(vm.tabSelected.active['scenarios'], function (scene) {
            return scene !== scenario.id;
          });
          vm.tabSelected['active'].total = vm.tabSelected['active']['scenarios'].length;
          vm.tabSelected['fav']['scenarios'] = utilService.filteredList(vm.tabSelected.fav['scenarios'], function (scene) {
            return scene !== scenario.id;
          });
          vm.tabSelected['fav'].total = vm.tabSelected['fav']['scenarios'].length;
          // }
          if ('fav' === scenario.scen_label && 'active' === vm.currentTab) {
            vm.favLen--;
            if (0 === vm.favLen) {
              vm.unmarkFavActive = false;
            }
          } else if ('fav' !== scenario.scen_label && 'active' === vm.currentTab) {
            vm.genLen--;
            if (0 === vm.genLen) {
              vm.markFavActive = false;
            }
          }
        }
      };

      vm.bulkDelete = function () {
        console.log(vm.tabSelected[vm.currentTab]['scenarios']);
        $uibModal.open({
          templateUrl: 'views/scenario_details/modals/bulk-delete-confirm.html',
          backdrop: 'static',
          size: 'sm',
          controller: 'ScenarioController',
          resolve: {
          }
        }).result.then(function (result) {
          var request = { 'scen_id_list': vm.tabSelected[vm.currentTab]['scenarios'] };
          nodeService.bulkDelete(request).then(function () {
            // getScenarios();
            vm.tabSelected[vm.currentTab]['scenarios'] = [];
            vm.tabSelected[vm.currentTab]['total'] = 0;
            vm.resetPageData();
            if (vm.searchStr !== '') {
              vm.searchList();
            } else {
              getUserData('init');
            }

          });
        }, function () {
          console.log("dismissed");
        });

      }


      vm.addScenarioPopup = function () {
        $uibModal.open({
          templateUrl: 'views/scenario/modals/add_scenario.html',
          size: 'sm',
          controller: 'ScenarioPopupController',
          controllerAs: 'popupCtrl',
          backdrop: 'static',
          keyboard: false,
          resolve: {
            scenarioObject: null,
            sharedUsers: null
          }

        }).result.then(function (data) {
          console.log("success ", data);
          //refresh the scenarios list
          // getScenarios();
          // vm.userData.scenario_count.active++;
          vm.resetPageData();
          vm.viewScenarioDetails(data.resp.id, 'addNew')
          // appService.gotoView('scenariodetails', { id: data.resp.id });
        }, function (data) {
          console.log('fail ', data);
        });
      };
      vm.stopAction = function (event) {
        event.stopPropagation();
      };
      vm.submitArchive = function (event) {
        $(event.currentTarget.parentElement.parentElement.parentElement).removeClass('open')
        var date = vm.archiveDate.split("/");
        var dateData = date[2] + "-" + date[1] + "-" + date[0] + "T00:00:00Z"
        // var dateData = date.getFullYear() + "-" + (date.getMonth() +] 1) + "-" + date.getDate() + "T00:00:00Z"
        var reqPayload = { "move_to": "archive", "input_date": dateData };
        nodeService.autoArchive(reqPayload).then(function (data) {
          vm.archiveDate = null;
          vm.resetPageData();
          if (vm.searchStr !== '') {
            vm.searchList();
          } else {
            getUserData('init');
          }
          // getScenarios();
        });
      }
      vm.editScenarioPopup = function (scenario) {
        scenario = utilService.getClone(scenario);
        scenario = Object.assign({}, scenario, { settings_json: scenario.settings_json[0] });
        $uibModal.open({
          templateUrl: 'views/scenario/modals/edit_scenario.html',
          size: 'sm',
          backdrop: 'static',
          keyboard: false,
          controller: 'ScenarioPopupController',
          controllerAs: 'popupCtrl',
          resolve: {
            scenarioObject: scenario,
            sharedUsers: null
          }

        }).result.then(function (data) {
          console.log("success ", data);
          //refresh the scenarios list
          // getScenarios();
          nodeService.getScenarioById(scenario.id).then(function (response) {
            switch (vm.currentOwnership) {
              case 'ACTIVE': {
                vm.scenarios = utilService.filteredList(vm.scenarios, function (scen) {
                  if (!scen) {
                    return true;
                  }
                  return scen.id !== response.id;
                });

                vm.scenarios = [response].concat(vm.scenarios);
                vm.scenarios = settingsToScenario(vm.scenarios);
                break;
              }
              case 'FAVORITE': {
                vm.favScenarios = utilService.filteredList(vm.favScenarios, function (scen) {
                  if (!scen) {
                    return true;
                  }
                  return scen.id !== response.id;
                });

                vm.favScenarios = [response].concat(vm.favScenarios);
                vm.favScenarios = settingsToScenario(vm.favScenarios);
                break;
              }
              case 'ARCHIVE': {
                vm.archScenarios = utilService.filteredList(vm.archScenarios, function (scen) {
                  if (!scen) {
                    return true;
                  }
                  return scen.id !== response.id;
                });

                vm.archScenarios = [response].concat(vm.archScenarios);
                vm.archScenarios = settingsToScenario(vm.archScenarios);
                break;
              }
            }
            vm.scenarioMap[vm.currentTab][vm.startRange + '-' + vm.endRange] = false;
            if (vm.searchStr !== '') {
              vm.searchData = vm.searchData.map(function (scen) {
                if (scen.id === response.id) {
                  scen = response;
                }
                return scen;
              })
              vm.searchData = utilService.filteredList(vm.searchData, function (scen) {
                return scen.name.toLowerCase().indexOf(vm.searchStr.toLowerCase()) !== -1;
              });
            }
            vm.paginationCheck();
          })
        }, function (data) {
          console.log("fail ", data)
        });
      };

      vm.cloneScenarioPopup = function (scenario) {
        scenario = utilService.getClone(scenario)
        scenario = Object.assign({}, scenario, { settings_json: scenario.settings_json[0] })
        var clonedScenario = angular.extend({}, scenario);
        clonedScenario.name = clonedScenario.name + "-copy";
        $uibModal.open({
          templateUrl: 'views/scenario/modals/clone_scenario.html',
          size: 'sm',
          backdrop: 'static',
          keyboard: false,
          controller: 'ScenarioPopupController',
          controllerAs: 'popupCtrl',
          resolve: {
            scenarioObject: clonedScenario,
            sharedUsers: null
          }

        }).result.then(function (data) {
          //refresh the scenarios list
          // vm.scenarios = data;
          /* vm.userData.scenario_count.active++;
          switch (vm.currentOwnership) {
            case 'ACTIVE': {
              vm.scenarios = [data].concat(vm.scenarios);
              vm.scenarios = settingsToScenario(vm.scenarios);
              break;
            }
            case 'FAVORITE': {
              // vm.favScenarios.push(data);
              vm.favScenarios = [data].concat(vm.favScenarios);
              vm.favScenarios = settingsToScenario(vm.favScenarios);
              break;
            }
            case 'ARCHIVE': {
              vm.archScenarios = [data].concat(vm.archScenarios);
              // vm.archScenarios.push(data);
              vm.archScenarios = settingsToScenario(vm.archScenarios);
              break;
            }
          }
          vm.paginationCheck(); */
          vm.resetPageData();
          if (vm.searchStr === '') {
            getUserData('init')
          } else {
            vm.searchList();
          }
          // getScenarios();
        }, function (data) {
          console.log("fail ", data)
        });
      };

      vm.keypress = function (event) {
        if (event.keyCode === 13) {
          vm.paginationJump();
        }
      }

      vm.deleteScenarioPopup = function (scenario) {
        $uibModal.open({
          templateUrl: 'views/scenario/modals/delete_scenario.html',
          size: 'sm',
          backdrop: 'static',
          keyboard: false,
          controller: 'ScenarioPopupController',
          controllerAs: 'popupCtrl',
          resolve: {
            scenarioObject: scenario,
            sharedUsers: null
          }

        }).result.then(function (data) {
          //refresh the scenarios list
          switch (vm.currentOwnership) {
            case 'ACTIVE': {
              vm.userData.scenario_count.active--;
              if (scenario.scen_label === 'fav') {
                vm.userData.scenario_count.favorite--;
              }
              vm.scenarios = utilService.filteredList(vm.scenarios, function (scen) {
                if (!scen) {
                  return true;
                }
                return scen.id !== scenario.id;
              });
              break;
            }
            case 'FAVORITE': {
              vm.userData.scenario_count.active--;
              vm.userData.scenario_count.favorite--;
              vm.favScenarios = utilService.filteredList(vm.favScenarios, function (scen) {
                if (!scen) {
                  return true;
                }
                return scen.id !== scenario.id;
              });
              break;
            }
            case 'ARCHIVE': {
              vm.userData.scenario_count.archive--;
              vm.archScenarios = utilService.filteredList(vm.archScenarios, function (scen) {
                if (!scen) {
                  return true;
                }
                return scen.id !== scenario.id;
              });
              break;
            }
          }
          vm.scenarioMap[vm.currentTab][vm.startRange + '-' + vm.endRange] = false;
          if (vm.searchStr !== '') {
            vm.searchData = utilService.filteredList(vm.searchData, function (scen) {
              return scen.id !== scenario.id;
            });
          }
          vm.paginationCheck();
          console.log(vm.userData);
          // getScenarios();
        }, function (data) {
          console.log("fail ", data)
        });
      };

      $scope.$on('REFRESH_HOME_PAGE', function () {
        init();
      });

      $scope.$on('$viewContentLoaded', function (event, viewConfig) {
        // init();
        // if not initiating in timeout, loader is not displaying
        $timeout(function () {
          init();
        }, 10)

      });

    }]);

})();
