
CREATE_ESTIMATE_PAYLOAD = {
  "ProcessQuote": {
    "DataArea": {
      "Quote": [
        {
          "QuoteHeader": {
            "Extension": [
              {
                "ID": [
                  {
                    "value": "",
                    "typeCode": "PriceListShortName"
                  },
                  {
                    "value": "Resale",
                    "typeCode": "IntendedUseCode"
                  }
                ],
                "ValueText": [
                  {
                    "value": "",
                    "typeCode": "Estimate Name"
                  }
                ]
              }
            ],
            "Status": [
              {
                "Code": {
                  "value": "VALID",
                  "typeCode": "EstimateStatus"
                }
              }
            ],

            "EffectiveTimePeriod": {
              "EndDateTime": "2013-08-04T07:00:00Z"
            },

            "Message": [
            {
                "Note": [
                {
                   "value": "This estimate was created via upload from the HX Sizer"
                }
                ]
            }
            ]

          },

          "QuoteLine": [
            {
              "LineNumberID": {
                "value": "1"
              },

              "Note": [
                {
                   "value": ""
                }
                ],

              "Item": {

                "ID": {
                  "value": "UCS-FI-6332",
                  "schemeAgencyID": "Cisco",
                  "typeCode": "PartNumber"
                },
                "Description": [
                  {
                    "value": ""
                  }
                ],

				"Extension": [
                  {
                    "Quantity": [
                      {
                        "value": 1,
                        "unitCode": "each"
                      }
                    ]
                  }
                ],

                "Classification": [
                  {
                    "Extension": [
                      {
                        "ValueText": [
                          {
                            "value": "",
                            "typeCode": "ItemType"
                          }
                        ]
                      }
                    ],
                    "UNSPSCCode": {
                      "value": "43222609"
                    }
                  }
                ],
                "Specification": [
                  {
                    "Property": [
                      {
                        "Extension": [
                          {
                            "ValueText": [
                              {
                                "value": "UCSC-MODEL:PROCESSOR_CLASS:0:RECOM_PROC_CAT|HX-CPU-I8276",
                                "typeCode": "ConfigurationPath"
                              },
                              {
                                "value": "C32111387D",
                                "typeCode": "ProductConfigurationReference"
                              },
                              {
                                "value": "USER",
                                "typeCode": "ConfigurationSelectCode"
                              },
                              {
                                "value": "",
                                "typeCode": "BundleIndicator"
                              },
                              {
                                "value": "INVALID",
                                "typeCode": "VerifiedConfigurationIndicator"
                              },
                              {
                                "value": "",
                                "typeCode": "ValidationDateTime"
                              }
                            ]
                          }
                        ],
                        "ParentID": {
                          "value": "0"
                        },
                        "NameValue": {
                          "value": "1.0",
                          "name": "CCWLineNumber"
                        },
                        "EffectiveTimePeriod": {
                          "Duration": "P0Y0M35DT0H0M"
                        }
                      }
                    ]
                  }
                ]
              },
              "UnitPrice": {
                "Extension": [
                  {
                    "Amount": [
                      {
                        "value": 1,
                        "currencyCode": "USD",
                        "typeCode": "UnitNetPrice"
                      }
                    ]
                  }
                ],
                "UnitAmount": {
                  "value": 1,
                  "currencyCode": "USD"
                }
              },
              "ExtendedAmount": {
                "value": 1,
                "currencyCode": "USD"
              },
              "TotalAmount": {
                "value": 1,
                "currencyCode": "USD"
              },
              "AmountDiscount": {
                "Percentage": {
                  "value": 0
                }
              },
              "Party": [
                {
                  "role": "Install Site",
                  "Location": [
                    {
                      "Address": [
                        {
                          "CountryCode": {
                            "value": "US"
                          }
                        }
                      ]
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    },
    "ApplicationArea": {
      "Sender": {
        "LogicalID": {
          "value": "847291911"
        },
        "ComponentID": {
          "value": "B2B-3.0"
        },
        "ReferenceID": {
          "value": "Tech Data"
        }
      },

      "CreationDateTime": "2020-01-07T21:00:59",
      "BODID": {
        "value": "10-2056548"
      }
    }
  }
}
