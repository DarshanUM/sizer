(function() {
  "use strict";

  angular
    .module('hyperflex')
    .service("ScenarioTransformer", [function() {
      // internal/private variables
      var fn = this;

      fn.transformToUI = function(scenarioData){
        if(!scenarioData || !scenarioData.workload_result) return scenarioData;

        var newData = getDuplicate(scenarioData);
        var i, j, k, wlResult, clusters, cluster;
        for(i=0; i<newData.workload_result.length; i++){
          wlResult = newData.workload_result[i];
          for(j=0; j<wlResult.clusters.length; j++){
            cluster = wlResult.clusters[j];
            for(k=0; k<cluster.wl_list.length; k++){
              TransfromDBWorkloadToUI( cluster.wl_list[k] );   
            }
          }
        }
        return newData;
      };

      fn.transformToAPI = function(scenarioData){
        if(!scenarioData || !scenarioData.wl_list) return scenarioData;

        var newData = getDuplicate(scenarioData);
        for(var i=0; i<newData.wl_list.length; i++){
          TransfromDBWorkloadToAPI( newData.wl_list[i] );
        }
        return newData;
      };

      /* Internal / Private functions */
      function getDuplicate(data){
        return JSON.parse( JSON.stringify(data) );
      }

      function TransfromDBWorkloadToUI(workload){
        if(workload.wl_type === "OLAP" || workload.wl_type === "OLTP"  ){
          workload.db_type = workload.wl_type; 
          workload.wl_type = "DB";
        }
      }

      function TransfromDBWorkloadToAPI(workload){
        /*This 'clusterIndex' is being created in UI & used for UI purposes*/
        delete workload.clusterIndex;

        if(workload.wl_type === "DB" ){
          workload.wl_type = workload.db_type;
          if(workload.db_type === "OLAP"){
            delete workload.avg_iops_per_db;
          }else if(workload.db_type === "OLTP"){
            delete workload.avg_mbps_per_db;
          }
          delete workload.db_type;
        }
      }


    }]);

})();
