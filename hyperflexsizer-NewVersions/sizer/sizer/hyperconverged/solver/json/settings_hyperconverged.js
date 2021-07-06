(function() {
    'use strict';

    /**
     * @ngdoc overview
     * @name clmServiceRequestApp Settings.js
     * @description
     * # clmServiceRequestApp
     *
     * Store all constant variables here for the clmServiceRequestApp. All data urls will be stored in the constants file.
     */

    angular.module("sizerApp")
        .constant('appSettings', {
            "static" : {
              "baseURL" : "http://localhost:9010",
              "wl_feilds" : {
                 "url" : "/data/fields_hyperconverged.txt"
              }
            },

            //API URL
            "appAPI": {
                "baseURL": "http://127.0.0.1:8000",
                // "baseURL": "http://localhost:9010",
                "download" : {
                  'pdf' : {
                    'url' : "/hyperconverged/Scenario/bomdetail/"
                  }
                },
                "scenarios" : {
                    "list" : {
                     // "url" : "/data/scenarios.json",
                      "url" : "/hyperconverged/Scenario/scenariolist/",
                      "method" : "GET",
                      "auth" : "true"
                    },
                    "details" : {
                      "url" : "/hyperconverged/Scenario/scenariodetail/",
                      "method" : "GET",
                      "auth" : "true"
                    },
                    "update" : {
                      "url" : "/hyperconverged/Scenario/scenariodetail/",
                      //"url" : "/data/scenarioUpdateSuccess.json",
                      "method" : "PUT",
                      //"method" : "GET",
                      "auth" : "true"
                    },
                    "create" : {
                      "url" : "/hyperconverged/Scenario/scenarios/",
                      //"url" : "/data/scenarioAddSuccess.json",
                      "method" : "POST", 
                      //"method" : "GET",
                      "auth" : "true"
                    },
                    "delete" : {
                      "url" : "/hyperconverged/Scenario/scenariodetail/",
                      //"url" : "/data/scenarioAddSuccess.json",
                      "method" : "DELETE", 
                      //"method" : "GET",
                      "auth" : "true"
                    }
                },
                "nodes" : {
                  "url" : "/hyperconverged/Node/nodelist/",
                  //"url" : "/data/nodes.json",
                  "method" : "GET",
                  "auth" : "true"
                },
                "users" : {
                  "register" : {
                    "url" : "/auth/register/",
                    "method" : "POST"
                  },
                  "login" : {
                   //"url" : "/data/login.json",
                    "url" : "/auth/login/",
                    "method" : "POST",
                   // "method" : "GET", // just for test
                  }
                }
            },
            "dateFormat": 'dd/MM/yyyy',
            "currency" : "$",
            "currencyName" : "USD",

            "threshold" : [
              {
                "range" : [0,50],
                "color" : "#2ecc71",
                "label" : "under"
              },
              {
                "range" : [51,90],
                "color" : "#e67e22",
                "label" : "ideal"
              },
              {
                "range" : [91,100],
                "color" : "#c0392b",
                "label" : "over"
              }
            ],
            "showAdvanced" : false,

            "defaultData" : {
                "wl_type": "VDI",
                "userType" : 1,
                "db_server_type" : "OLAP",
                "provisioning_type" : "View Linked Clones",
                "num_db_instances" : 1,
                "num_vms" : 1,
                "num_desktops" : 1
            },

            "dataModels" : {
              'VDI' : {
                  "wl_name": "String",
                  "wl_type": "String",
                  "profile_type": "String",
                  "provisioning_type": "String",
                  "avg_iops_per_desktop": "Number",
                  "gold_image_size": "Number",
                  "vcpus_per_desktop": "Number",
                  "vcpus_per_core": "Number",
                  "disk_per_desktop": "Number",
                  "num_desktops": "Number",
                  "ram_per_desktop": "Number",
                  "replication_factor": "Number",
                  "compression_factor": "Number"
              },
              'Raw' : {
                "wl_name": "",
                "wl_type": "",
                "user_type": "",
                "hdd_size": "",
                "avg_iops": "",
                "ram_size": "",
                "cpu_cores": "",
                "ssd_size": ""
              },
              'VM' : {
                "wl_name": "String",
                "wl_type": "String",
                "profile_type": "String",
                "num_vms": "Number",
                "vcpus_per_vm": "Number",
                "vcpus_per_core": "Number",
                "ram_per_vm": "Number",
                "disk_per_vm": "Number",
                "avg_iops_per_vm": "Number",
                "compression_factor": "Number",
                "replication_factor": "Number" 
              },
              'DB' : {
                "wl_name": "String",
                "wl_type": "String",
                "db_server_type" : "String",
                "profile_type": "String", 
                "business_critical": "String",
                "vcpus_per_core": "Number", 
                "working_set": "Number", 
                "num_db_instances": "Number",
                "db_size": "Number", 
                "ram_per_db": "Number",  
                "vcpus_per_db": "Number", 
                "compression_factor": "Number",
                "replication_factor": "Number",
                "block_size" : "Number", 
                "avg_iops_per_db": "Number", 
                "Read_db" : "Number"
              }
            }
            "errorMsg" : {
              "duplicateName" : "Duplicate name. Choose another name.",
              "numberOutOfRange" : "Number out of range."
            },

            "maxNoOfWorkloads" : 1000


        })


}());





/**/

