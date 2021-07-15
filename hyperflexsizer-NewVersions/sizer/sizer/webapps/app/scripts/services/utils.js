(function() {
  "use strict";

  angular
    .module('hyperflex')
    .service("utilService", function($http, $q, $state, $sessionStorage) {
      var fn = this;

      fn.getItemByPropVal = function(list, propName, value){
        list = list || [];
        for(var i=0; i<list.length; i++){
          if( list[i][propName] === value ){
            return list[i];
          }
        }
        return null;
      };

      fn.deleteItemByPropVal = function(list, propName, value){
        list = list || [];
        for(var i=0; i<list.length; i++){
          if( list[i][propName] === value ){
            list.splice(i, 1);
          }
        }
      };

      fn.updateItemByProp = function(list, propName, item){
        list = list || [];
        for(var i=0; i<list.length; i++){
          if( list[i][propName] === item[propName] ){
            list[i] = item;
            break;
          }
        }
        return list;
      };

      fn.getItemsNotContainsText = function(list, searchStr){
        list = list || [];
        var filteredList = [];
        for(var i=0; i<list.length; i++){
          if(list[i].indexOf(searchStr) == -1){
            filteredList.push(list[i]);
          }
        }
        return filteredList;
      };

      fn.doesListHasItem = function(srcList, searchItem){
        return srcList.indexOf(searchItem)!==-1;
      };

      fn.doesListNotHasItem = function(srcList, searchItem){
        return srcList.indexOf(searchItem)===-1;
      };

      fn.hasAllItemsInList = function(srcList, includesList){
        for(var i=0; i<includesList.length; i++){
          if( srcList.indexOf( includesList[i] ) === -1)
            return false;
        }
        return true;
      };

      fn.hasNoItemsInList = function(srcList, excludesList){
        for(var i=0; i<excludesList.length; i++){
          if( srcList.indexOf( excludesList[i] ) !== -1)
            return false;
        }
        return true;
      };

      fn.hasSomeItemsInList = function(srcList, includesList){
        if(includesList.length==0) 
          return true;
        
        for(var i=0; i<includesList.length; i++){
          if( srcList.indexOf( includesList[i] ) !== -1)
            return true;
        }
        return false;
      };

      fn.getClone = function(srcObject){
        return  JSON.parse( JSON.stringify(srcObject) );// Object.assign({}, srcObject);
      };

      fn.filteredList = function(srcList, filterFn){
        if(!srcList || !srcList.length) return srcList;
        if(typeof filterFn !== "function") return srcList;

        var list = [].concat(srcList);
        var filteredList = [];
        for(var i=0; i<list.length; i++){
          if( filterFn(list[i]) ){
            filteredList.push( list[i] );
          }
        }

        return filteredList;
      }

      fn.deleteItemByVal = function(srcList, val) {
        srcList = srcList || [];
        var index = srcList.indexOf(val);
        if(index !== -1){
          var list = [].concat(srcList);
          list.splice(index, 1);
          return list;
        }else {
          return srcList;
        }
      }

      fn.startsWith = function(srcStr, searchStr) {
        srcStr = srcStr || '';
        searchStr = searchStr || '';
        return srcStr.substring(0, searchStr.length) === searchStr;
      }

      fn.endsWith = function(srcStr, searchStr) {
        srcStr = srcStr || '';
        searchStr = searchStr || '';
        return srcStr.substring(srcStr.length-searchStr.length) === searchStr;
      }

      fn.hasText = function(srcStr, searchStr) {
        return srcStr.indexOf(searchStr)!==-1;
      }

    }); //utilService

})();
