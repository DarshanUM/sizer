(function() {
  "use strict";

  angular
    .module('hyperflex')
    .filter("currency", function() {
      return function(numericInput, currencySymbol) {
        var quantityChar = "";
        currencySymbol = currencySymbol || "$";

        if( isNaN(numericInput) ){
            return (currencySymbol + 0 + quantityChar);
        }

        var quantityChar = "";
        if (numericInput > 999999) {
          numericInput = (numericInput / 1000000);
          quantityChar = "M";
        } else if (numericInput > 999) {
          numericInput = (numericInput / 1000);
          quantityChar = "K";
        }

        numericInput = numericInput.toFixed(1);

        return  (currencySymbol + numericInput + quantityChar);

      }
    })

}());
