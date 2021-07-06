from base_sizer.solver.attrib import BaseConstants
from collections import OrderedDict

class HyperConstants:

    # Settings JSON Fields
    FAULT_TOLERANCE = 'fault_tolerance'
    THRESHOLD = 'threshold'
    HERCULES_CONF = 'hercules_conf'
    HX_BOOST_CONF = 'hx_boost_conf'

    # capacity attributes
    CLOCK = 'CLOCK'
    ALL_FLASH_HDD = 'ALL_FLASH_HDD'
    DISK = 'Total Disk'
    LFF_HDD = 'LFF_HDD'

    UNITS = "units"
    RATIO = "ratio"

    # To convert from GB to GiB, divide by 1.073741824.
    GB_TO_GIB_CONVERSION_FACTOR = 1.073741824

    # To convert from GB to GiB or TB to TiB, multiply
    GB_TO_GIB_CONVERSION = 0.931322575
    TB_TO_TIB_CONVERSION = 0.909494702

    GIB_TO_GB_CONVERSION = 1.073741824
    TIB_TO_TB_CONVERSION = 1.099511628

    # capacity attributes to be used for sizing
    CAP_LIST = [BaseConstants.CPU, BaseConstants.RAM, BaseConstants.HDD, BaseConstants.SSD, BaseConstants.VRAM]
    WL_CAP_LIST = [BaseConstants.CPU, BaseConstants.RAM, BaseConstants.HDD, BaseConstants.SSD, BaseConstants.IOPS,
                   BaseConstants.VRAM]
    CAP_LIST_CONF = [BaseConstants.CPU, BaseConstants.RAM, BaseConstants.HDD, BaseConstants.SSD, BaseConstants.VRAM]
    STAT_LIST = WL_CAP_LIST
    STAT_UNIT_LIST = ["CPU",  "RAM", "Storage Capacity", "Cache", "Storage IOPS", "GPU Users"]
    STAT_UNITS = ["vCPUs", "GiB", "GB", "GB", "K IOPS", "Users"]
    MODEL_DETAILS_LIST = CAP_LIST

    # node JSON strings
    TYPE = 'type'

    CPU_OPT = 'cpu_options'
    CPU_PART = 'cpu_part'

    CPU_PRICE = 'cpu_price'
    CPU_DESCR = 'cpu_description'

    TOTAL_RAM = 'total_ram_size'
    RAM_OPT = 'ram_options'
    RAM_PART = 'ram_part'
    RAM_PRICE = 'ram_price'
    RAM_DESCR = 'ram_description'

    HDD_OPT = 'hdd_options'
    HDD_PRICE = 'hdd_price'
    HDD_DESCR = 'hdd_description'
    HDD_TYPE = 'hdd_type'
    CUSTOM = 'custom'

    SSD_FULL_SIZE = 'ssd_full'
    SSD_OUTPUT_CAPACITY = 'ssd_output_capacity'
    OUTPUT_CAPACITY = 'output_capacity'
    SSD_SIZE_UNIT = "ssd_size_unit"
    SSD_OPT = 'ssd_options'
    SSD_PART = 'ssd_part'
    SSD_PRICE = 'ssd_price'
    SSD_DESCR = 'ssd_description'
    DISK_CAP = 'disk_capacity'
    AVG_IOPS = 'iops'
    GPU_PART = 'gpu_part'
    GPU_SLOTS = 'gpu_slots'
    PCIE_SLOTS = 'pcie_slots'
    PCIE_REQ = 'pcie_req'
    FRAME_BUFF = 'frame_buff'
    GPU_CAP = 'gpu_capacity'
    GPU_OPT = 'gpu_options'
    GPU_DESCR = 'gpu_description'
    GPU_PRICE = 'gpu_price'
    IOPS_PER_DISK = 'iops_per_disk'
    RACK_SPACE = 'rack_space'
    HETEROGENOUS = 'heterogenous'

    # Scenario JSON Enumerated Types
    CONS_THRESHOLD = 0
    NORM_THRESHOLD = 1
    AGGR_THRESHOLD = 2

    # WL JSON strings
    RAW = 'RAW'
    RAW_FILE = 'RAW_FILE'
    EXCHANGE = 'EXCHANGE'
    VDI = 'VDI'
    RDSH = 'RDSH'
    VSI = 'VSI'
    VM = 'VM'
    DB = 'DB'
    OLTP = 'OLTP'
    OLAP = 'OLAP'
    ROBO = 'ROBO'
    ORACLE = 'ORACLE'
    OOLTP = 'OOLTP'
    OOLAP = 'OOLAP'
    AWR_FILE = 'AWR_FILE'
    CONTAINER = 'CONTAINER'
    AIML = 'AIML'
    ANTHOS = 'ANTHOS'
    ROBO_BACKUP = 'ROBO_BACKUP'
    ROBO_BACKUP_SECONDARY = 'ROBO_BACKUP_SECONDARY'
    INTERNAL_TYPE = 'internal_type'
    CLUSTER_TYPE = 'cluster_type'
    WL_CLUSTER_NAME = 'wl_cluster_name'
    IS_DIRTY = 'isDirty'
    IO_BLOCK_SIZE = 'io_block_size'
    IOPS_VALUE = 'iops_value'
    TAGGED_WL = 'tagged_wl'

    REPLICATION_FACTOR = 'replication_factor'

    # Raw WL JSON strings
    RAW_OVERHEAD_PERCENTAGE = 'overhead_percentage'
    CPU_ATTRIBUTE = 'cpu_attribute'
    CPU_CORES = 'cpu_cores'
    CPU_CLOCK = 'cpu_clock'
    CPU_MODEL = 'cpu_model'
    VCPUS = 'vcpus'
    DISK_SIZE = 'disk_size'
    RAW_REPLICATION_FACTOR = 'replication_factor'
    RAW_WORKING_SET_SIZE = 'working_set'

    # VDI WL JSON strings
    VDI_USER_TYPE = 'profile_type'
    NUM_DT = 'num_desktops'
    VCPUS_PER_DT = 'vcpus_per_desktop'
    VCPUS_PER_CORE = 'vcpus_per_core'
    RAM_PER_DT = 'ram_per_desktop'
    RAM_PER_DT_UNIT = 'ram_per_desktop_unit'
    HDD_PER_DT = 'disk_per_desktop'
    HDD_PER_DT_UNIT = 'disk_per_desktop_unit'
    GOLD_IMG_SIZE = 'gold_image_size'
    GOLD_IMG_SIZE_UNIT = 'gold_image_size_unit'
    IOPS_PER_DT = 'avg_iops_per_desktop'
    USER_DATA_IOPS = 'user_iops'
    DT_PROV_TYPE = 'provisioning_type'
    VIEW_FULL = 'Persistent Desktops'
    VIEW_LINKED = 'Pooled Desktops'
    XEN_PVS = 'Xen PVS'
    XEN_MCS = 'Xen MCS'
    XEN_FULL = 'Xen Full Clones'
    DT_REPLICATION_FACTOR = 'replication_factor'
    DT_REPLICATION_MULT = 'replication_mult'
    DT_WORKING_SET_SIZE = 'working_set'
    DT_INFLIGHT_DEDUPE = 'inflight_dedupe_factor'
    INFLIGHT_DATA = 'inflight_data_size'
    IMAGE_DEDUPE = 'image_dedupe_factor'
    DT_CLOCK_SPEED = 'clock_per_desktop'
    CONCURRENCY = 'concurrency'
    VIDEO_RAM = "video_RAM"
    VRAM = "VRAM"
    GPU_STATUS = "gpu_users"
    DT_SNAPSHOTS = 'snapshots'

    # Infrastructure keys
    VDI_INFRA = 'VDI_INFRA'

    # EPIC WL keys
    EPIC = 'EPIC'
    RAM_PER_GUEST_UNIT = 'ram_per_guest_unit'

    # Veeam WL keys
    VEEAM = 'VEEAM'

    # Splunk WL keys
    SPLUNK = 'SPLUNK'

    # Home directory keys
    VDI_HOME = 'VDI_HOME'
    RDSH_HOME = 'RDSH_HOME'
    VDI_DIRECTORY = 'vdi_directory'
    RDSH_DIRECTORY = 'rdsh_directory'

    # VM WL JSON strings
    VM_PROF_TYPE = 'profile_type'
    NUM_VM = 'num_vms'
    VCPUS_PER_VM = 'vcpus_per_vm'
    RAM_PER_VM = 'ram_per_vm'
    RAM_PER_VM_UNIT = 'ram_per_vm_unit'
    HDD_PER_VM = 'disk_per_vm'
    HDD_PER_VM_UNIT = 'disk_per_vm_unit'
    IOPS_PER_VM = 'avg_iops_per_vm'
    VM_REPLICATION_FACTOR = 'replication_factor'
    VM_REPLICATION_MULT = 'replication_mult'
    VM_WORKING_SET_SIZE = 'working_set'
    VM_BASE_IMG_SIZE = 'base_image_size'
    VM_BASE_IMG_SIZE_UNIT = 'base_image_size_unit'
    VM_SNAPSHOTS = 'snapshots'

    # RDSH WL JSON strings
    OS_PER_VM = 'os_per_vm'
    OS_PER_VM_UNIT = 'os_per_vm_unit'
    TOTAL_USERS = 'total_users'
    SESSIONS_PER_VM = 'sessions_per_vm'
    CLOCK_PER_SESSION = 'clock_per_session'
    HDD_PER_USER = 'hdd_per_user'
    HDD_PER_USER_UNIT = 'hdd_per_user_unit'

    # DB WL JSON strings
    DB_TYPE = 'db_type'
    DB_SERVER_TYPE = 'profile_type'
    NUM_DB = 'num_db_instances'
    VCPUS_PER_DB = 'vcpus_per_db'
    RAM_PER_DB = 'ram_per_db'
    RAM_PER_DB_UNIT = 'ram_per_db_unit'
    DB_SIZE = 'db_size'
    DB_SIZE_UNIT = 'db_size_unit'
    LOG_SIZE = 'log_size'
    TEMPDB_SIZE = 'tempdb_size'
    INDEX_SIZE = 'index_size'
    HDD_PER_DB = 'disk_per_db'
    IOPS_PER_DB = 'avg_iops_per_db'
    MBPS_PER_DB = 'avg_mbps_per_db'
    DB_REPLICATION_FACTOR = 'replication_factor'
    DB_REPLICATION_MULT = 'replication_mult'
    META_DATA = 'metadata_size'

    # EXCHANGE WL JSON strings
    EXCHANGE_32KB = 'EXCHANGE_32KB'
    EXCHANGE_16KB = 'EXCHANGE_16KB'
    EXCHANGE_64KB = 'EXCHANGE_64KB'

    # CONTAINER WL JSON strings
    NUM_CONTAINERS = 'num_containers'
    BASE_IMG_SIZE = 'base_image_size'
    BASE_IMG_SIZE_UNIT = 'base_image_size_unit'
    WORKING_SET_SIZE = 'working_set'
    IOPS_PER_CONTAINER = 'iops_per_container'
    VCPUS_PER_CONTAINER = 'vcpus_per_container'
    HDD_PER_CONTAINER = 'disk_per_container'
    RAM_PER_CONTAINER = 'ram_per_container'
    RAM_PER_CONTAINER_UNIT = 'ram_per_container_unit'
    HDD_PER_CONTAINER_UNIT = 'disk_per_container_unit'
    REPLICATION_MULT = 'replication_mult'

    # AI/ML WL JSON strings
    NUM_DATA_SCIENTISTS = 'num_data_scientists'
    IOPS_PER_DS = 'iops_per_ds'
    VCPUS_PER_DS = 'vcpus_per_ds'
    RAM_PER_DS = 'ram_per_ds'
    RAM_PER_DS_UNIT = 'ram_per_ds_unit'
    GPU_PER_DS = 'gpu_per_ds'
    HDD_PER_DS = 'disk_per_ds'
    HDD_PER_DS_UNIT = 'disk_per_ds_unit'
    ENABLESTORAGE = 'enablestorage'

    # Modular LAN string
    MOD_10G = '10G'
    SINGLE_SWITCH = 'SINGLE'
    DUAL_SWITCH = 'DUAL'
    MOD_LAN = 'mod_lan'

    # Calculation of bill of material.
    RESP = "resp"
    MODEL_DETAILS = "model_details"

    HDD_PART = "hdd_part"
    ID = "id"
    UNIT_PRICE = "unit_price"
    CTO_PRICE = "cto_price"
    part_list = ["ssd_part", "ram_part", "cpu_part", "hdd_part"]
    part_slot_list = ["ssd_slots", "ram_slots", "cpu_socket_count", "hdd_slots"]
    I_YEAR = "I_year"
    II_YEAR = "II_year"
    III_YEAR = "III_year"
    IV_YEAR = "IV_year"
    V_YEAR = "V_year"
    ROI = "ROI"
    Total_cost = "Total_cost"

    # Calculation for Private Cloud
    BLOCK_SIZE = 4
    GROSS_MARGIN = 35
    PRICE_PER_PORT = 17114 / 36.0
    VM_WARE_PER_3_HOST = 4995
    VM_WARE_ADD_SUPPORT_PER_YEAR = 1249
    CAPEX_PER_3_YEARS = "capex_per_3_years"
    OPEX_1_YEAR = "opex_1_year"
    HOURS_PER_YEAR = 8760
    NUM_YEARS = 3.0
    MS_WIN_VIRTUAL_PRICE = 80
    VMWARE_HOST_LICENSE = 3
    MAPLE_GROSS_MARGIN = 35
    SOFTWARE_MARGIN = 15
    SUPPORT_MARGIN = 10
    POWER_COST_PER_KWH = 11
    RACK_PER_MONTH = 50
    MAINTAINANCE_PRICE = 70
    MAINTAINANCE_HOUR = 3
    SERVER = "server"
    NETWORK = "network"
    SOFTWARE = "softwate"
    VMWARE = "vmware"
    SUPPORT = "support"
    FACILITIES = "facilities"
    MAINTAINANCE = "maintainance"
    PRIVATE_CLOUD = "PRIVATE CLOUD"
    # ROI CALCULATION CONSTANTS FOR SIZER
    SIZER_BLOCK_SIZE = 4

    SIZER_HOURS_PER_YEAR = 8760
    SIZER_NUM_YEARS = 3.0
    SIZER_MS_WIN_VIRTUAL_PRICE = 80

    SIZER_SUPPORT_MARGIN = 10
    SIZER_POWER_COST_PER_KWH = 0.11
    SIZER_RACK_PER_MONTH = 50
    SIZER_MAINTAINANCE_PRICE = 70
    SIZER_MAINTAINANCE_HOUR = 3

    SIZER_SUPPORT = "support"
    SIZER_FACILITIES = "facilities"
    SIZER_MAINTAINANCE = "maintainance"

    SIZER_TOTAL_OPEX = "total"
    # Maple parts
    FREQUENCY = "frequency"
    L3_CACHE = "l3_cache"
    TDP = "tdp"
    RAM_LIMIT = "ram_limit"
    SPECLNT = "speclnt"
    CORES_PER_CPU_PRESPECLNT = 'cores_per_cpu_prespeclnt'
    ENCRYPTION = "encryption"
    DESCRIPTION = "description"

    PRICE_PER_VDI = "price_per_vdi"
    PRICE_PER_VM = "price_per_vm"
    PRICE_PER_DB = "price_per_db"
    PRICE_PER_RAW = "price_per_raw"
    NUM_NODES = "num_nodes"

    # new , According to UI

    CAPEX_CPX = "Capex"
    OPEX = "Opex"
    OPEX_OPX = "Opex"
    SUMMARY = "Summary"
    TAG_VAL = "tag_val"
    TAG_NAME = "tag_name"
    HIGHLIGHT = "highlight"
    LABEL = "label"
    VAL = "value"
    UTIL_STATUS = 'status'

    PRICING_COMPUTE = "compute_pricing"
    INFORMATION_COMPUTE = "information_compute"
    COMPUTE_MODEL_DETAILS = "compute_model_details"
    FAULT_TOLERANCE_COUNT = "num_ft_nodes"
    POWER = "power"
    POWER_CONSUMPTION = "power_consumption"
    USABLE_VAL = "usable"
    USABLE_VAL_BINARYBYTE = "usable_binarybyte"
    BINARYBYTE_UNIT = 'binarybyte_unit'

    # Utilization Strings
    WL_UTILIZATION = "wl_util"
    OVERHEAD_UTILIZATION = "overhead_util"
    FT_UTIL = "ft_util"
    THRESHOLD_UTILIZATION = "threshold_util"
    FREE_UTIL = "free_util"
    SITE_FT_UTIL = "site_ft_util"

    # BOM Labels
    BOM_MODEL_DETAILS = "bom_details"
    BOM_NAME = "bom_name"
    BOM_DESCR = "bom_description"
    BOM_CPU_PART = "cpu_bom_name"
    BOM_CPU_DESCR = "cpu_bom_descr"
    BOM_RAM_PART = "ram_bom_name"
    BOM_RAM_DESCR = "ram_bom_descr"
    BOM_HDD_PART = "hdd_bom_name"
    BOM_HDD_DESCR = "hdd_bom_descr"
    BOM_SSD_PART = "ssd_bom_name"
    BOM_SSD_DESCR = "ssd_bom_descr"
    BOM_GPU_PART = "gpu_bom_name"
    BOM_GPU_DESCR = "gpu_bom_descr"
    BOM_PACKAGE_NAME = "bom_package_name"
    BOM_FI_PACKAGE_NAME = "bom_fi_package_name"
    BOM_RAID_NAME = "bom_raid_name"
    BOM_SYSTEM_DRIVE = "bom_system_drive"
    BOM_BOOT_DRIVE = "bom_boot_drive"
    FI_OPTIONS = "fi_options"
    M5_DISK_PACKAGE = "disk_package"
    BOM_ADD_MEM = "bom_add_memory_name"
    BOM_ADD_MEM_SLOTS = "bom_add_mem_slots"
    BOM_MIN_SLOTS = "bom_ram_min_slots"
    BOM_40G_PART = "bom_40g_name"
    BOM_40G_PART_COUNT = "bom_40g_count"
    BOM_10G_PART = "bom_10g_name"
    BOM_10G_PART_COUNT = "bom_10g_count"
    BOM_DUAL_SWITCH_PART = "bom_dual_switch_name"
    BOM_DUAL_SWITCH_PART_COUNT = "bom_dual_switch_count"
    BOM_HERCULES_PART = 'bom_hercules_part'
    BOM_HERCULES_COUNT = 'bom_hercules_count'
    BOM_CHASSIS_NAME = "chassis_bom_name"
    BOM_CHASSIS_DESCR = "chassis_bom_descr"
    BOM_CHASSIS_COUNT = "chassis_count"

    # Accessory Labels
    ACC = 'accessory'
    ACC_NAME = 'part_name'
    ACC_DESCR = 'part_description'
    ACC_PRICE = 'part_price'
    ACC_COUNT = 'count'
    ACC_TYPE = 'type'
    ACC_BUNDLE_COUNT = 'bundle_count'

    WORKLOAD_TYPES = [VDI, RDSH, VDI_INFRA, VSI, DB, OLTP, OLAP, ROBO, RAW, ORACLE, OOLTP, OOLAP, EXCHANGE, EPIC,
                      VEEAM, SPLUNK, VDI_HOME, RDSH_HOME, CONTAINER, AIML, ANTHOS]

    # CLUSTER TYPE CONSTANTS
    NORMAL = "normal"
    STRETCH = "stretch"
    REPLICATION_FLAG = "remote_replication_enabled"
    REPLICATED = "replicated"
    REPLICATION_AMT = "replication_amt"
    ANY_CLUSTER = "any"
    REPLICATION_TYPE = "replication_type"
    REMOTE = "remote"

    LICENSE_YEARS = 'license_yrs'

    # LICENSE COST
    LICENSE = {'STANDARD': {'cto_1': 9375,
                            'cto_3': 24750,
                            'bundle_1': 7969,
                            'bundle_3': 21038},
               'PREMIUM': {'cto_1': 16875,
                           'cto_3': 44550,
                           'bundle_1': 14344,
                           'bundle_3': 37868}}

    # HYPERVISOR PRICE
    ESX_SOFTWARE_PRICE = 14000
    HYPER_V_SOFTWARE_PRICE = 288

    # NODE_SUB_TYPE
    HYPER = "hyperconverged"
    ALL_FLASH = "all-flash"
    ALL_FLASH_7_6TB = "all-flash-7.6tb"     # This subtype for 7.6TB as it has different static overhead
    COMPUTE = "compute"
    ROBO_NODE = "robo"
    AF_ROBO_NODE = "robo_allflash"
    ROBO_TWO_NODE = "robo_two_node"
    AF_ROBO_TWO_NODE = "robo_allflash_two_node"
    ROBO_240 = "robo_240"
    ROBO_AF_240 = "robo_af_240"
    EPIC_NODE = "epic"
    VEEAM_NODE = 'veeam'
    LFF_12TB_NODE = 'lff_12tb'
    ALLNVME_NODE = 'allnvme'
    ALLNVME_NODE_8TB = 'allnvme_8tb'
    AIML_NODE = 'aiml'
    LFF_NODE = 'lff'

    # resize for 5.3 version required the merging of two settings_json
    # the below list has tags that are required to produce the single json
    base_list = ["heterogenous", "sed_only", "disk_option", "modular_lan",
                 "Compute_Type", "Node_Type", "RAM_Slots", "RAM_Options",
                 "CPU_Type", "bundle_only", "includeSoftwareCost", "filters", "threshold"]

    # this list is used in node_views for constructing the tag list for UI filter settings.
    base_node_list = ['HXAF-SP-220', 'HXAF-SP-240',
                      'HXAF-220', 'HXAF-220 [1 CPU]',
                      'HXAF-240', 'HXAF-240 [1 CPU]', 'HXAF-220 [NVME]',
                      'HXAF-E-240', 'HXAF-E-220', 'HXAF-240 [SD EDGE]',
                      'HX-SP-220', 'HX-SP-240', 'HX-SP-240 [LFF]',
                      'HX220C', 'HX220C [1 CPU]',
                      'HX240C', 'HX240C [1 CPU]', 'HX240C [LFF]',
                      'HX-E-240', 'HX-E-220', 'HX240C [SD EDGE]']

    # Availability of parts should be tracked
    CPU_AVAILABILITY = "CPU_AVAILABILITY"
    HDD_AVAILABILITY = "HDD_AVAILABILITY"
    RAM_AVAILABILITY = "RAM_AVAILABILITY"
    SSD_AVAILABILITY = "SSD_AVAILABILITY"
    GPU_AVAILABILITY = "GPU_USERS_AVAILABILITY"

    # Sizing Calculation for Nodes
    SIZING_CALCULATION = 'sizing_calculation'

    RAW_CORES_TOTAL = 'raw_cores_total'
    RAW_CORES_ADJSPECLNT = 'raw_cores_adjspeclnt'
    CORES_TOTAL_POSTOVERHEAD = 'cores_total_postoverhead'
    CORES_TOTAL_POSTTHRESHOLD = 'cores_total_postthreshold'
    CPU_OPRATIO = 'cpu_opratio'

    RAW_RAM_TOTAL = 'raw_ram_total'
    RAM_TOTAL_POSTOVERHEAD = 'ram_total_postoverhead'
    RAM_TOTAL_POSTTHRESHOLD = 'ram_total_postthreshold'
    RAM_OPRATIO = 'ram_opratio'

    RAW_HDD_TOTAL = 'raw_hdd_total'
    HDD_TOTAL_POSTRF = 'hdd_total_postrf'
    HDD_TOTAL_POSTOVERHEAD = 'hdd_total_postoverhead'
    HDD_TOTAL_POSTTHRESHOLD = 'hdd_total_postthreshold'
    HDD_OPRATIO = 'hdd_opratio'

    RAW_IOPS_TOTAL = 'raw_iops_total'
    IOPS_TOTAL_POSTIOPSCONV = 'iops_total_postiopsconv'

    RAW_VRAM_TOTAL = 'raw_vram_total'
    NODE_OVERHEAD = 'node_overhead'
    HIGHEST_RF = 'highest_rf'
    THRESHOLD_KEY = 'threshold_key'
    SCALING_FACTOR = 'scaling_factor'

    # Settings string
    DISK_CAGE = 'disk_cage'
    SMALL_FORM_FACTOR = 'SFF'
    LARGE_FORM_FACTOR = 'LFF'
    SOFTWARE_COST = "includeSoftwareCost"
    BUNDLE_DISCOUNT = "bundle_discount_percentage"
    CTO_DISCOUNT = "cto_discount_percentage"

    NODE = 'node'
    NUM = 'num'
    NUM_COMPUTE = 'num_compute'

    TOP_VALUE = 10
    RACK_UNITS = 'rack_units'


    HOME_CONFIG = OrderedDict()
    HOME_CONFIG['Small'] = {'cpu': 2, 'ram': 8, 'max_data': 4000, 'max_iops': 3000}
    HOME_CONFIG['Medium'] = {'cpu': 4, 'ram': 16, 'max_data': 16000, 'max_iops': 6000}
    HOME_CONFIG['Large']= {'cpu': 8, 'ram': 32, 'max_data': 32000, 'max_iops': 12000}

    # Hercules IO/s performance increase in percentage
    HERCULES_IOPS = {
        OLAP: 16,
        OOLAP: 16,
        EXCHANGE_32KB: 12,
        EXCHANGE_16KB: 15,
        VDI_HOME: 13,
        OLTP: 8,
        OOLTP: 8,
        VSI: 8,
        ROBO: 8,
        ROBO_BACKUP: 8,
        EXCHANGE_64KB: 16,
        VDI: 15,
        RDSH: 15,
        RDSH_HOME: 13,
        VDI_INFRA: 0,
        SPLUNK: 0,
        EPIC: 0,
        VEEAM: 0,
        RAW: 0,
        CONTAINER: 8,
        AIML: 0,
        ANTHOS: 0
    }

    HERCULES_CARD_COST = 2599

    # HX Boost IO/s performance increase in percentage
    HX_BOOST_IOPS = {
        OLAP: 10,
        OOLAP: 10,
        EXCHANGE_32KB: 10,
        EXCHANGE_16KB: 10,
        VDI_HOME: 10,
        OLTP: 25,
        OOLTP: 25,
        VSI: 25,
        ROBO: 10,
        ROBO_BACKUP: 10,
        EXCHANGE_64KB: 10,
        VDI: 10,
        RDSH: 10,
        RDSH_HOME: 10,
        VDI_INFRA: 10,
        SPLUNK: 10,
        EPIC: 10,
        VEEAM: 10,
        RAW: 10,
        CONTAINER: 25,
        AIML: 10,
        ANTHOS: 0,
    }

    # extra HDD compression provided by hercules configs
    HERCULES_COMP = 10

    COMPRESSION_FACTOR = 'compression_factor'
    DEDUPE_FACTOR = 'dedupe_factor'

    # Hercules configs
    DISABLED = 'disabled'
    ENABLED = 'enabled'
    FORCED = 'forced'

    MAX_CONTAINER_IOPS_NODES = 4
    SINGLE_CLUSTER = 'single_cluster'

    REF_IOPS_CPU = '8276 [Cascade]'

    # Sizing Option configs
    BUNDLE_ONLY = 'bundle'
    CTO_ONLY = 'cto'
    BUNDLE_AND_CTO = 'ALL'

    # N:1 backup related
    NUM_OF_SITES = 'num_of_sites'
    WL_NAME = "wl_name"
    WL_TYPE = "wl_type"
    BACKUP_REPLICATION_FACTOR = "backup_replication_factor"
    BACKUP_FAULT_TOLERANCE = "backup_fault_tolerance"
    BACKUP_COMPRESSION_FACTOR = "backup_compression_factor"
    BACKUP_DEDUPE_FACTOR = "backup_dedupe_factor"
    # "backup_compression_saved"
