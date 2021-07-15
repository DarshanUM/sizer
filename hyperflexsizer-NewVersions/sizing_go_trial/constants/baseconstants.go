package constants

const (
	// capacity attributes to be used for sizing
	// CAP_LIST = list()
	// CAP_LIST_CONF = list()
	// STAT_LIST = list()
	// MODEL_DETAILS_LIST = list()

	MSG_101 = "Please provide the authentication token"
	MSG_102 = "Unauthorized User"

	// Path to Log Files
	LOGFILE_SIZE_MB   = 1
	LOGGING_BACKCOUNT = 5

	// CRITICAL
	// ERROR
	// WARNING
	// INFO
	// DEBUG
	// NOTSET

	// part JSON strings
	PARTS        = "parts"
	PART_ID      = "name"
	CAPACITY     = "capacity"
	MAX_SESSION  = "max_session"
	PART_PRICE   = "unit_price"
	AVAILABILITY = "availability"

	// node JSON strings
	NODE_DESCR      = "node_description"
	NODE_HEAD       = "node_heading"
	MODELS          = "models"
	VENDOR          = "vendor"
	MODEL           = "name"
	NODE_TYPE       = "type"
	FIXED           = "fixed"
	CONF            = "configurable"
	BUNDLE          = "bundle"
	CTO             = "cto"
	BASE_PRICE      = "base_price"
	RACK_SPACE      = "rack_space"
	POWER           = "power"
	BTU             = "btu"
	NODE_BASE_PRICE = "node_base_price"

	// result JSON strings
	DISPLAY_NAME             = "display_name"
	TITLE                    = "title"
	INFORMATION              = "information"
	STATS                    = "stats"
	TAG_NAME                 = "tag_name"
	TAG_VAL                  = "tag_val"
	HIGHLIGHT                = "highlight"
	WORKLOAD_VAL             = "workload_val"
	NODE_VAL                 = "node_val"
	TOTAL_NODE_VAL           = "total_node_val"
	UTILIZATION              = "utilization"
	PRICING                  = "pricing"
	SERVER                   = "server"
	NETWORK                  = "network"
	SOFTWARE                 = "software"
	VMWARE                   = "vmware"
	TOTAL                    = "total"
	FACILITIES               = "facilities"
	SUPPORT                  = "support"
	MAINTAINANCE             = "maintainance"
	CAPEX                    = "capex"
	TOTAL_PRICE              = "total_price"
	HYPERVISOR               = "hypervisor"
	RESULT_NAME              = "result_name"
	BEST_PRACTICE            = "best_practice"
	NODE_VAL_BINARYBYTE      = "node_val_binarybyte"
	BEST_PRACTICE_BINARYBYTE = "best_practice_binarybyte"

	NUM_NODE      = "num_nodes"
	SIZING_STATS  = "sizing_stats"
	WL_TOTAL      = "workload_total"
	NODE_TOTAL    = "node_total"
	TCO           = "TCO"
	OPEX_PER_YEAR = "opex_per_year"
	MODEL_DETAILS = "model_details"

	// WL JSON strings
	WORKLOADS = "workloads"
	WL_TYPE   = "wl_type"
	WL_NAME   = "wl_name"

	// Sizer Component
	CPU  = "CPU"
	RAM  = "RAM"
	HDD  = "HDD"
	SSD  = "SSD"
	IOPS = "IOPS"
	GPU  = "GPU"

	PARTS_LIST = "parts_list"
	MAX_NODE   = "max_node"

	// Node Attributes for Cisco related properties
	STATIC_OVERHEAD   = "static_overhead"
	IOPS_CONV_FAC     = "iops_conversion_factor"
	MIN_IOPS_CONV_FAC = "min_iops_conv_fac"
	SUBTYPE           = "subtype"
	HETEROGENOUS      = "heterogenous"
	SLOTS             = "slots"
	SIZE              = "size"

	// node json base settings
	// CPU
	CPU_CNT       = "cpu_socket_count"
	CORES_PER_CPU = "cores_per_cpu"
	// CLOCK
	CLOCK_SPEED    = "frequency"
	BASE_CPU_CLOCK = "base_frequency"
	// RAM
	RAM_SLOTS = "ram_slots"
	MIN_SLOTS = "min_slots"
	RAM_SIZE  = "ram_size"
	// HDD
	HDD_SLOTS     = "hdd_slots"
	HDD_SIZE      = "hdd_size"
	HDD_SIZE_UNIT = "hdd_size_unit"
	RAM_SIZE_UNIT = "ram_size_unit"
	MAX_HDD_SLOTS = "max_hdd_slots"
	MIN_HDD_SLOTS = "min_hdd_slots"
	MAX_CLUSTER   = "max_cluster"
	// SSD
	SSD_SLOTS = "ssd_slots"
	SSD_SIZE  = "ssd_size"
	// ROI calculation Input for Sizer
	SIZER_GROSS_MARGIN = 65

	SIZER_SERVER                       = "server"
	SIZER_NETWORK                      = "network"
	SIZER_SOFTWARE                     = "software"
	SIZER_VMWARE                       = "vmware"
	SIZER_TOTAL_CAPEX                  = "total"
	SIZER_SOFTWARE_MARGIN              = 15
	SIZER_PRICE_PER_PORT               = 17114 / 36.0
	SIZER_VM_WARE_PER_3_HOST           = 4995
	SIZER_VMWARE_HOST_LICENSE          = 3
	SIZER_VM_WARE_ADD_SUPPORT_PER_YEAR = 1249

	PRICE = "price"
)
