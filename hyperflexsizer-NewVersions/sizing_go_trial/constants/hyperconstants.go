package constants

// capacity attributes to be used for sizing
var CAP_LIST = [5]string{CPU, RAM, HDD, SSD, VRAM}
var WL_CAP_LIST = [6]string{CPU, RAM, HDD, SSD, IOPS, VRAM}

// var CAP_LIST_CONF = [5]string{CPU, RAM, HDD, SSD, VRAM}
var STAT_LIST = WL_CAP_LIST
var STAT_UNIT_LIST = []string{"CPU", "RAM", "Storage Capacity", "Cache", "Storage IOPS", "GPU Users"}
var STAT_UNITS = []string{"vCPUs", "GiB", "GB", "GB", "K IOPS", "Users"}
var MODEL_DETAILS_LIST = CAP_LIST

//Hercules IO/s performance increase in percentage
var HERCULES_IOPS = map[string]float64{
	OLAP:          16,
	OOLAP:         16,
	EXCHANGE_32KB: 12,
	EXCHANGE_16KB: 15,
	VDI_HOME:      13,
	OLTP:          8,
	OOLTP:         8,
	VSI:           8,
	ROBO:          8,
	ROBO_BACKUP:   8,
	EXCHANGE_64KB: 16,
	VDI:           15,
	RDSH:          15,
	RDSH_HOME:     13,
	VDI_INFRA:     0,
	SPLUNK:        0,
	EPIC:          0,
	VEEAM:         0,
	RAW:           0,
	CONTAINER:     8,
	AIML:          0,
	ANTHOS:        0,
}

// HX Boost IO/s performance increase in percentage
var HX_BOOST_IOPS = map[string]float64{
	OLAP:          10,
	OOLAP:         10,
	EXCHANGE_32KB: 10,
	EXCHANGE_16KB: 10,
	VDI_HOME:      10,
	OLTP:          25,
	OOLTP:         25,
	VSI:           25,
	ROBO:          10,
	ROBO_BACKUP:   10,
	EXCHANGE_64KB: 10,
	VDI:           10,
	RDSH:          10,
	RDSH_HOME:     10,
	VDI_INFRA:     10,
	SPLUNK:        10,
	EPIC:          10,
	VEEAM:         10,
	RAW:           10,
	CONTAINER:     25,
	AIML:          10,
	ANTHOS:        0,
}

