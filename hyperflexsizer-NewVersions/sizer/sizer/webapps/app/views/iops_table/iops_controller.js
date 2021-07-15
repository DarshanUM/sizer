(function () {
  "use strict";

  angular
    .module('hyperflex')
    .controller("IOPSController", ["$scope", "$uibModal", "$timeout", "IopsTableService", "utilService", function ($scope, $uibModal, $timeout, IopsTableService, utilService) {
      var vm = this;
      function init() {
        IopsTableService.getIopsData().then(function (resp) {
          var hypervisor = {};
          resp.map(function (option) {
            if (!hypervisor[option.hypervisor]) {
              hypervisor[option.hypervisor] = {
                "hypervisor": option.hypervisor,
                "hListLength": 0,
                "hList": []
              };
            }
            hypervisor[option.hypervisor].hList.push(option);
          });
          angular.forEach(hypervisor, function (value, key) {
            value.hList.map(function (hy) {
              if (!hypervisor[key][hy.server_type]) {
                hypervisor[key][hy.server_type] = {
                  "server_type": hy.server_type,
                  "sList": []
                };
              }
              hypervisor[key][hy.server_type].sList.push(hy);
            });
            angular.forEach(hypervisor[key], function (svalue, skey) {
              if (svalue.hasOwnProperty('sList')) {
                svalue.sList.map(function (server) {
                  if (!hypervisor[key][skey][server.wl_type + '|' + server.iops_type.split('|')[0]]) {
                    hypervisor[key][skey][server.wl_type + '|' + server.iops_type.split('|')[0]] = {
                      "wl_type": server.wl_type,
                      "iops_type": server.iops_type,
                      "wList": []
                    };
                  }
                  hypervisor[key][skey][server.wl_type + '|' + server.iops_type.split('|')[0]]["wList"].push(server);
                });
                var wlCount = 0;
                angular.forEach(hypervisor[key][skey], function (wvalue, wkey) {
                  if (hypervisor[key][skey][wkey].hasOwnProperty("wl_type")) {
                    wlCount++;
                  }
                });
                hypervisor[key][skey]["sListLength"] = wlCount;
                delete hypervisor[key][skey].sList;
              }

              angular.forEach(hypervisor[key][skey], function (wval, wkey) {
                if (wval.hasOwnProperty('wList')) {
                  wval.wList.map(function (workload) {
                    if (!hypervisor[key][skey][wkey][workload.node_substring]) {
                      hypervisor[key][skey][wkey][workload.node_substring] = {
                        "list": []
                      };
                    }
                    hypervisor[key][skey][wkey][workload.node_substring].list.push(workload);
                  });
                }
                delete hypervisor[key][skey][wkey].wList;

                angular.forEach(hypervisor[key][skey][wkey], function (nval, nkey) {
                  if (nval.hasOwnProperty('list')) {
                    nval.list.map(function (node) {
                      if (!hypervisor[key][skey][wkey][nkey][node.ssd_string]) {
                        hypervisor[key][skey][wkey][nkey][node.ssd_string] = {
                          "list": []
                        }
                      }
                      hypervisor[key][skey][wkey][nkey][node.ssd_string].list.push(node);
                    });
                    delete nval.list
                  }

                  angular.forEach(hypervisor[key][skey][wkey][nkey], function (val, k) {
                    if (val.hasOwnProperty('list')) {
                      val.list.map(function (v) {
                        if (!hypervisor[key][skey][wkey][nkey][k][v.replication_factor]) {
                          hypervisor[key][skey][wkey][nkey][k][v.replication_factor] = {
                            "list": []
                          }
                        }
                        hypervisor[key][skey][wkey][nkey][k][v.replication_factor].list.push(v);
                      })
                    }
                    delete val.list;

                    angular.forEach(hypervisor[key][skey][wkey][nkey][k], function (rfval, rfkey) {
                      var list = [];
                      if (rfval.hasOwnProperty('list')) {
                        // for (var i = 0; i < 3; i++) {
                        list = utilService.filteredList(rfval.list, function (option) {
                          // if (option.threshold === 1) {
                          return option.threshold === 1;
                          // }
                        })[0];
                        /* var data = rfval.list.map(function (rfDat) {
                          if (rfDat.threshold === i) {
                            return rfDat;
                          } else {
                            return {};
                          }
                        })
                        list[i] = data[0]; */
                        // }
                        rfval.list = list;
                      }
                    })
                  })
                })
              });
            });
            angular.forEach(hypervisor[key], function (val, k) {
              if (val.hasOwnProperty('server_type')) {
                hypervisor[key]['hListLength'] += val.sListLength;
              }
            });
            delete hypervisor[key].hList;
          });
          vm.hypervisor = [];
          vm.serverType = [];
          vm.workloadIops = [];
          var node_str = {};
          var nodeList = [];
          angular.forEach(hypervisor, function (hval, hkey) {
            vm.hypervisor.push({
              "hypervisor": hval.hypervisor,
              "hypervisor_name": !hval.hypervisor ? 'ESXi' : 'Hyper-V',
              "hListLength": hval.hListLength
            });
            angular.forEach(hval, function (sval, skey) {
              if (sval.hasOwnProperty("server_type")) {
                vm.serverType.push({
                  "hypervisor_name": !hval.hypervisor ? 'ESXi' : 'Hyper-V',
                  "server_type": sval.server_type,
                  "sListLength": sval.sListLength
                })
              }
              angular.forEach(sval, function (wval, wkey) {
                if (wval.hasOwnProperty('wl_type')) {
                  vm.workloadIops.push({
                    "wl_type": wval.wl_type,
                    "iops_type": wval.iops_type
                  })
                }
                angular.forEach(wval, function (nval, nkey) {
                  if (typeof nval === "object") {
                    if (!node_str[nkey]) {
                      node_str[nkey] = {
                        "ssd_count": 0,
                        "node_substring": nkey
                      }
                    }
                    if (typeof nval === "object") {
                      angular.forEach(nval, function (ssdval, ssdkey) {
                        /* ssdval.hasOwnProperty('RF2') || */
                        if (ssdval.hasOwnProperty('RF3')) {
                          if (!node_str[nkey][ssdkey]) {
                            node_str[nkey].ssd_count++;
                            node_str[nkey][ssdkey] = {
                              "RF3": []
                            };
                          }
                          /* if (ssdval.RF2) {
                            node_str[nkey][ssdkey].RF2 = node_str[nkey][ssdkey].RF2.concat(ssdval.RF2.list);
                          } else {
                            node_str[nkey][ssdkey].RF2 = node_str[nkey][ssdkey].RF2.concat([undefined, undefined, undefined]);
                          } */
                          if (ssdval.RF3) {
                            node_str[nkey][ssdkey].RF3 = node_str[nkey][ssdkey].RF3.concat(ssdval.RF3.list);
                          } else {
                            node_str[nkey][ssdkey].RF3 = node_str[nkey][ssdkey].RF3.concat([undefined, undefined, undefined]);
                          }
                        }
                      })
                    }
                  }
                })
              });
            });
          });
          vm.thresholdHeader = []
          for (var i = 0; i < vm.workloadIops.length; i++) {
            vm.thresholdHeader = vm.thresholdHeader.concat(["Standard"])
          }

          angular.forEach(node_str, function (value, key) {
            var list = [];
            if (typeof value === "object") {
              var temp = utilService.filteredList(nodeList, function (node) {
                return node.node_substring === key;
              });
              var count = 0;
              angular.forEach(value, function (ssdval, ssdkey) {
                if (ssdval.hasOwnProperty('RF2') || ssdval.hasOwnProperty('RF3')) {
                  count++;
                  var nodeData = [{
                    "node_substring": key,
                    "ssd_string": ssdkey,
                    "isFirstSsd": true,
                    "rfList": [],
                  }];
                  /* , {
                    "node_substring": key,
                    "ssd_string": ssdkey,
                    "rfList": []
                  } */
                  /* if (ssdval.RF2) {
                    nodeData[0]["repl_factor"] = "RF2";
                    nodeData[0]["rfList"] = ssdval.RF2;
                  }
                  if (ssdval.RF3) {
                    nodeData[1]["repl_factor"] = "RF3";
                    nodeData[1]["rfList"] = ssdval.RF3;
                  } */
                  if (ssdval.RF3) {
                    nodeData[0]["repl_factor"] = "RF3";
                    nodeData[0]["rfList"] = ssdval.RF3;
                  }
                  list = list.concat(nodeData);
                }
              });
              if (list.length > 0) {
                list[0]["isFirstNode"] = true;
                list[0]["ssd_count"] = count;
                nodeList = nodeList.concat(list);
              }
            }
          })



          vm.nodeStr = nodeList;

        })
      }

      $scope.$on('$viewContentLoaded', function (event, viewConfig) {
        $timeout(function () {
          init();
        })
      });
    }]);

})();


