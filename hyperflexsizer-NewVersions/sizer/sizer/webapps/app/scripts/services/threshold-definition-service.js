(function() {
  'use strict';

  angular
    .module('hyperflex')
    .service('THRESHOLD_DEFINITION', ['appService', 'APP_ENV', 'REQUEST_TYPE', function(appService, APP_ENV, REQUEST_TYPE) {

      var fn = this;
      var CONSERVATIVE = 0;
      var STANDARD = 1;
      var AGGRESSIVE = 2;      

      /*
      // default response
      {
        'CONSERVATIVE' : [
          {name: "cpu", val: "70"},{name: "ram", val: "70"},{name: "hdd", val: "80"},{name: "ssd", val: "80"},{name: "iops", val: "80"}
        ],
        'STANDARD' : [
          {name: "cpu", val: "80"},{name: "ram", val: "80"},{name: "hdd", val: "90"},{name: "ssd", val: "90"},{name: "iops", val: "90"}
        ],
        'AGGRESSIVE' : [
          {name: "cpu", val: "100"},{name: "ram", val: "100"},{name: "hdd", val: "95"},{name: "ssd", val: "95"},{name: "iops", val: "95"}
        ]
      };*/

      getThresholdDefinitions().then(function(data){
        /*
        fn['CONSERVATIVE'] = data['CONSERVATIVE'];
        fn['STANDARD'] = data['STANDARD'];
        fn['AGGRESSIVE'] = data['AGGRESSIVE'];  
        */

        var props;
        for(var thresholdName in data){
        	fn[thresholdName] = {};
        	props = data[thresholdName];
        	for(var i=0; i<props.length; i++){
        		fn[thresholdName][props[i].name] = props[i].val;
        	}
        }

      }, function(){

      });

      function getThresholdDefinitions() {
        var config = {
          url: (APP_ENV.baseUrl + "/hyperconverged/threshold"),
          method: "GET"/*,
          headers: {
            "contentType": "application/json"
          }*/
        };
        return appService.processRequest(config);
      };

    }])

})();
