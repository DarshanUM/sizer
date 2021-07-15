package hyperconverged

import (
	"cisco_sizer/constants"
	"cisco_sizer/model"
	"cisco_sizer/structure"
	"cisco_sizer/utilities"
	"reflect"
	"strings"
)

func LoadNode(lstNode []model.Node) HyperNodeType {
	//TODO: amend_cto_list option -- need to take during sizing and we should try to avoid put the logic here.
	var hyperNode HyperNodeType
	for _, node := range lstNode {
		hyperconveregNode := InitializeHyperconvergedNode(&node)
		switch nodeType := hyperconveregNode.Attrib.Type; nodeType {
		case "bundle":
			switch subType := hyperconveregNode.Attrib.Subtype; strings.ToLower(subType) {
			case "hyperconverged", "lff", "lff_12tb":
				hyperNode.BundleHxNode = append(hyperNode.BundleHxNode, hyperconveregNode)
			case "compute", "aiml":
				hyperNode.BundleCoNode = append(hyperNode.BundleCoNode, hyperconveregNode)
			case "all-flash", "allnvme_8tb", "allnvme", "all-flash-7.6tb":
				hyperNode.BundleAFNode = append(hyperNode.BundleAFNode, hyperconveregNode)
			case "robo", "robo_allflash", "robo_two_node", "robo_allflash_two_node", "robo_240", "robo_af_240":
				hyperNode.BundleRoboNode = append(hyperNode.BundleRoboNode, hyperconveregNode)
			case "epic":
				hyperNode.BundleEpicNode = append(hyperNode.BundleEpicNode, hyperconveregNode)

			}
		case "cto":
			switch subType := hyperconveregNode.Attrib.Subtype; strings.ToLower(subType) {
			case "hyperconverged", "lff", "lff_12tb":
				hyperNode.CtoHxNode = append(hyperNode.CtoHxNode, hyperconveregNode)
			case "compute", "aiml":
				hyperNode.CtoCoNode = append(hyperNode.CtoCoNode, hyperconveregNode)
			case "all-flash", "allnvme_8tb", "allnvme", "all-flash-7.6tb":
				hyperNode.CtoAFNode = append(hyperNode.CtoAFNode, hyperconveregNode)
			case "robo", "robo_allflash", "robo_two_node", "robo_allflash_two_node", "robo_240", "robo_af_240":
				hyperNode.CtoRoboNode = append(hyperNode.CtoRoboNode, hyperconveregNode)
			case "epic":
				hyperNode.CtoEpicNode = append(hyperNode.CtoEpicNode, hyperconveregNode)

			}
		}
	}
	return hyperNode
}

