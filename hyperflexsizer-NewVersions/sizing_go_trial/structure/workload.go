package structure

import "cisco_sizer/constants"

// import "cisco_sizer/constants"

type CapSumType struct {
	Normal   CustomDictionary
	Hercules CustomDictionary
}

type WorkloadCustom struct {
	Attrib             Workload         `json:"wl_type"`
	Compression        float64          `json:"compression"`
	Dedupe             float64          `json:"dedupe"`
	FrameBuffer        float64          `json:"frame_buff"`
	HerculesComp       float64          `json:"herc_comp"`
	NumInstance        float64          `json:"num_inst"`
	OriginalSize       float64          `json:"original_size"`
	OsData             float64          `json:"os_data"`
	UserData           float64          `json:"user_data"`
	ReplicationTraffic float64          `json:"replication_traffic"`
	OriginalIopsSum    CustomDictionary `json:"original_iops_sum"`
	Capsum             CapSumType       `json:"capsum"`
	ClockPerVM         float64          `json:"clock_per_vm"`
	MaxClockPerCore    float64          `json:"max_clock_per_core"`
	NumVms             float64          `json:"num_vms"`
}

type Workload struct {
	WlType            string   `json:"wl_type"`
	WlName            string   `json:"wl_name"`
	WlClusterName     string   `json:"wl_cluster_name"`
	ProfileType       string   `json:"profile_type"`
	Remote            bool     `json:"remote"`
	InfoMsg           []string `json:"infoMsg"`
	IsDirty           bool     `json:"isDirty"`
	NumVms            float64  `json:"num_vms"`
	Snapshots         float64  `json:"snapshots"`
	DiskPerVm         float64  `json:"disk_per_vm"`
	DiskPerVmUnit     string   `json:"disk_per_vm_unit"`
	WorkingSet        int      `json:"working_set"`
	ClusterType       string   `json:"cluster_type"`
	DedupeSaved       int      `json:"dedupe_saved"`
	ProvisioningType  string   `json:"provisioning_type"`
	DedupeFactor      float64  `json:"dedupe_factor"`
	InternalType      string   `json:"internal_type"`
	AvgIopsPerVm      int      `json:"avg_iops_per_vm"`
	BaseImageSize     float64  `json:"base_image_size"`
	BaseImageSizeUnit string   `json:"base_image_size_unit"`
	FaultTolerance    int      `json:"fault_tolerance"`
	Concurrency       float64  `json:"concurrency"`
	GpuUsers          bool     `json:"gpu_users"`
	UserIops          float64  `json:"user_iops"`
	GoldImageSize     float64  `json:"gold_image_size"`
	GoldImageSizeUnit string   `json:"gold_image_size_unit"`
	CompressionFactor float64  `json:"compression_factor"`
	CompressionSaved  int      `json:"compression_saved"`
	StorageProtocol   string   `json:"storage_protocol"`
	TaggedWorkload    bool     `json:"TAGGED_WL,omitempty"`

	//Raw
	OverheadPercentage float64 `json:"overhead_percentage"`
	CpuModel           string  `json:"cpu_model"`
	CpuAttribute       string  `json:"cpu_attribute"`
	CpuClock           float64 `json:"cpu_clock"`
	Vcpus              int     `json:"vcpus"`
	RamSize            float64 `json:"ram_size"`
	RamSizeUnit        string  `json:"ram_size_unit"`
	RamOpratio         float64 `json:"ram_opratio"`
	HddSize            float64 `json:"hdd_size"`
	HddSizeUnit        string  `json:"hdd_size_unit"`
	Compression        float64 `json:"compression"`
	Dedupe             float64 `json:"dedupe"`
	IoBlockSize        string  `json:"io_block_size"`
	IopsValue          float64 `json:"iops_value"`
	SsdSize            float64 `json:"ssd_size"`
	EXCHANGE_32KB      float64 `json:"EXCHANGE_32KB"`
	EXCHANGE_16KB      float64 `json:"EXCHANGE_16KB"`
	EXCHANGE_64KB      float64 `json:"EXCHANGE_64KB"`

	//RDSH
	RdshDirectory   int    `json:"rdsh_directory"`
	TotalUsers      int    `json:"total_users"`
	SessionsPerVm   int    `json:"sessions_per_vm"`
	ClockPerSession int    `json:"clock_per_session"`
	MaxVcpusPerCore int    `json:"max_vcpus_per_core"`
	HddPerUser      int    `json:"hdd_per_user"`
	HddPerUserUnit  string `json:"hdd_per_user_unit"`
	OsPerVm         int    `json:"os_per_vm"`
	OsPerVmUnit     string `json:"os_per_vm_unit"`

	//INFRA VDI
	VmDetails CustomDictionary `json:"vm_details"`

	//DB
	NumDbInstances float64 `json:"num_db_instances"`
	VcpusPerDb     float64 `json:"vcpus_per_db"`
	RamPerDbUnit   string  `json:"ram_per_db_unit"`
	RamPerDb       float64 `json:"ram_per_db"`
	DbSize         float64 `json:"db_size"`
	DbSizeUnit     string  `json:"db_size_unit"`
	MetaDataSize   float64 `json:"metadata_size"`
	AvgIopsPerDb   float64 `json:"avg_iops_per_db"`

	//VSI
	VcpusPerVm   int `json:"vcpus_per_vm"`
	VcpusPerCore int `json:"vcpus_per_core"`

	//vdi
	DiskPerDesktop       float64 `json:"disk_per_desktop"`
	DiskPerDesktopUnit   string  `json:"disk_per_desktop_unit"`
	VcpusPerDesktop      int     `json:"vcpus_per_desktop"`
	NumDesktops          float64 `json:"num_desktops"`
	ClockPerDesktop      float64 `json:"clock_per_desktop,omitempty"`
	RamPerDesktop        float64 `json:"ram_per_desktop,omitempty"`
	RamPerDesktopUnit    string  `json:"ram_per_desktop_unit,omitempty"`
	AvgIopsPerDesktop    float64 `json:"avg_iops_per_desktop,omitempty"`
	VdiDirectory         int     `json:"vdi_directory,omitempty"`
	OsType               string  `json:"os_type"`
	VideoRAM             string  `json:"video_RAM"` //ui need to fix to int
	InflightDedupeFactor float64 `json:"inflight_dedupe_factor,omitempty"`
	InflightDataSize     float64 `json:"inflight_data_size,omitempty"`
	ImageDedupeFactor    float64 `json:"image_dedupe_factor,omitempty"`
	ReplicationFactor    int     `json:"replication_factor,omitempty"`

	//vdi home directory
	PrimaryWlName   string `json:"primary_wl_name"`
	NumberOfVms     int    `json:"number_of_vms"`
	Profile         string `json:"profile"`
	ReplicationType string `json:"replication_type"`

	//VSI
	ReplicationMult   float64 `json:"replication_mult,omitempty"`
	ReplicationAmount float64 `json:"replication_amt,omitempty"`
	RamPerVm          float64 `json:"ram_per_vm,omitempty"`
	RamPerVmUnit      string  `json:"ram_per_vm_unit,omitempty"`

	//AIML
	InputType    string `json:"input_type,omitempty"`
	ExpectedUtil string `json:"expected_util,omitempty"`
	GpuType      string `json:"gpu_type,omitempty"`

	//ROBO/EDGE
	ModeLan string `json:"mod_lan,omitempty"`
}

