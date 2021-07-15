package hyperconverged

import (
	"cisco_sizer/constants"
	"cisco_sizer/structure"
	"cisco_sizer/utilities"
	"math"
)

type partitionSizingInfo struct {
	HighestRF       int
	RFString        string
	FaultTolerance  int
	WlClustertype   string
	Hypervisor      string
	SlotDic         map[string][]int
	FilterNode      []HyperconvergedNode
	StaticOverHead  map[string]int
	Workload        []structure.WorkloadCustom
	ThresholdFactor int
	Hercules        bool
	HxBoost         bool
	VdiGpuExists    bool
	PartsNeed       []PartitionPart
	HxNodeList      []HyperconvergedNode
}

func UnitConversion(num float64, unit string, req_unit string) float64 {
	var result float64
	var TIB_TO_TB_CONVERSION float64 = 1.099511628
	var GIB_TO_GB_CONVERSION float64 = 1.073741824

	// var GB_TO_GIB_CONVERSION float64= 0.931322575
	// var TB_TO_TIB_CONVERSION float64 = 0.909494702

	switch req_unit {
	case "GB":
		switch unit {
		case "TB":
			result = num * 1000
		case "GiB":
			result = num * GIB_TO_GB_CONVERSION
		case "TiB":
			result = num * TIB_TO_TB_CONVERSION * 1000
		default:
			result = num
		}
	case "GiB":
		switch unit {
		case "TiB":
			result = num * 1024
		case "GiB":
			result = num / GIB_TO_GB_CONVERSION
		case "TB":
			result = (num / TIB_TO_TB_CONVERSION) * 1024
		default:
			result = num
		}
	}
	return result
}

func (sizingInfo *partitionSizingInfo) GetBasicSizingInfo(lstWorkload []structure.WorkloadCustom, wlClusterType string) {
	var lstReplicationFactor = make([]int, 0)
	var lstFaultTolerance = make([]int, 0)

	for _, workload := range lstWorkload {
		lstReplicationFactor = append(lstReplicationFactor, workload.Attrib.ReplicationFactor)
		lstFaultTolerance = append(lstFaultTolerance, workload.Attrib.FaultTolerance)
	}
	sizingInfo.HighestRF = utilities.MaxInt(lstReplicationFactor)
	sizingInfo.FaultTolerance = utilities.MaxInt(lstFaultTolerance)
	switch sizingInfo.HighestRF {
	case 2:
		sizingInfo.RFString = "RF2"
	case 3:
		sizingInfo.RFString = "RF3"
	default:
		sizingInfo.RFString = "RF3"
	}
	sizingInfo.WlClustertype = wlClusterType
	// sizingInfo.PartsNeed = make([])
}

func getSlotKeys() []string {
	return []string{"cpu_socket_count", "ram_slots", "hdd_slots", "ssd_slots", "pcie_slots"}
}

//get_minimum_size
func GetMinimumSize(subtype string, faultTolerance int, clusterType string, replicationFactor int) int {

	switch subtype {
	case constants.ROBO_NODE, constants.AF_ROBO_NODE, constants.ROBO_TWO_NODE, constants.AF_ROBO_TWO_NODE:
		if replicationFactor == 3 {
			return 3
		} else {
			return 2
		}
	case constants.ROBO_240, constants.ROBO_AF_240:
		return 3
	}
	if clusterType == constants.STRETCH {
		return 2
	}
	minSize := 3
	if 2 <= faultTolerance && faultTolerance <= 4 {
		return faultTolerance + minSize
	}
	return minSize
}

//get_max_cluster_value
func GetMaxClusterValue(nodeType string, diskCage string, hypervisor string, clusterType string, isCompute bool) (max_cluster int) {
	if clusterType == constants.STRETCH {
		if utilities.StringInSlice(nodeType, []string{constants.LFF_NODE, constants.LFF_12TB_NODE}) {
			max_cluster = 8
		} else {
			max_cluster = 16
		}
	} else if hypervisor == "hyperv" {
		max_cluster = 16
	} else if utilities.StringInSlice(nodeType, []string{constants.ROBO_NODE, constants.AF_ROBO_NODE, constants.ROBO_240, constants.ROBO_AF_240}) {
		max_cluster = 4
	} else if utilities.StringInSlice(nodeType, []string{constants.ROBO_TWO_NODE, constants.AF_ROBO_TWO_NODE}) {
		max_cluster = 2
	} else if utilities.StringInSlice(nodeType, []string{constants.VEEAM_NODE}) {
		max_cluster = 8
	} else if utilities.StringInSlice(nodeType, []string{constants.LFF_NODE, constants.LFF_12TB_NODE}) {
		max_cluster = 16
	} else if diskCage == constants.SMALL_FORM_FACTOR {
		max_cluster = 32
	} else {
		panic("Could not return the max cluster size i.e. unrecognizable combination")
	}

	if isCompute {
		if clusterType == constants.STRETCH {
			value, _ := GetComputeToHxRatio(nodeType, diskCage, hypervisor, clusterType)
			max_cluster = int(math.Min(float64(max_cluster*value), 16))
		} else {
			value, _ := GetComputeToHxRatio(nodeType, diskCage, hypervisor, clusterType)
			max_cluster = int(math.Min(float64(max_cluster*value), 32))
		}
	}
	return
}

// get_comp_to_hx_ratio
func GetComputeToHxRatio(nodeType, diskCage, hypervisor, clusterType string) (int, int) {
	// 2,1 means for each HX node there can be 2 compute nodes
	if hypervisor == "hyperv" {
		return 1, 1
	} else {
		return 2, 1
	}
}

func GetStaticOverHeadData(overhead map[string]Overhead, hypervisor string) (cpu int, hdd int, ram int) {
	cpu = overhead[hypervisor].CPU
	hdd = overhead[hypervisor].HDD
	ram = overhead[hypervisor].RAM
	return
}