func GetCompatibleNodes(wlClusterType string, bundleOnly string, lstWorkload *[]structure.WorkloadCustom, hypernode *HyperNodeType) ([]HyperconvergedNode, []HyperconvergedNode) {
	var filteredHxNode, filteredCoNode []HyperconvergedNode
	switch wlClusterType {
	case constants.DB, constants.SPLUNK, constants.CONTAINER, constants.ORACLE:
		switch bundleOnly {
		case constants.BUNDLE_ONLY:
			filteredHxNode = append(filteredHxNode, hypernode.BundleAFNode...)
			//Compute node
			filteredCoNode = append(filteredCoNode, hypernode.BundleCoNode...)
		case constants.CTO_ONLY:
			filteredHxNode = append(filteredHxNode, hypernode.CtoAFNode...)
			//Compute node
			filteredCoNode = append(filteredCoNode, hypernode.CtoCoNode...)
		case constants.BUNDLE_AND_CTO:
			filteredHxNode = append(filteredHxNode, hypernode.BundleAFNode...)
			filteredHxNode = append(filteredHxNode, hypernode.CtoAFNode...)
			//Compute node
			filteredCoNode = append(filteredCoNode, hypernode.BundleCoNode...)
			filteredCoNode = append(filteredCoNode, hypernode.CtoCoNode...)
		}
	case constants.ROBO, constants.ROBO_BACKUP_SECONDARY:
		switch bundleOnly {
		case constants.BUNDLE_ONLY:
			filteredHxNode = append(filteredHxNode, hypernode.BundleRoboNode...)
			//Compute node
			filteredCoNode = append(filteredCoNode, hypernode.BundleCoNode...)
		case constants.CTO_ONLY:
			filteredHxNode = append(filteredHxNode, hypernode.CtoRoboNode...)
			//Compute node
			filteredCoNode = append(filteredCoNode, hypernode.CtoCoNode...)
		case constants.BUNDLE_AND_CTO:
			filteredHxNode = append(filteredHxNode, hypernode.BundleRoboNode...)
			filteredHxNode = append(filteredHxNode, hypernode.CtoRoboNode...)
			//Compute node
			filteredCoNode = append(filteredCoNode, hypernode.BundleCoNode...)
			filteredCoNode = append(filteredCoNode, hypernode.CtoCoNode...)
		}
	case constants.EPIC:
		switch bundleOnly {
		case constants.BUNDLE_ONLY:
			filteredHxNode = append(filteredHxNode, hypernode.BundleEpicNode...)
			//Compute node
			filteredCoNode = append(filteredCoNode, hypernode.BundleCoNode...)
		case constants.CTO_ONLY:
			filteredHxNode = append(filteredHxNode, hypernode.CtoEpicNode...)
			//Compute node
			filteredCoNode = append(filteredCoNode, hypernode.CtoCoNode...)
		case constants.BUNDLE_AND_CTO:
			filteredHxNode = append(filteredHxNode, hypernode.BundleEpicNode...)
			filteredHxNode = append(filteredHxNode, hypernode.CtoEpicNode...)
			//Compute node
			filteredCoNode = append(filteredCoNode, hypernode.BundleCoNode...)
			filteredCoNode = append(filteredCoNode, hypernode.CtoCoNode...)
		}
	default:
		switch bundleOnly {
		case constants.BUNDLE_ONLY:
			filteredHxNode = append(filteredHxNode, hypernode.BundleHxNode...)
			filteredHxNode = append(filteredHxNode, hypernode.BundleAFNode...)
			//Compute node
			filteredCoNode = append(filteredCoNode, hypernode.BundleCoNode...)
		case constants.CTO_ONLY:
			filteredHxNode = append(filteredHxNode, hypernode.CtoHxNode...)
			filteredCoNode = append(filteredCoNode, hypernode.CtoCoNode...)
			//Compute node
			filteredHxNode = append(filteredHxNode, hypernode.CtoAFNode...)
		case constants.BUNDLE_AND_CTO:
			filteredHxNode = append(filteredHxNode, hypernode.BundleHxNode...)
			filteredHxNode = append(filteredHxNode, hypernode.BundleAFNode...)
			filteredHxNode = append(filteredHxNode, hypernode.CtoHxNode...)
			filteredHxNode = append(filteredHxNode, hypernode.CtoAFNode...)
			//Compute node
			filteredCoNode = append(filteredCoNode, hypernode.BundleCoNode...)
			filteredCoNode = append(filteredCoNode, hypernode.CtoCoNode...)
		}
	}

	//TODO: below code base is converted yet. need to check if we can move this logic to sizing for better coding
	// // if self.current_cluster == HyperConstants.STRETCH:
	// // # Copy because its causing Hercules availability false for Normal cluster
	// // node_list = copy.deepcopy(node_list)
	// // for node in node_list:
	// // 	node.hercules_avail = True

	//TODO: SED node should be removed for STRETCH cluster. try move this logic to prepartition filter
	// // node_list = list(filter(lambda node: 'SED' not in node.name, node_list))

	ValidateNodeList(&filteredHxNode, &wlClusterType, lstWorkload)
	return filteredHxNode, filteredCoNode
}

// check if atleast one node has pci slots
func CheckNodesPcieSlots(lstNode *[]HyperconvergedNode) bool {
	for _, node := range *lstNode {
		if len(node.Attrib.PcieSlots) > 0 {
			return true
		}
	}
	return false
}

