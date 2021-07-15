(function() {
  "use strict";

  angular
    .module('hyperflex')
    .filter("kilo", function() {
      return function(numericInput) {
        var quantityChar = "";

        if( isNaN(numericInput) ){
            return (0 + quantityChar);
        }

        if (numericInput > 999) {
          numericInput = (numericInput / 1000);
          quantityChar = "K";
        }

        numericInput = numericInput.toFixed(1);

        return  (numericInput + quantityChar);

      }
    })

}());
