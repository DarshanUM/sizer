(function() {
  'use strict';

  var request_array = [
    "SCENARIO_ADD", "SCENARIO_EDIT", "SCENARIO_GET", "SCENARIO_DELETE", "SCENARIO_QUERY",
    "SCENARIO_CLONE",
    "NODE_ADD", "NODE_EDIT", "NODE_GET", "NODE_DELETE", "NODE_QUERY",
    "LOGIN",
    "USERDATA"
  ];

  // this is to create named constants
  function getRequestObject(){
    var reqTypes = {};
    for(var i=0; i<request_array.length; i++){
      reqTypes[ request_array[i] ] = (i+1);
    }
    return reqTypes;
  }

  angular
    .module('hyperflex')
    .constant("REQUEST_TYPE", getRequestObject());

})();