type WorkloadType struct {
	VDI []WorkloadCustom
	// RDSH                  []WorkloadCustom
	// VDI_INFRA             []WorkloadCustom
	VSI []WorkloadCustom
	// DB                    []WorkloadCustom
	ORACLE                []WorkloadCustom
	RAW                   []WorkloadCustom
	EXCHANGE              []WorkloadCustom
	ROBO                  []WorkloadCustom
	EPIC                  []WorkloadCustom
	VEEAM                 []WorkloadCustom
	SPLUNK                []WorkloadCustom
	CONTAINER             []WorkloadCustom
	AIML                  []WorkloadCustom
	ANTHOS                []WorkloadCustom
	ROBO_BACKUP           []WorkloadCustom
	ROBO_BACKUP_SECONDARY []WorkloadCustom
}

func (customeWorkload *WorkloadCustom) InitWorkloadCustom(workload Workload) {
	customeWorkload.Attrib = workload
	customeWorkload.OriginalIopsSum = make(CustomDictionary)
}

// type HomeConfig struct {
// 	fieldValue map[string]HomeConfigValues
// 	// Small  HomeConfigValues
// 	// Medium HomeConfigValues
// 	// Large  HomeConfigValues
// }
type HomeConfigValues struct {
	Cpu     float64
	Ram     float64
	MaxData float64
	MaxIops float64
}

func GetHomeConfig() map[string]HomeConfigValues {
	var homeConfigs = make(map[string]HomeConfigValues)
	homeConfigs["Small"] = HomeConfigValues{Cpu: 2, Ram: 8, MaxData: 4000, MaxIops: 3000}
	homeConfigs["Medium"] = HomeConfigValues{Cpu: 4, Ram: 16, MaxData: 16000, MaxIops: 6000}
	homeConfigs["Large"] = HomeConfigValues{Cpu: 8, Ram: 32, MaxData: 32000, MaxIops: 12000}
	return homeConfigs
	// homeConfig.Small = HomeConfigValues{Cpu: 2, Ram: 8, MaxData: 4000, MaxIops: 3000}
	// homeConfig.Medium = HomeConfigValues{Cpu: 4, Ram: 16, MaxData: 16000, MaxIops: 6000}
	// homeConfig.Large = HomeConfigValues{Cpu: 8, Ram: 32, MaxData: 32000, MaxIops: 12000}
}

func (workload *WorkloadCustom) GetWorkloadCapsum(cap string, hercules bool) float64 {
	if hercules {
		return workload.Capsum.Hercules.JsonParseFloat(cap)
	} else {
		return workload.Capsum.Normal.JsonParseFloat(cap)
	}
}

func (workload *WorkloadCustom) SetWorkloadIopsCapsum(hercules bool, value float64) {
	if hercules {
		workload.Capsum.Hercules[constants.IOPS] = value
	} else {
		workload.Capsum.Hercules[constants.IOPS] = value
	}
}
