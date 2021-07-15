package hyperconverged

import (
	"cisco_sizer/constants"
	"cisco_sizer/model"
	"encoding/json"
	"strings"
)

//DB node_json data
type NodeAttrib struct {
	//yet the check node name
	NodeName string
	//DB data
	BasePrice         float64             `json:"base_price"`
	BomFiPackageName  string              `json:"bom_fi_package_name"`
	BomName           string              `json:"bom_name"`
	BomPackageName    string              `json:"bom_package_name"`
	Btu               int                 `json:"btu"`
	CpuOptions        []string            `json:"cpu_options"`
	CpuSocketCount    []int               `json:"cpu_socket_count"`
	RamOptions        []string            `json:"ram_options"`
	RamSlots          []int               `json:"ram_slots"`
	DiskCage          string              `json:"disk_cage"`
	DiskPackage       string              `json:"disk_package"`
	FiOptions         []string            `json:"fi_options"`
	GenericRules      []int               `json:"generic_rules"` // it may need change as interface
	GpuOptions        []string            `json:"gpu_options"`
	HddOptions        []string            `json:"hdd_options"`
	HddSlots          []int               `json:"hdd_slots"`
	Name              string              `json:"name"`
	NetworkThroughput int                 `json:"network_throughput"`
	PcieSlots         []int               `json:"pcie_slots"`
	Power             int                 `json:"power"`
	RackSpace         int                 `json:"rack_space"`
	SsdOptions        []string            `json:"ssd_options"`
	SsdSlots          []int               `json:"ssd_slots"`
	StaticOverhead    map[string]Overhead `json:"static_overhead"`
	Status            bool                `json:"status"`
	Subtype           string              `json:"subtype"`
	Type              string              `json:"type"`
	Vendor            string              `json:"vendor"`

	UseChassis     bool   `json:"use_chassis"`
	ChassisOptions string `json:"chassis_options"`
	RiserOptions   string `json:"riser_options"`
	BomRaidName    string `json:"bom_raid_name"`
	BomSystemDrive string `json:"bom_system_drive,"`
	BomBootDrive   string `json:"bom_boot_drive"`

	// calculated data
	CpuPart        string `json:"cpu_part"`
	CpuPriceFactor string `json:"cpu_price"`
	RamPart        string `json:"ram_part"`
	RamPriceFactor string `json:"ram_price"`
	HddPart        string `json:"hdd_part"`
	HddPriceFactor string `json:"hdd_price"`
	SsdPart        string `json:"ssd_part"`
	SsdPriceFactor string `json:"ssd_price"`
	GpuPart        string `json:"gpu_part"`
	GpuPriceFactor string `json:"gpu_price"`

	Frequency         float64 `json:"frequency"`
	SpecInt           float64 `json:"speclnt"`
	CoresPerCpu       float64 `json:"cores_per_cpu"`
	CpuDescription    string  `json:"cpu_description"`
	Tdp               float64 `json:"tdp"`
	CpuBomName        string  `json:"cpu_bom_name"`
	CpuBomDescription string  `json:"cpu_bom_descr"`

	RamSize             float64 `json:"ram_size"`
	RamDescription      string  `json:"ram_description"`
	RamBomName          string  `json:"ram_bom_name"`
	RamBomDescription   string  `json:"ram_bom_descr"`
	RamBomAddMemoryname string  `json:"bom_add_memory_name"`

	HddSize           float64 `json:"hdd_size"`
	HddDescription    string  `json:"hdd_description"`
	HddType           string  `json:"hdd_type"`
	HddBomName        string  `json:"hdd_bom_name"`
	HddBomDescription string  `json:"hdd_bom_descr"`

	SsdDescription    string  `json:"ssd_description"`
	SsdOutputCapacity float64 `json:"ssd_output_capacity"`
	SsdSize           float64 `json:"ssd_size"`
	SsdBomName        string  `json:"ssd_bom_name"`
	SsdBomDescription string  `json:"ssd_bom_descr"`

	GpuDescription    string  `json:"gpu_description"`
	GpuBomName        string  `json:"gpu_bom_name"`
	GpuBomDescription string  `json:"gpu_bom_descr"`
	GpuSize           float64 `json:"gpu_capacity"`
	IopsConvFactor    float64 `json:"iops_conversion_factor"`

	ClockSpeed     float64
	RamSlot        int
	MinRamSlot     float64
	Vram           float64
	Iops           float64
	HddSlot        float64
	MinHddSlot     float64
	SsdSlot        float64
	CpuSocketValue int
	Capex          float64
	OpexPerYear    int `json:"opex_per_year"`
}

type Overhead struct {
	CPU int
	HDD int
	RAM int
}

type NodeCap struct {
	CPU  float64
	HDD  float64
	RAM  float64
	SSD  float64
	VRAM float64
	IOPS float64
}

