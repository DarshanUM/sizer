(function() {
  "use strict";

  angular
    .module('hyperflex')
    .filter("trustUrl", ['$sce', function ($sce) {
        return function (videoUrl) {
            return $sce.trustAsResourceUrl(videoUrl);
        };
    }]);

  angular
    .module('hyperflex')
    .controller("HelpController", ["$scope", "nodeService", "$timeout", "HX_ANALYTICS_EVENTS", function($scope, nodeService, $timeout, HX_ANALYTICS_EVENTS ) {
      var vm = this;

      vm.trainingFilesList = null;
      vm.selectedtrainingFile = null;
      vm.helpContainerHeight = window.innerHeight -95; 


      vm.pathProp = 'filepath_url';
      var _pathProp = 'filepath_url';
      var _pdfContainer, _htmlContainer, _videoContainer, 
          _objectTag, _embedTag, _videoTag;


      function Init(){

        _pdfContainer = $("#pdf-container");
        _videoContainer = $("#video-container");
        _htmlContainer = $("#html-container");

        _objectTag = _pdfContainer.find("object");
        _embedTag = _pdfContainer.find("embed");
        _videoTag = _videoContainer.find("video");

        vm.pdfContainerHeight = $(window).height() - _objectTag.offset().top - 10;

        _objectTag.get(0).addEventListener("load", function(a, b, c){
          console.log(" loaded ", a, b, c)
        });

        _objectTag.get(0).addEventListener("readystatechange", function(a, b, c){
          console.log(" onreadystatechange ", a, b, c)
        });



        hideElem(_pdfContainer);
        hideElem(_videoContainer);
        hideElem(_htmlContainer);

        if(vm.trainingFilesList){
          vm.selectedtrainingFile = vm.trainingFilesList[0];
          loadTrainingFile();
        }else{
          nodeService.getTrainingsVideosList().then(function(data){
            vm.trainingFilesList = data;
            vm.selectedtrainingFile = vm.trainingFilesList[0];
            loadTrainingFile();
          })
        }        
      }

      function loadTrainingFile(){
        switch(vm.selectedtrainingFile.type){
          case "document":
            loadPDF(); break;
          case "video":
            loadVideo(); break;
          case "html":
            loadHTML(); break;
        }
      }

      function showElem(elem){
        elem.get(0).style.display = "block";
      }

      function hideElem(elem){
        elem.get(0).style.display = "none";
      }

      function loadVideo(){
        hideElem(_pdfContainer);
        hideElem(_htmlContainer);


        _videoTag.attr("src", vm.selectedtrainingFile[ _pathProp ]);
        _videoTag.get(0).play();
        showElem(_videoContainer);

        // Google analytics :: Tracking the number of times a video play is requested 
        ga('send', 'event', {
          eventCategory: HX_ANALYTICS_EVENTS.CATEGORY.TRAININGS.UI_LABEL,
          eventAction: ( 'VIDEO :: ' + vm.selectedtrainingFile.name ),
          eventLabel: vm.selectedtrainingFile.name  ,
          transport: 'beacon'
        });
      }

      function loadHTML(){
        _videoTag.get(0).pause();
        hideElem(_videoContainer);
        hideElem(_pdfContainer);        
        
        showElem(_htmlContainer);

        // Google analytics :: Tracking the number of times a video play is requested 
        ga('send', 'event', {
          eventCategory: HX_ANALYTICS_EVENTS.CATEGORY.TRAININGS.UI_LABEL,
          eventAction: ( 'HTML :: ' + vm.selectedtrainingFile.name ),
          eventLabel: vm.selectedtrainingFile.name  ,
          transport: 'beacon'
        });

      }

      function loadPDF(){
        _videoTag.get(0).pause();
        hideElem(_videoContainer);
        hideElem(_htmlContainer);   
        showElem(_pdfContainer);
        _objectTag.attr("data", vm.selectedtrainingFile[_pathProp]);     
        
        

        // Google analytics :: Tracking the number of times a video play is requested 
        ga('send', 'event', {
          eventCategory: HX_ANALYTICS_EVENTS.CATEGORY.TRAININGS.UI_LABEL,
          eventAction: ( 'PDF :: ' + vm.selectedtrainingFile.name ),
          eventLabel: vm.selectedtrainingFile.name  ,
          transport: 'beacon'
        });
      }

      vm.selectTrainingFile = function(trainingsVideo){
        if(vm.selectedtrainingFile !== trainingsVideo){
          vm.selectedtrainingFile = trainingsVideo;        
          loadTrainingFile(vm.selectedtrainingFile);  
        }
        
      };

      $scope.$on('$viewContentLoaded', function(event, viewConfig) {
        $timeout(Init, 100);
      });

    }]);

})();