// This function is used for robo workload
func filterVICNode(lstNode *[]HyperconvergedNode, lstRoboWorkload *[]structure.WorkloadCustom) []HyperconvergedNode {

	var searchTerm string = ""
	var filteredLstNode []HyperconvergedNode
	search_ssd_opts := func(node *HyperconvergedNode) bool {
		var updatedSsdOption []string = node.Attrib.SsdOptions
		switch searchTerm {
		case constants.SINGLE_SWITCH:
			for index, val := range updatedSsdOption {
				if strings.Contains(val, "40G-10G") && strings.Contains(val, "DUAL") {
					//TODO: this logic  of removing the data from array may not work
					node.Attrib.SsdOptions = append(node.Attrib.SsdOptions[:index], node.Attrib.SsdOptions[index+1:]...)
				}
			}
		default:
			for index, val := range updatedSsdOption {
				if searchTerm != "" && strings.Contains(val, searchTerm) {
					//TODO: this logic  of removing the data from array may not work
					node.Attrib.SsdOptions = append(node.Attrib.SsdOptions[:index], node.Attrib.SsdOptions[index+1:]...)
				}
			}

		}
		if len(node.Attrib.SsdOptions) > 0 {
			return true
		} else {
			return false
		}

	}
	for _, roboWl := range *lstRoboWorkload {
		switch roboWl.Attrib.ModeLan {
		case constants.MOD_10G:
			searchTerm = "40G-10G"
		case constants.DUAL_SWITCH:
			searchTerm = "DUAL"
		case constants.SINGLE_SWITCH:
			searchTerm = "SINGLE"
		default:
			searchTerm = ""
		}
	}
	for _, hyperNode := range *lstNode {
		if !search_ssd_opts(&hyperNode) {
			filteredLstNode = append(filteredLstNode, hyperNode)
		}
	}
	return filteredLstNode

}

// this is required for RDSH workload, AIML workload, ROBO, N:1 backup workload
func PrePartitionFilter(lstHxNode, lstCoNode *[]HyperconvergedNode, lstWorkload *[]structure.WorkloadCustom, wlClusterType string) ([]HyperconvergedNode, []HyperconvergedNode) {
	var filteredHxNode, filteredCoNode []HyperconvergedNode

	var isRdshWorkload bool = false
	pcie_slot_zero := [1]int{0}

	//TODO: we can refactor the below anonymus func to get the RDSH WL separately
	CalculateRdshWorkload := func(hyperNode *HyperconvergedNode) bool {
		for _, wl := range *lstWorkload {
			if wl.Attrib.InternalType == constants.RDSH {
				isRdshWorkload = true
				lstCpu := make([]string, 0)
				for _, cpu := range hyperNode.Attrib.CpuOptions {
					cpu_clock := GetPartAttrib(cpu, constants.FREQUENCY).(float64)
					cpu_capacity := GetPartAttrib(cpu, constants.CAPACITY).(float64)
					if !((cpu_clock * cpu_capacity) < wl.ClockPerVM) {
						lstCpu = append(lstCpu, cpu)
					}
				}
				// hyperNode.Attrib.CpuOptions = lstCpu
				return len(lstCpu) > 0
			}
		}
		return false
	}

	filter_gpu := func(nodeGpuOptions []string, wlGpuType string) []string {
		var lstGpu = make([]string, 0)
		for _, gpuName := range nodeGpuOptions {
			if GetPartAttrib(gpuName, constants.FilterTag).(string) == wlGpuType && strings.Contains(gpuName, "V100-32") {
				lstGpu = append(lstGpu, gpuName)
			}
		}
		return lstGpu
	}

	isAimlInputType := CheckAllAimlInputType(lstWorkload)
	isAllAimlWl := CheckAllAimlWorkload(lstWorkload)
	for _, hyperNode := range *lstHxNode {
		if CalculateRdshWorkload(&hyperNode) {
			filteredHxNode = append(filteredHxNode, hyperNode)
		} else if wlClusterType == constants.AIML {
			if (isAimlInputType || !isAllAimlWl) && reflect.DeepEqual(hyperNode.Attrib.PcieSlots, pcie_slot_zero) {
				continue
			}

			wlGpuType := (*lstWorkload)[0].Attrib.GpuType
			filtersGPuOptions := filter_gpu(hyperNode.Attrib.GpuOptions, wlGpuType)
			if len(filtersGPuOptions) > 0 {
				filteredHxNode = append(filteredHxNode, hyperNode)
			}
		} else if wlClusterType == constants.ROBO || wlClusterType == constants.ROBO_BACKUP_SECONDARY {
			var arrReplicationFactor = make([]int, 0)
			for _, workload := range *lstWorkload {
				arrReplicationFactor = append(arrReplicationFactor, workload.Attrib.ReplicationFactor)
			}
			if utilities.MaxInt(arrReplicationFactor) == 3 && utilities.StringInSlice(hyperNode.Attrib.Subtype, []string{constants.ROBO_NODE, constants.AF_ROBO_NODE, constants.ROBO_240, constants.ROBO_AF_240}) {
				filteredHxNode = append(filteredHxNode, hyperNode)
			}
		} else {
			filteredHxNode = append(filteredHxNode, hyperNode)
		}
	}

	if len(filteredHxNode) > 0 && isRdshWorkload {
		panic("Unable to find a CPU that can fit an entire VM. Please check the filters")
	}
	isAnyAIMLWl := CheckAnyAimlWorkload(lstWorkload)
	for _, hyperCoNode := range *lstCoNode {
		if wlClusterType == constants.AIML {
			if isAnyAIMLWl && hyperCoNode.Attrib.Subtype != constants.AIML_NODE {
				continue
			} else if hyperCoNode.Attrib.Subtype == constants.AIML_NODE {
				continue
			}
			filteredCoNode = append(filteredCoNode, hyperCoNode)
		} else {
			filteredCoNode = append(filteredCoNode, hyperCoNode)
		}
	}

	return filteredHxNode, filteredCoNode
}