type HyperconvergedNode struct {
	BTU_CONV_FACTOR float64
	COST_PER_KWH    float64
	HOURS_PER_YEAR  int
	MONTHS_PER_YEAR int
	RACK_COST_MONTH int
	HRS_PER_MONTH   float64

	Attrib              NodeAttrib
	RawCap              NodeCap                 `json:"raw_cap"` //map[float64]interface{} // Holds value of raw capacity of caps {CPU:1}
	Cap                 NodeCap                 //map[string]interface{}
	OverheadData        NodeCap                 //map[float64]interface{} // Holds Overhead value of caps {CPU:0}
	HddSsdOverhead      map[float64]interface{} `json:"hdd_ssd_overhead"`
	ServerHardwarePrice float64                 `json:"server_hardware_price"`
	SoftwarePrice       float64                 `json:"software_price"`
	NetworkPrice        float64                 `json:"network_price"`
	VmwarePrice         float64                 `json:"vmware_price"`
	RawBaseRam          float64                 `json:"raw_base_ram"`
	AdditionalBaseRam   float64                 `json:"additional_base_ram"`
	RawBaseHdd          float64                 `json:"raw_base_hdd"`
	AdditionalBaseHdd   float64                 `json:"additional_base_hdd"`

	//TODO
	// self.storage_ref_dict

	NodeName             string
	HerculesAvail        bool    `json:"hercules_avail"`
	HxBoostAvail         bool    `json:"hx_boost_avail"`
	HerculesOn           bool    `json:"hercules_on"`
	HxBoostOn            bool    `json:"hx_boost_on"`
	PowerPrice           float64 `json:"power_price"`
	AnnualSupportOsPrice int     `json:"annual_support_os_price"`
	// Server_hardware_price   int
	// Software_price          int
	RackPrice         int `json:"rack_price"`
	FacilitiesPrice   int `json:"facilities_price"`
	MaintenancesPrice int `json:"maintenances_price"`

	Model_dict []string // For adding dict with LABEL, TAG_NAME ETC
	TotalOpex  int      `json:"total_opex"`
	TotalCapex int      `json:"total_capex"`
	Tco        int      `json:"tco"`
	// Vmware_price            int
	// Total_capex             int
}

type HyperNodeType struct {
	BundleHxNode   []HyperconvergedNode
	BundleCoNode   []HyperconvergedNode
	BundleAFNode   []HyperconvergedNode
	BundleRoboNode []HyperconvergedNode
	BundleEpicNode []HyperconvergedNode
	BundleVeemNode []HyperconvergedNode

	CtoHxNode   []HyperconvergedNode
	CtoCoNode   []HyperconvergedNode
	CtoAFNode   []HyperconvergedNode
	CtoRoboNode []HyperconvergedNode
	CtoEpicNode []HyperconvergedNode
	CtoVeemNode []HyperconvergedNode
}

func (node *HyperconvergedNode) SetDefault(model *model.Node) {

	err := json.Unmarshal(model.NodeJson, &node.Attrib)
	if err != nil {
		panic(err)
	}
	node.BTU_CONV_FACTOR = 0.00029307107
	node.COST_PER_KWH = 0.11
	node.HOURS_PER_YEAR = 8760
	node.MONTHS_PER_YEAR = 12
	node.RACK_COST_MONTH = 50
	node.HRS_PER_MONTH = 3.2

	node.NodeName = model.Name
	node.HerculesOn = model.HerculesAvail
	node.HxBoostOn = model.HxBoostAvail
	// node.Attrib.Static_overhead({exsi})

}

func (node *HyperconvergedNode) InitSeedNode(nodeName string, nodeType string, nodeSubType string, hercules bool, hxBoost bool) {
	var nodeJson NodeAttrib
	nodeJson.Type = nodeType
	nodeJson.Subtype = nodeSubType
	node.Attrib = nodeJson

}

func InitializeHyperconvergedNode(model *model.Node) HyperconvergedNode {

	node := HyperconvergedNode{}
	node.SetDefault(model)
	// fmt.Println(node)
	return node
}

//Get_tco
func (node *HyperconvergedNode) GetTco() {
	node.Tco = node.TotalCapex + node.TotalOpex*3
}

//calculate_cpu_usable_capacity
// raw = CPU_CNT * CORES_PER_CPU
// usable = raw - overhead value of CPU
func (node *HyperconvergedNode) CalculateCpuUsableCapacity() {
	node.RawCap.CPU = float64(node.Attrib.CpuSocketValue) * node.Attrib.CoresPerCpu
	node.Cap.CPU = node.RawCap.CPU - node.OverheadData.CPU
}

//calculate_clock_usable_capacity

func (node *HyperconvergedNode) CalculateClockUsableCapacity() {
	node.RawCap.CPU = node.Attrib.ClockSpeed*node.RawCap.CPU - 10.8
}

//calculate_ram_usable_capacity
func (node *HyperconvergedNode) CalculateRamUsableCapacity() {
	node.RawCap.RAM = float64(node.Attrib.RamSlot) * node.Attrib.RamSize
	node.Cap.RAM = node.RawCap.RAM - node.OverheadData.RAM
	node.RawBaseRam = node.Attrib.MinRamSlot
	node.AdditionalBaseRam = float64(node.Attrib.RamSlot) - node.Attrib.MinRamSlot
}

