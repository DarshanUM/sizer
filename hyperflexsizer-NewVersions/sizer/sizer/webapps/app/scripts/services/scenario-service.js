(function() {
  'use strict';
  
  angular
    .module('hyperflex')
    .factory('scenarioService', ['$resource', 'APP_ENV', 'REQUEST_TYPE', function($resource, APP_ENV, REQUEST_TYPE) {

      // return $resource('http://jsonplaceholder.typicode.com/users/:id', {id:'@id'}, {
      return $resource(APP_ENV.baseUrl + '/hyperconverged/scenarios/:id', { id: '@id' }, {
        get: {
          method: 'GET',
          progressbar: {id:'scenario-request-get'},
          requestId: REQUEST_TYPE.SCENARIO_GET
        },
        query: {
          method: 'GET',
          isArray: true,
          progressbar: {id:'scenario-request-query'},
          requestId: REQUEST_TYPE.SCENARIO_QUERY
        },
        save: {
          method: 'POST',
          progressbar: {id:'scenario-request-save'},
          requestId: REQUEST_TYPE.SCENARIO_SAVE
        },
        delete: {
          method: 'DELETE',
          progressbar: {id:'scenario-request-delete'},
          requestId: REQUEST_TYPE.SCENARIO_DELETE
        },
        update: {
          method: 'PUT',
          progressbar: {id:'scenario-request-update'},
          requestId: REQUEST_TYPE.SCENARIO_UPDATE
        },
        patch: {
          method: 'PATCH',
          progressbar: {id:'scenario-request-patch'},
          requestId: REQUEST_TYPE.SCENARIO_EDIT 
        }
      });

    }])

})();
