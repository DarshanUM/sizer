  (function() {
  "use strict";

  var CONVERSION_FACTOR = {
    gb_to_gb: 1,
    gb_to_gib: 0.931323,
    gb_to_tb: 0.001,
    gb_to_tib: 0.000909495,
    gib_to_tb: 0.00107374,
    tib_to_tb: 1.09951,
    tb_to_tb: 1
  };

  angular
    .module('hyperflex')
    .filter("storageUnit", function() {
      return function(numericInput, toUnit, fromUnit) {
        var conversionFactor;
        var propName;
        fromUnit = fromUnit ? fromUnit.toLowerCase() : 'gb';
        toUnit = toUnit.toLowerCase();
        propName = fromUnit + '_to_' + toUnit;
        conversionFactor = CONVERSION_FACTOR[ propName ];

        if( isNaN(numericInput) ){
            return 0
        }

        var value = (numericInput * conversionFactor);
        return  parseFloat(value.toFixed(2));
      }
    })

}());