//calculate_gpu_usable_capacity
func (node *HyperconvergedNode) CalculateGpuUsableCapacity() {
	node.RawCap.VRAM = node.Attrib.Vram
	node.Cap.VRAM = node.RawCap.VRAM - node.OverheadData.VRAM
}

//calculate_iops_usable_capacity, calculate_gpu_usable_capacity
// calculate VRAM / IOPS usable capacity
func (node *HyperconvergedNode) CalculateIopsUsableCapacity() {
	node.RawCap.IOPS = node.Attrib.Iops
	node.Cap.IOPS = node.RawCap.IOPS - node.OverheadData.VRAM
}

//calculate_storage_usable_capacity
func (node *HyperconvergedNode) CalculateStorageUsableCapacity() {
	slots := node.Attrib.HddSlot
	size := node.Attrib.HddSize
	node.RawCap.HDD = slots * size
	node.Cap.HDD = slots * (size - node.OverheadData.HDD)

	node.RawBaseHdd = node.Attrib.MinHddSlot
	node.AdditionalBaseHdd = node.Attrib.HddSlot - node.RawBaseHdd
}

//calculate_storage_usable_capacity
func (node *HyperconvergedNode) CalculateSSDUsableCapacity() {
	slots := node.Attrib.SsdSlot
	size := node.Attrib.SsdSize
	node.RawCap.SSD = slots * size
	node.Cap.SSD = slots * (size - node.OverheadData.SSD)
}

//get_mod_lan --> called by utilization class
func (node *HyperconvergedNode) GetModuleLan() string {

	valid := true
	node_subtype := map[string]bool{"robo": valid, "robo_allflash": valid, "robo_two_node": valid, "robo_allflash_two_node": valid, "robo_240": valid, "robo_af_240": valid}

	module_lan := map[string]string{"40G-10G": "10G/40G", "40G": "40G", "10G": "10G", "DUAL": "Dual Switch"}
	// module_lan := []string{"40G-10G", "40G", "10G", "DUAL"}

	var mod_lan string = ""
	if node_subtype[node.Attrib.Subtype] {
		for search, mod := range module_lan {
			if strings.Contains(node.Attrib.SsdPart, search) {
				mod_lan = mod
				break
			}
		}
		if mod_lan == "" {
			mod_lan = "Single Switch"
		}
		mod_lan += " modular LAN"
	}
	return mod_lan
}

//calculate_overhead  -- Recheck the code base
func (node *HyperconvergedNode) CalculateOverhead(cap string, hypervisor string, storageProtocol string, hxBoost bool) {
	//var defaultOverhead = make(map[string]Overhead)
	// var overhead Overhead
	//TODO: this condition need to check if it required or not
	// if node.Attrib.StaticOverhead == nil {
	// 	node.Attrib.StaticOverhead[hypervisor].CPU =0
	// }
	var cpuOverhead, hddOverhead, ramOverhead int
	cpuOverhead, hddOverhead, ramOverhead = GetStaticOverHeadData(node.Attrib.StaticOverhead, hypervisor)
	switch cap {
	case constants.CPU:
		if hxBoost {
			cpuOverhead += 2
		}
		node.Attrib.StaticOverhead[hypervisor] = Overhead{cpuOverhead, hddOverhead, ramOverhead}
	case constants.RAM:
		if storageProtocol != "" && ramOverhead != 0 {
			ramOverhead += 2
		}
		node.Attrib.StaticOverhead[hypervisor] = Overhead{cpuOverhead, hddOverhead, ramOverhead}
	case constants.HDD:
		round_value := float64(hddOverhead) / 100
		// self.hdd_ssd_overhead[size_key] = round_value * self.attrib[size_key] // need to check
		round_value *= node.Attrib.HddSize
		hddOverhead = int(round_value * node.Attrib.HddSlot * round_value)
		node.Attrib.StaticOverhead[hypervisor] = Overhead{cpuOverhead, hddOverhead, ramOverhead}
	case constants.SSD:
		// -- we may have to add SSD overhead
		// round_value := float64(ssdOverhead) / 100
		// // self.hdd_ssd_overhead[size_key] = round_value * self.attrib[size_key] // need to check
		// round_value *= node.Attrib.SsdSize
		// ssdOverhead = int(round_value * node.Attrib.SsdSlot * round_value)

	}
}

//calc_cap
func (node *HyperconvergedNode) CalculateCapex(cap string) {
	switch cap {
	case constants.CPU:
		node.CalculateCpuUsableCapacity()
	case constants.RAM:
		node.CalculateRamUsableCapacity()
	case constants.HDD:
		node.CalculateStorageUsableCapacity()
	case constants.SSD:
		node.CalculateSSDUsableCapacity()
	case constants.VRAM:
		node.CalculateGpuUsableCapacity()
	}
}

//calc_capex_opex
func (node *HyperconvergedNode) CalculateCapexOpex() {
	node.Attrib.Capex = float64(node.Attrib.BasePrice)
	node.Attrib.OpexPerYear = 0
}
