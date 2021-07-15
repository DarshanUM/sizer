angular.module('hyperflex-env', [])

.constant('APP_ENV', {name:'development',baseUrl:'http://10.11.100.49:8000',workload_url:{default_values:'data/workload-default-values.json',epic_hyperspace:'data/workload-fields-epic_hyperspace.json',vdi:'data/workload-fields-vdi.json',vdi_infra:'data/workload-fields-vdi-infra.json',vsi:'data/workload-fields-vsi.json',rdsh:'data/workload-rdsh.json',raw:'data/workload-fields-raw.json',db:'data/workload-fields-db.json',robo:'data/workload-fields-robo.json',oracle:'data/workload-fields-oracle.json',exchange:'data/workload-fields-exchange.json',splunk:'data/workload-fields-splunk.json',veeam:'data/workload-fields-veeam.json',bulk:'data/workload-fields-bulk.json'}})

.value('debug', false)

;