const (
	// NODE_SUB_TYPE
	HYPER            = "hyperconverged"
	ALL_FLASH        = "all-flash"
	ALL_FLASH_7_6TB  = "all-flash-7.6tb" // This subtype for 7.6TB as it has different static overhead
	COMPUTE          = "compute"
	ROBO_NODE        = "robo"
	AF_ROBO_NODE     = "robo_allflash"
	ROBO_TWO_NODE    = "robo_two_node"
	AF_ROBO_TWO_NODE = "robo_allflash_two_node"
	ROBO_240         = "robo_240"
	ROBO_AF_240      = "robo_af_240"
	EPIC_NODE        = "epic"
	VEEAM_NODE       = "veeam"
	LFF_12TB_NODE    = "lff_12tb"
	ALLNVME_NODE     = "allnvme"
	ALLNVME_NODE_8TB = "allnvme_8tb"
	AIML_NODE        = "aiml"
	LFF_NODE         = "lff"

	//threshold
	ALL_FLASH_HDD = "ALL_FLASH_HDD"
	LFF_HDD       = "LFF_HDD"

	BUNDLE_ONLY    = "bundle"
	CTO_ONLY       = "cto"
	BUNDLE_AND_CTO = "ALL"

	MOD_10G       = "10G"
	SINGLE_SWITCH = "SINGLE"
	DUAL_SWITCH   = "DUAL"

	//  CLUSTER TYPE CONSTANTS
	NORMAL           = "normal"
	STRETCH          = "stretch"
	REPLICATION_FLAG = "remote_replication_enabled"
	REPLICATED       = "replicated"
	REPLICATION_AMT  = "replication_amt"
	ANY_CLUSTER      = "any"
	REPLICATION_TYPE = "replication_type"
	REMOTE           = "remote"

	//part attributes
	FREQUENCY       = "frequency"
	FilterTag       = "filter_tag"
	FRAME_BUFF      = "frame_buff"
	SPECLNT         = "speclnt"
	L3_CACHE        = "l3_cache"
	TDP             = "tdp"
	RAM_LIMIT       = "ram_limit"
	PCIE_REQ        = "pcie_req"
	CTO_PRICE       = "cto_price"
	BOM_NAME        = "bom_name"
	BOM_DESCR       = "bom_description"
	DESCRIPTION     = "description"
	BOM_ADD_MEM     = "bom_add_memory_name"
	HDD_TYPE        = "hdd_type"
	OUTPUT_CAPACITY = "output_capacity"

	//Disk cage
	DISK_CAGE         = "disk_cage"
	SMALL_FORM_FACTOR = "SFF"
	LARGE_FORM_FACTOR = "LFF"

	// Hercules configs
	DISABLED = "disabled"
	ENABLED  = "enabled"
	FORCED   = "forced"

	// WL JSON strings
	RAW                   = "RAW"
	RAW_FILE              = "RAW_FILE"
	EXCHANGE              = "EXCHANGE"
	VDI                   = "VDI"
	RDSH                  = "RDSH"
	VSI                   = "VSI"
	VM                    = "VM"
	DB                    = "DB"
	OLTP                  = "OLTP"
	OLAP                  = "OLAP"
	ROBO                  = "ROBO"
	ORACLE                = "ORACLE"
	OOLTP                 = "OOLTP"
	OOLAP                 = "OOLAP"
	AWR_FILE              = "AWR_FILE"
	CONTAINER             = "CONTAINER"
	AIML                  = "AIML"
	ANTHOS                = "ANTHOS"
	ROBO_BACKUP           = "ROBO_BACKUP"
	ROBO_BACKUP_SECONDARY = "ROBO_BACKUP_SECONDARY"
	INTERNAL_TYPE         = "internal_type"
	CLUSTER_TYPE          = "cluster_type"
	WL_CLUSTER_NAME       = "wl_cluster_name"
	IS_DIRTY              = "isDirty"
	IO_BLOCK_SIZE         = "io_block_size"
	IOPS_VALUE            = "iops_value"
	TAGGED_WL             = "tagged_wl"

	REPLICATION_FACTOR = "replication_factor"

	// Raw WL JSON strings
	RAW_OVERHEAD_PERCENTAGE = "overhead_percentage"
	CPU_ATTRIBUTE           = "cpu_attribute"
	CPU_CORES               = "cpu_cores"
	CPU_CLOCK               = "cpu_clock"
	CPU_MODEL               = "cpu_model"
	VCPUS                   = "vcpus"
	DISK_SIZE               = "disk_size"
	RAW_REPLICATION_FACTOR  = "replication_factor"
	RAW_WORKING_SET_SIZE    = "working_set"

	// VDI WL JSON strings
	VDI_USER_TYPE         = "profile_type"
	NUM_DT                = "num_desktops"
	VCPUS_PER_DT          = "vcpus_per_desktop"
	VCPUS_PER_CORE        = "vcpus_per_core"
	RAM_PER_DT            = "ram_per_desktop"
	RAM_PER_DT_UNIT       = "ram_per_desktop_unit"
	HDD_PER_DT            = "disk_per_desktop"
	HDD_PER_DT_UNIT       = "disk_per_desktop_unit"
	GOLD_IMG_SIZE         = "gold_image_size"
	GOLD_IMG_SIZE_UNIT    = "gold_image_size_unit"
	IOPS_PER_DT           = "avg_iops_per_desktop"
	USER_DATA_IOPS        = "user_iops"
	DT_PROV_TYPE          = "provisioning_type"
	VIEW_FULL             = "Persistent Desktops"
	VIEW_LINKED           = "Pooled Desktops"
	XEN_PVS               = "Xen PVS"
	XEN_MCS               = "Xen MCS"
	XEN_FULL              = "Xen Full Clones"
	DT_REPLICATION_FACTOR = "replication_factor"
	DT_REPLICATION_MULT   = "replication_mult"
	DT_WORKING_SET_SIZE   = "working_set"
	DT_INFLIGHT_DEDUPE    = "inflight_dedupe_factor"
	INFLIGHT_DATA         = "inflight_data_size"
	IMAGE_DEDUPE          = "image_dedupe_factor"
	DT_CLOCK_SPEED        = "clock_per_desktop"
	CONCURRENCY           = "concurrency"
	VIDEO_RAM             = "video_RAM"
	GPU_STATUS            = "gpu_users"
	DT_SNAPSHOTS          = "snapshots"
	VRAM                  = "VRAM"

	// Infrastructure keys
	VDI_INFRA = "VDI_INFRA"

	// EPIC WL keys
	EPIC               = "EPIC"
	RAM_PER_GUEST_UNIT = "ram_per_guest_unit"

	// Veeam WL keys
	VEEAM = "VEEAM"

	// Splunk WL keys
	SPLUNK = "SPLUNK"

	// Home directory keys
	VDI_HOME       = "VDI_HOME"
	RDSH_HOME      = "RDSH_HOME"
	VDI_DIRECTORY  = "vdi_directory"
	RDSH_DIRECTORY = "rdsh_directory"

	// VM WL JSON strings
	VM_PROF_TYPE          = "profile_type"
	NUM_VM                = "num_vms"
	VCPUS_PER_VM          = "vcpus_per_vm"
	RAM_PER_VM            = "ram_per_vm"
	RAM_PER_VM_UNIT       = "ram_per_vm_unit"
	HDD_PER_VM            = "disk_per_vm"
	HDD_PER_VM_UNIT       = "disk_per_vm_unit"
	IOPS_PER_VM           = "avg_iops_per_vm"
	VM_REPLICATION_FACTOR = "replication_factor"
	VM_REPLICATION_MULT   = "replication_mult"
	VM_WORKING_SET_SIZE   = "working_set"
	VM_BASE_IMG_SIZE      = "base_image_size"
	VM_BASE_IMG_SIZE_UNIT = "base_image_size_unit"
	VM_SNAPSHOTS          = "snapshots"

	// RDSH WL JSON strings
	OS_PER_VM         = "os_per_vm"
	OS_PER_VM_UNIT    = "os_per_vm_unit"
	TOTAL_USERS       = "total_users"
	SESSIONS_PER_VM   = "sessions_per_vm"
	CLOCK_PER_SESSION = "clock_per_session"
	HDD_PER_USER      = "hdd_per_user"
	HDD_PER_USER_UNIT = "hdd_per_user_unit"

	// DB WL JSON strings
	DB_TYPE               = "db_type"
	DB_SERVER_TYPE        = "profile_type"
	NUM_DB                = "num_db_instances"
	VCPUS_PER_DB          = "vcpus_per_db"
	RAM_PER_DB            = "ram_per_db"
	RAM_PER_DB_UNIT       = "ram_per_db_unit"
	DB_SIZE               = "db_size"
	DB_SIZE_UNIT          = "db_size_unit"
	LOG_SIZE              = "log_size"
	TEMPDB_SIZE           = "tempdb_size"
	INDEX_SIZE            = "index_size"
	HDD_PER_DB            = "disk_per_db"
	IOPS_PER_DB           = "avg_iops_per_db"
	MBPS_PER_DB           = "avg_mbps_per_db"
	DB_REPLICATION_FACTOR = "replication_factor"
	DB_REPLICATION_MULT   = "replication_mult"
	META_DATA             = "metadata_size"

	// EXCHANGE WL JSON strings
	EXCHANGE_32KB = "EXCHANGE_32KB"
	EXCHANGE_16KB = "EXCHANGE_16KB"
	EXCHANGE_64KB = "EXCHANGE_64KB"

	// CONTAINER WL JSON strings
	NUM_CONTAINERS         = "num_containers"
	BASE_IMG_SIZE          = "base_image_size"
	BASE_IMG_SIZE_UNIT     = "base_image_size_unit"
	WORKING_SET_SIZE       = "working_set"
	IOPS_PER_CONTAINER     = "iops_per_container"
	VCPUS_PER_CONTAINER    = "vcpus_per_container"
	HDD_PER_CONTAINER      = "disk_per_container"
	RAM_PER_CONTAINER      = "ram_per_container"
	RAM_PER_CONTAINER_UNIT = "ram_per_container_unit"
	HDD_PER_CONTAINER_UNIT = "disk_per_container_unit"
	REPLICATION_MULT       = "replication_mult"

	// AI/ML WL JSON strings
	NUM_DATA_SCIENTISTS = "num_data_scientists"
	IOPS_PER_DS         = "iops_per_ds"
	VCPUS_PER_DS        = "vcpus_per_ds"
	RAM_PER_DS          = "ram_per_ds"
	RAM_PER_DS_UNIT     = "ram_per_ds_unit"
	GPU_PER_DS          = "gpu_per_ds"
	HDD_PER_DS          = "disk_per_ds"
	HDD_PER_DS_UNIT     = "disk_per_ds_unit"
	ENABLESTORAGE       = "enablestorage"

	// extra HDD compression provided by hercules configs
	HERCULES_COMP = 10

	//slots
	CPUSLOT  = "cpu_socket_count"
	RAMSLOT  = "ram_slots"
	HDDSLOT  = "hdd_slots"
	SSDSLOT  = "ssd_slots"
	PCIESLOT = "pcie_slots"

	//parts name
	CUSTOM       = "[CUSTOM]"
	CUSTOM_6SLOT = "[CUSTOM_6SLOT]"

	//RAM constants
	MIN_MEMORY = 10000

	//storage protocol
	NFS = "NFS"

	REF_IOPS_CPU = "8276 [Cascade]"

	//HYPERVISOR PRICE
	ESX_SOFTWARE_PRICE     = 14000
	HYPER_V_SOFTWARE_PRICE = 288
)
