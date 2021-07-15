(function() {
  "use strict";

  angular
    .module('hyperflex')
    .filter("scenariofilter", function() {
      return function(scenariosList, filterText) {
        var scenario, filteredList = [];
        for(var i=0; i<scenariosList.length; i++){
          scenario = scenariosList[i];
          if(scenario.name.indexOf(filterText) !== -1 || 
              (scenario.settings_json[0].account && scenario.settings_json[0].account.indexOf(filterText) !== -1) ){
            filteredList.push(scenario);
          }
        }
        return filteredList;
      }
    })

}());