func PostPartitionFilter(lstHxNode, lstCoNode *[]HyperconvergedNode, partitionGrp *[]structure.WorkloadCustom, wlClusterType string) ([]HyperconvergedNode, []HyperconvergedNode) {
	var filteredHxNode, filteredCoNode, gpuNode []HyperconvergedNode

	//TODO: yet to convert the codebase -- need to check if the code is really required
	// if len(partn_grp) > 1:
	//         for node in filtered_nodes:
	//             node.hercules_avail = False

	switch wlClusterType {
	case constants.EPIC:
		//TODO: yet to do
	case constants.ROBO, constants.ROBO_BACKUP_SECONDARY:
		// TOOD: test --> these part partn_grp[0]
		filteredHxNode = append(filteredHxNode, filterVICNode(lstHxNode, partitionGrp)...)
	case constants.VDI:
		filteredHxNode = func() (tempNode []HyperconvergedNode) {
			for _, hyperNode := range *lstHxNode {
				if hyperNode.Attrib.DiskCage == constants.LARGE_FORM_FACTOR {
					tempNode = append(tempNode, hyperNode)
				}
			}
			return
		}()

		gpuStatus, frame_buff_req := func() (tempGpuStatus bool, frameBuffReq []float64) {
			for _, wl := range *partitionGrp {
				if wl.Attrib.GpuUsers {
					tempGpuStatus = true
					frameBuffReq = append(frameBuffReq, wl.FrameBuffer)
				}
			}
			return
		}()
		if gpuStatus {
			pcie_slot_zero := [1]int{0}
			for _, hyperHxNode := range filteredHxNode {
				//TODO: need to  test
				if reflect.DeepEqual(hyperHxNode.Attrib.PcieSlots, pcie_slot_zero) {
					continue
				}
				usable_gpus := make([]string, 0)

				hyperHxNode.HerculesAvail = false
				for _, gpuName := range hyperHxNode.Attrib.GpuOptions {
					partFrameBuff := GetPartAttrib(gpuName, constants.FRAME_BUFF).([]int)
					for _, frameBuff := range frame_buff_req {
						if utilities.IntInSlice(int(frameBuff), partFrameBuff) {
							usable_gpus = append(usable_gpus, gpuName)
						}
					}
				}
				if len(usable_gpus) > 0 {
					hyperHxNode.Attrib.GpuOptions = usable_gpus
					gpuNode = append(gpuNode, hyperHxNode)
				}
			}
			filteredHxNode = gpuNode
		}
	}
	return filteredHxNode, filteredCoNode
}
