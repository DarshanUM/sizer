(function() {
  'use strict';

  var eventsConfig = {
    CATEGORY: {
      DOWNLOADS: {
        UI_LABEL: 'Downloads',
        ACTIONS: {
          HX_PROFILER_OVA: 'HX Profiler OVA',
          HX_BENCH_OVA: 'HX Bench OVA',
          HX_SIZING_REPORT: 'HX Sizing Report',
          HX_FIXED_CONFIG_SIZING_REPORT: 'HX Fixed Config Sizing Report',
          HX_BOM_REPORT: 'HX BOM Report'
        },
        LABELS: {
          HX_PROFILER_OVA: 'HX Profiler OVA',
          HX_BENCH_OVA: 'HX Bench OVA',
          HX_SIZING_REPORT: 'HX Sizing Report',
          HX_FIXED_CONFIG_SIZING_REPORT: 'HX Fixed Config Sizing Report',
          HX_BOM_REPORT: 'HX BOM Report'
        }
      },
      SHARING_SCENARIO: {
        UI_LABEL: 'Sharing Scenario',
        ACTIONS: {
          SHARING_SCENARIO: 'Sharing Scenario'
        },
        LABELS: {
          SHARING_SCENARIO: 'Sharing Scenario'
        }
      },
      TRAININGS: {
        UI_LABEL: 'Trainings',
        ACTIONS: {
          SIZER_WHATS_NEW: "HX Sizer - What's New",
          SIZER_GETTING_STARTED: 'HX Sizer - Getting Started',
          SIZER_OVERVIEW : 'HX Sizer - Overview',
          SIZER_WORKLOADS : 'HX Sizer - Workloads',
          PROFILER_GETTING_STARTED : 'HX Profiler - Getting Started',
          PROFILER_OVERVIEW : 'HX Profiler - Overview'
        },
        LABELS: {
          SIZER_WHATS_NEW: "HX Sizer - What's New",
          SIZER_GETTING_STARTED: 'HX Sizer - Getting Started',
          SIZER_OVERVIEW : 'HX Sizer - Overview',
          SIZER_WORKLOADS : 'HX Sizer - Workloads',
          PROFILER_GETTING_STARTED : 'HX Profiler - Getting Started',
          PROFILER_OVERVIEW : 'HX Profiler - Overview',
        }
      }
    }

  };

  angular
    .module('hyperflex')
    .constant("HX_ANALYTICS_EVENTS", eventsConfig);

})();
