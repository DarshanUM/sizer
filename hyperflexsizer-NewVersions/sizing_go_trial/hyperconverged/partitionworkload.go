package hyperconverged

import (
	"cisco_sizer/constants"
	"cisco_sizer/structure"
	"cisco_sizer/utilities"
	"math"
	"sort"
	"strings"
)

type PartitionPart struct {
	Name          string
	PartsNeeded   float64
	ServersNeeded float64
	Price         float64
}

var listPartName map[string][]string

// we can create a global variable as partitionHxNode, which will used only in the partition file
// global variable -- need to handle during concurrency
var partitionSizingDetails partitionSizingInfo

func GetPartitionedList(clusterWorkload *[]structure.WorkloadCustom, hxHyperNode []HyperconvergedNode, wlClusterType string, hyperviser string, setting_json *structure.SettingJson) [][]structure.WorkloadCustom {

	partitionSizingDetails.Hypervisor = hyperviser
	partitionSizingDetails.Workload = *clusterWorkload
	partitionSizingDetails.HxNodeList = hxHyperNode
	if setting_json.HerculesConf != constants.DISABLED {
		partitionSizingDetails.Hercules = true
	}
	if setting_json.HxBoostConf != constants.DISABLED {
		partitionSizingDetails.HxBoost = true
	}

	if len(*clusterWorkload) == 2 && (*clusterWorkload)[0].Attrib.WlName == (*clusterWorkload)[1].Attrib.WlName {
		if (*clusterWorkload)[0].Attrib.ReplicationType == constants.NORMAL {
			return [][]structure.WorkloadCustom{[]structure.WorkloadCustom{(*clusterWorkload)[0]}, []structure.WorkloadCustom{(*clusterWorkload)[1]}}
		} else {
			return [][]structure.WorkloadCustom{[]structure.WorkloadCustom{(*clusterWorkload)[1]}, []structure.WorkloadCustom{(*clusterWorkload)[0]}}
		}
	} else if len(*clusterWorkload) > 1 {
		if wlClusterType == constants.VDI && checkForRDSHWorkload(clusterWorkload) {
			// partitionSizingInfo.VdiGpuExists = True
			return [][]structure.WorkloadCustom{*clusterWorkload}
		}

	} else {
		return [][]structure.WorkloadCustom{*clusterWorkload}
	}
	return [][]structure.WorkloadCustom{*clusterWorkload}
}

func PartitionGpuWorkloads(clusterWorkload *[]structure.WorkloadCustom, hxHyperNode []HyperconvergedNode, wlClusterType string) {
	// filter_any_gpu_wls := func() {

	// }
	wl_gpu_frame_dict := map[string][]int{"P40": []int{3072, 6144, 12288, 24576}, "V100-32": []int{32768}, "any": []int{0, 512, 1024, 2048, 4096, 8192, 16384}}
	// cluster := make([][]structure.WorkloadCustom, 0)

	var wl_gpu_dict = make(map[string][]structure.WorkloadCustom, 0)

	for gpu_key, frame_value := range wl_gpu_frame_dict {
		//wl_gpu_dict[gpu_key]
		wl_gpu_dict[gpu_key] = func() (tempWl []structure.WorkloadCustom) {
			for _, wl := range *clusterWorkload {
				if utilities.IntInSlice(int(wl.FrameBuffer), frame_value) {
					tempWl = append(tempWl, wl)
				}
			}
			return
		}()

	}

	if len(wl_gpu_dict["p40"]) != 0 {
		// partnPreRequirement(wl_gpu_dict["p40"])

	}

}

func partitionPreRequirement(lstWorkload []structure.WorkloadCustom, hxHyperNode []HyperconvergedNode, wlClusterType string) {

	partitionSizingDetails.GetBasicSizingInfo(lstWorkload, wlClusterType)
	GenerateSeedNode(lstWorkload, hxHyperNode)
	// CreateCluster()
}

func GenerateSeedNode(lstWorkload []structure.WorkloadCustom, hxHyperNode []HyperconvergedNode) {
	lstNodeSubType := func() (subType []string) {
		for _, node := range hxHyperNode {
			subType = append(subType, node.Attrib.Subtype)
		}
		return
	}()

	//below
	var node_subtype string = ""
	if partitionSizingDetails.WlClustertype == constants.ROBO || partitionSizingDetails.WlClustertype == constants.ROBO_BACKUP_SECONDARY {
		if utilities.StringInSlice(constants.AF_ROBO_NODE, lstNodeSubType) {
			node_subtype = constants.AF_ROBO_NODE
		} else if utilities.StringInSlice(constants.AF_ROBO_NODE, lstNodeSubType) {
			node_subtype = constants.AF_ROBO_NODE
		} else if utilities.StringInSlice(constants.AF_ROBO_TWO_NODE, lstNodeSubType) {
			node_subtype = constants.AF_ROBO_TWO_NODE
		} else if utilities.StringInSlice(constants.ROBO_TWO_NODE, lstNodeSubType) {
			node_subtype = constants.ROBO_TWO_NODE
		} else if utilities.StringInSlice(constants.ROBO_240, lstNodeSubType) {
			node_subtype = constants.ROBO_240
		} else if utilities.StringInSlice(constants.ROBO_AF_240, lstNodeSubType) {
			node_subtype = constants.ROBO_AF_240
		} else {
			node_subtype = constants.ROBO_NODE
		}
	} else if len(lstNodeSubType) == 1 {
		node_subtype = lstNodeSubType[0]
	} else {
		if utilities.StringInSlice(constants.ALL_FLASH, lstNodeSubType) {
			node_subtype = constants.ALL_FLASH
		} else if utilities.StringInSlice(constants.HYPER, lstNodeSubType) {
			node_subtype = constants.HYPER
		} else if utilities.StringInSlice(constants.ALLNVME_NODE, lstNodeSubType) {
			node_subtype = constants.ALLNVME_NODE
		} else if utilities.StringInSlice(constants.LFF_NODE, lstNodeSubType) {
			node_subtype = constants.LFF_NODE
		} else if utilities.StringInSlice(constants.ALLNVME_NODE_8TB, lstNodeSubType) {
			node_subtype = constants.ALLNVME_NODE_8TB
		} else if utilities.StringInSlice(constants.LFF_12TB_NODE, lstNodeSubType) {
			node_subtype = constants.LFF_12TB_NODE
		} else if utilities.StringInSlice(constants.ALL_FLASH_7_6TB, lstNodeSubType) {
			node_subtype = constants.ALL_FLASH_7_6TB
		} else {
			panic("Unknown node subtype found.")
		}

	}
	partitionRefreshNodeData(node_subtype, hxHyperNode)
	partnPopulatePartList() // skip this code as per refactor
	partList := SolveOptimalPartSeed(node_subtype)

	// Iterate all possible cpus and solve their combinations.
	// If we find a combination, quit early, as the cpu list is sorted on price.

	var config = make(map[string]PartitionPart)
	added := false
	for _, cpuPart := range partList[constants.CPU] {
		config[constants.CPU] = cpuPart
		for _, cap := range []string{constants.RAM, constants.HDD, constants.SSD, constants.VRAM} {
			added = false
			parts := listPartName[cap]
			parts = get_part_combo(cpuPart.Name, parts, partitionSizingDetails.HxNodeList, cap)
			if len(parts) == 0 {
				break
			}
			cap_set := partList[cap]
			part_set := func() (tempList []PartitionPart) {
				for _, part_config := range cap_set {
					if cpuPart.ServersNeeded > part_config.ServersNeeded && utilities.StringInSlice(part_config.Name, parts) {
						tempList = append(tempList, part_config)
						// if one data is added then stop iterating
						break
					}
				}
				return
			}()
			if len(part_set) > 0 {
				added = true
				config[cap] = part_set[0]
			}
			if !added {
				break
			}
		}
		if added {
			break
		}
	}

	//If there is a dimension without a part, solve for the best possible part in that dimension, as the other dimensions are the primary constraining factor
	for _, cap := range []string{constants.RAM, constants.HDD, constants.SSD, constants.VRAM} {
		if cap == constants.VRAM {
			wl_sum := func() (total float64) {
				for _, workload := range partitionSizingDetails.Workload {
					total += workload.GetWorkloadCapsum(cap, partitionSizingDetails.Hercules)
				}
				return
			}()
			if wl_sum == 0 {
				config[constants.VRAM] = PartitionPart{"HX-GPU-T4-16", 0, 0, 0}
				continue
			}
		}
		if _, ok := config[cap]; !ok {
			cap_set := partList[cap]
			parts := listPartName[cap]
			parts = get_part_combo(config[constants.CPU].Name, parts, partitionSizingDetails.HxNodeList, cap)
			if len(parts) > 0 {
				part_set := func() (tempList []PartitionPart) {
					for _, part_config := range cap_set {
						if utilities.StringInSlice(part_config.Name, parts) {
							tempList = append(tempList, part_config)
							// if one data is added then stop iterating
							break
						}
					}
					return
				}()
				if len(part_set) > 0 {
					config[cap] = part_set[0]
				}

			}
		}

		if _, ok := config[cap]; !ok {
			panic("Partiotion - Data_Issue")
		}
	}

	//Initialize new node, as we have a config.
	// newHxHyperNode := init_seed_node(config, node_subtype)
}

//refresh_nodes_slots
func partitionRefreshNodeData(priorityNodeSubType string, hxHyperNode []HyperconvergedNode) {
	var updatedNode []HyperconvergedNode
	var slot_dict = make(map[string][]int, 0)
	var staticOverhead = make(map[string]int, 0)
	anyHercules := false
	anyHxBoost := false

	for _, node := range hxHyperNode {
		switch node.Attrib.Subtype {
		case priorityNodeSubType:
			//filter node based on type
			updatedNode = append(updatedNode, node)
			//set Hercules and HxBoost from final node list
			if partitionSizingDetails.Hercules && !anyHercules && node.HerculesAvail {
				anyHercules = true
			}
			if partitionSizingDetails.Hercules && !anyHxBoost && node.HxBoostAvail {
				anyHxBoost = true
			}
			//slot
			for _, keys := range getSlotKeys() {
				switch keys {
				case constants.CPUSLOT:
					slot_dict[keys] = append(slot_dict[keys], node.Attrib.CpuSocketCount...)
				case constants.RAMSLOT:
					slot_dict[keys] = append(slot_dict[keys], node.Attrib.RamSlots...)
				case constants.HDDSLOT:
					slot_dict[keys] = append(slot_dict[keys], node.Attrib.HddSlots...)
				case constants.SSDSLOT:
					slot_dict[keys] = append(slot_dict[keys], node.Attrib.SsdSlots...)
				case constants.PCIESLOT:
					slot_dict[keys] = append(slot_dict[keys], node.Attrib.PcieSlots...)
				}
			}
			// get MAX of static overhead for CPU, RAM, HDD -- for the
			for _, cap := range []string{constants.CPU, constants.RAM, constants.HDD} {
				switch cap {
				case constants.CPU:
					if node.Attrib.StaticOverhead[partitionSizingDetails.Hypervisor].CPU > staticOverhead[constants.CPU] {
						staticOverhead[constants.CPU] = node.Attrib.StaticOverhead[partitionSizingDetails.Hypervisor].CPU
					}
				case constants.RAM:
					if node.Attrib.StaticOverhead[partitionSizingDetails.Hypervisor].RAM > staticOverhead[constants.RAM] {
						staticOverhead[constants.RAM] = node.Attrib.StaticOverhead[partitionSizingDetails.Hypervisor].RAM
					}
				case constants.HDD:
					if node.Attrib.StaticOverhead[partitionSizingDetails.Hypervisor].HDD > staticOverhead[constants.HDD] {
						staticOverhead[constants.HDD] = node.Attrib.StaticOverhead[partitionSizingDetails.Hypervisor].HDD
					}
				}

			}
		}
	}
	for _, keys := range getSlotKeys() {
		slot_dict[keys] = utilities.RemoveDuplicateValuesInt(slot_dict[keys])
	}

	if partitionSizingDetails.Hercules {
		partitionSizingDetails.Hercules = anyHercules
	}
	if partitionSizingDetails.HxBoost {
		partitionSizingDetails.HxBoost = anyHxBoost
	}
	partitionSizingDetails.SlotDic = slot_dict
	partitionSizingDetails.FilterNode = updatedNode
	partitionSizingDetails.StaticOverHead = staticOverhead
}

//solve_optimal_part_seed
func SolveOptimalPartSeed(nodeSubType string) (partList map[string][]PartitionPart) {
	if partList == nil {
		partList = make(map[string][]PartitionPart)
	}
	var part_list []PartitionPart
	var max_part_list []PartitionPart
	mlom_40_10 := false
	max_mem_limit := 0.0
	thresholdValue := 0.0
	minSlot := 0
	isRoboType := false
	var max_specint float64
	thresholdKey := ""

	isMaxPartListRobo := func(nodeSubType string, cap string, serverNeed float64) bool {
		max_cluster := float64(GetMaxClusterValue(nodeSubType, constants.SMALL_FORM_FACTOR, "esxi", constants.NORMAL, false))
		if cap != constants.HDD {
			max_cluster -= func() (temp float64) {
				for _, workload := range partitionSizingDetails.Workload {
					temp = math.Max(temp, float64(workload.Attrib.FaultTolerance))
				}
				return
			}()
		}
		return serverNeed > max_cluster
	}

	for _, cap := range constants.CAP_LIST {
		//reset  the part data
		part_list = make([]PartitionPart, 0)
		max_part_list = make([]PartitionPart, 0)

		switch cap {
		case constants.CPU, constants.SSD, constants.VRAM:
			thresholdKey = cap
		case constants.HDD:
			thresholdKey = cap
			switch nodeSubType {
			case
				constants.ALL_FLASH,
				constants.ALL_FLASH_7_6TB,
				constants.ALLNVME_NODE,
				constants.ALLNVME_NODE_8TB,
				constants.AF_ROBO_NODE,
				constants.AF_ROBO_TWO_NODE,
				constants.ROBO_AF_240:
				thresholdKey = constants.ALL_FLASH_HDD
			case constants.LFF_NODE, constants.LFF_12TB_NODE:
				thresholdKey = constants.LFF_HDD
			}

		case constants.RAM:
			thresholdKey = cap
			minMemory := constants.MIN_MEMORY
			minSlot = utilities.MinInt(partitionSizingDetails.SlotDic[constants.RAM])
			for _, part := range listPartName[constants.RAM] {
				if strings.Contains(part, constants.CUSTOM) {
					minSlot = 12
				} else if strings.Contains(part, constants.CUSTOM_6SLOT) {
					minSlot = 6
				}
				ramCapacity := minSlot * GetPartAttrib(part, constants.CAPACITY).(int)
				if ramCapacity < minMemory {
					minMemory = ramCapacity
				}
			}
			isMTen := func() (isPresent bool) {
				isPresent = true
				for _, part := range listPartName[constants.VRAM] {
					if !strings.Contains(part, "M10") {
						isPresent = false
						break
					}
				}
				return
			}()
			if isMTen {
				max_mem_limit = 1000
			}
		}
	}
	thresholdValue = FetchThresholdData(partitionSizingDetails.Workload[0].Attrib.InternalType, partitionSizingDetails.ThresholdFactor, thresholdKey, nil)
	for _, cap := range constants.CAP_LIST {
		switch cap {
		case constants.SSD:

			switch nodeSubType {
			case constants.ROBO_NODE, constants.ROBO_TWO_NODE, constants.ROBO_240:
				mlom_40_10 = func() bool {
					for _, part := range listPartName[constants.SSD] {
						if strings.Contains(part, "40G-10G") {
							return true
						}
					}
					return false
				}()
				isRoboType = true
			}
			var pcnt_increase float64
			for _, partSsd := range listPartName[constants.SSD] {

				if mlom_40_10 && !strings.Contains(partSsd, "40G-10G") && isRoboType {
					continue
				}
				for _, workload := range partitionSizingDetails.Workload {
					//
					workload.SetWorkloadIopsCapsum(partitionSizingDetails.Hercules, 0)
					for iops_key := range workload.OriginalIopsSum {

						iops_fac := fetchIopsConvData(partSsd, partitionSizingDetails.ThresholdFactor, partitionSizingDetails.RFString, iops_key, workload.Attrib.StorageProtocol)
						pcnt_increase = 0
						if partitionSizingDetails.Hercules {
							pcnt_increase += constants.HERCULES_IOPS[iops_key]
						}
						if partitionSizingDetails.HxBoost {
							pcnt_increase += constants.HX_BOOST_IOPS[iops_key]
						}

						iops_fac *= (1 + pcnt_increase/100.0)
						max_specint = max_specint / GetPartAttrib(constants.REF_IOPS_CPU, constants.SPECLNT).(float64)
						iops_fac *= FetchThresholdData(workload.Attrib.InternalType, partitionSizingDetails.ThresholdFactor, constants.IOPS, partitionSizingDetails.Workload)

						capsumValue := workload.GetWorkloadCapsum(constants.IOPS, partitionSizingDetails.Hercules) + workload.OriginalIopsSum.JsonParseFloat(iops_key)/iops_fac
						workload.SetWorkloadIopsCapsum(partitionSizingDetails.Hercules, capsumValue)
					}
				}
				wl_sum_group, iops_parts_needed := func() (totalCap float64, totalIops float64) {
					for _, workload := range partitionSizingDetails.Workload {
						totalCap += workload.GetWorkloadCapsum(cap, partitionSizingDetails.Hercules)
						totalIops += workload.GetWorkloadCapsum(constants.IOPS, partitionSizingDetails.Hercules)
					}
					totalIops = math.Ceil(totalIops)
					return
				}()
				part_capacity := GetPartAttrib(partSsd, constants.CAPACITY).(float64)
				cache_parts_needed := math.Ceil(wl_sum_group / part_capacity)
				parts_needed := math.Max(cache_parts_needed, iops_parts_needed)
				price := parts_needed * GetPartAttrib(partSsd, constants.CTO_PRICE).(float64)
				if isRoboType && isMaxPartListRobo(nodeSubType, cap, parts_needed) {
					max_part_list = append(max_part_list, PartitionPart{partSsd, parts_needed, parts_needed, price})
				} else {
					part_list = append(part_list, PartitionPart{partSsd, parts_needed, parts_needed, price})
				}
			}
		case constants.CPU, constants.RAM, constants.HDD, constants.VRAM:
			thresholdKey = cap

			wl_sum := func() (total float64) {
				for _, workload := range partitionSizingDetails.Workload {
					total += workload.GetWorkloadCapsum(cap, partitionSizingDetails.Hercules)
				}
				return
			}()
			max_slot_per_node := 0.0
			for _, part := range listPartName[cap] {
				part_capacity := GetPartAttrib(part, constants.CAPACITY).(float64)
				var slots []int
				switch cap {
				case constants.HDD:
					slots = utilities.MakeRangeInt(utilities.MinInt(partitionSizingDetails.SlotDic[cap]), utilities.MaxInt(partitionSizingDetails.SlotDic[cap]))
				case constants.RAM:
					if strings.Contains(part, constants.CUSTOM) {
						slots = []int{12}
					} else if strings.Contains(part, constants.CUSTOM_6SLOT) {
						slots = []int{6}
					} else {
						slots = partitionSizingDetails.SlotDic[cap]
					}
					slots = func() (tempSlot []int) {
						for _, slot := range slots {
							if float64(slot)*part_capacity <= max_mem_limit {
								tempSlot = append(tempSlot, slot)
							}
						}
						return
					}()

					if len(slots) == 0 {
						continue
					}
				default:
					slots = partitionSizingDetails.SlotDic[cap]
				}
				max_slot_per_node = float64(utilities.MaxInt(slots))
				if cap == constants.VRAM && partitionSizingDetails.Workload[0].Attrib.InternalType == constants.AIML && CheckAnyAimlWorkload(&partitionSizingDetails.Workload) {
					max_slot_per_node = 5
				}

				if cap == constants.VRAM && partitionSizingDetails.VdiGpuExists {
					// TODO: SliceInterfaceToSliceInt may have to implement
					frame_buff_list := GetPartAttrib(part, constants.FRAME_BUFF).([]int)
					count := 0
					for _, workload := range partitionSizingDetails.Workload {

						if utilities.IntInSlice(int(workload.FrameBuffer), frame_buff_list) && workload.Attrib.GpuUsers {
							count++
						}
					}
					if count != len(partitionSizingDetails.Workload) {
						continue
					}
				}
				if cap == constants.CPU {
					current_spec := GetPartAttrib(part, constants.SPECLNT).(float64)
					part_capacity *= current_spec
					max_specint = math.Max(max_specint, current_spec)

					max_mem_limit = math.Max(max_mem_limit, max_slot_per_node*GetPartAttrib(part, constants.RAM_LIMIT).(float64))
				} else if cap == constants.HDD {
					part_capacity /= float64(partitionSizingDetails.HighestRF)
				}
				parts_needed := wl_sum / part_capacity
				part_sum := (parts_needed * part_capacity * thresholdValue) - calcSeedPartOverhead(part, parts_needed, cap, max_slot_per_node, part_capacity)
				for wl_sum > part_sum {
					parts_needed += 1
					part_sum = (parts_needed * part_capacity * thresholdValue) - calcSeedPartOverhead(part, parts_needed, cap, max_slot_per_node, part_capacity)
				}
				if parts_needed == 0 {
					// this condition satisfy only when required parts for the wrokload is zero
					part_list = append(part_list, PartitionPart{part, 0.0, 0.0, 0.0})
					continue
				}
				parts_needed = func() (temp float64) {
					var mod_part_need []int
					for _, slot := range slots {
						if slot != 0 {
							mod_part_need = append(mod_part_need, int(parts_needed)%slot)
						}
					}
					return float64(utilities.MinInt(mod_part_need))
				}()
				servers_needed := math.Ceil(parts_needed / max_slot_per_node)

				if cap == constants.VRAM {
					servers_needed *= GetPartAttrib(part, constants.PCIE_REQ).(float64)
				}

				price := parts_needed * GetPartAttrib(part, constants.CTO_PRICE).(float64)

				if cap == constants.CPU {
					var hypervisor_sw_price float64 = 0
					switch partitionSizingDetails.Hypervisor {
					case "esxi":
						hypervisor_sw_price = 2 * constants.ESX_SOFTWARE_PRICE
					default:
						hypervisor_sw_price = float64(2 * constants.HYPER_V_SOFTWARE_PRICE * GetPartAttrib(part, constants.CAPACITY).(float64))
					}
					orig_sw_cost := hypervisor_sw_price * servers_needed
					price += orig_sw_cost

				}

				if isRoboType && isMaxPartListRobo(nodeSubType, cap, servers_needed) {
					max_part_list = append(max_part_list, PartitionPart{part, parts_needed, servers_needed, price})
				} else {
					part_list = append(part_list, PartitionPart{part, parts_needed, servers_needed, price})
				}
			}
		}
		sort.SliceStable(part_list, func(i, j int) bool {
			return part_list[i].Price < part_list[j].Price
		})
		if isRoboType && len(max_part_list) > 0 {
			sort.SliceStable(max_part_list, func(i, j int) bool {
				return max_part_list[i].Price < max_part_list[j].Price
			})
			part_list = append(part_list, max_part_list...)
		}
		partList[cap] = part_list
	}

	return
}

//calc_seed_part_overhead
func calcSeedPartOverhead(partName string, partCount float64, cap string, maxSlotsPerNode float64, partCapacity float64) (overhead float64) {

	overheadAmt, ok := partitionSizingDetails.StaticOverHead[cap]
	if !ok {
		overheadAmt = 0
	}
	if cap == constants.VRAM && maxSlotsPerNode == 0 {
		maxSlotsPerNode = 1
	}
	node_count := int(math.Ceil(partCount / maxSlotsPerNode))
	overhead = float64(overheadAmt * node_count)
	if cap == constants.HDD {
		hdd_overhead := (float64(overheadAmt) / 100.0) * (partCapacity / float64(partitionSizingDetails.HighestRF))
		overhead = partCount * hdd_overhead
	}
	return
}

//populate_part_list
func partnPopulatePartList() {
	var lstCpuOption = make([]string, 0)
	var lstRamOption = make([]string, 0)
	var lstHddOption = make([]string, 0)
	var lstSsdOption = make([]string, 0)
	var lstGpuOption = make([]string, 0)
	for _, hyperNode := range partitionSizingDetails.HxNodeList {
		lstCpuOption = append(lstCpuOption, hyperNode.Attrib.CpuOptions...)
		lstRamOption = append(lstRamOption, hyperNode.Attrib.RamOptions...)
		lstHddOption = append(lstCpuOption, hyperNode.Attrib.HddOptions...)
		lstSsdOption = append(lstCpuOption, hyperNode.Attrib.SsdOptions...)
		lstGpuOption = append(lstCpuOption, hyperNode.Attrib.GpuOptions...)
	}
	listPartName[constants.CPU] = utilities.RemoveDuplicateValuesString(lstCpuOption)
	listPartName[constants.RAM] = utilities.RemoveDuplicateValuesString(lstRamOption)
	listPartName[constants.HDD] = utilities.RemoveDuplicateValuesString(lstHddOption)
	listPartName[constants.SSD] = utilities.RemoveDuplicateValuesString(lstSsdOption)
	listPartName[constants.VRAM] = utilities.RemoveDuplicateValuesString(lstGpuOption)
}

func get_part_combo(cpuName string, parts []string, node_list []HyperconvergedNode, cap string) []string {

	var cpuNodeOptions = make([]string, 0)
	var capNodeOption = make([]string, 0)

	parts = func() (tempParts []string) {
		for _, node := range node_list {
			cpuNodeOptions = node.Attrib.CpuOptions
			switch cap {
			case constants.RAM:
				capNodeOption = node.Attrib.RamOptions
			case constants.HDD:
				capNodeOption = node.Attrib.HddOptions
			case constants.SSD:
				capNodeOption = node.Attrib.SsdOptions
			case constants.VRAM:
				capNodeOption = node.Attrib.GpuOptions
			}
			for _, part := range parts {
				if utilities.StringInSlice(part, capNodeOption) && utilities.StringInSlice(cpuName, cpuNodeOptions) {
					tempParts = append(tempParts, part)
				}
			}
		}
		return
	}()
	return parts
}

func init_seed_node(config map[string]PartitionPart, nodeSubtype string) HyperconvergedNode {
	var total_price float64
	var newHxNode HyperconvergedNode
	var defaultOverhead = make(map[string]Overhead)
	newHxNode.InitSeedNode("Seed_Node", "cto", nodeSubtype, partitionSizingDetails.Hercules, partitionSizingDetails.HxBoost)
	// newHxNode.Attrib.StaticOverhead[partitionSizingDetails.Hypervisor] = Overhead{0, 0, 0}
	var cpuStaticData int = partitionSizingDetails.StaticOverHead[constants.CPU]
	var ramStaticData int = partitionSizingDetails.StaticOverHead[constants.RAM]
	var hddStaticData int = partitionSizingDetails.StaticOverHead[constants.HDD]

	defaultOverhead[partitionSizingDetails.Hypervisor] = Overhead{cpuStaticData, ramStaticData, hddStaticData}
	newHxNode.Attrib.StaticOverhead = defaultOverhead

	if strings.Contains(config[constants.HDD].Name, "LFF") {
		newHxNode.Attrib.DiskCage = "LFF"
	} else {
		newHxNode.Attrib.DiskCage = "SFF"
	}
	var cpu_price, ram_price, hdd_price, ssd_price, gpu_price float64
	for _, cap := range constants.CAP_LIST {
		switch cap {
		case constants.CPU:
			newHxNode, cpu_price = cpu_parts_price_calculation(cap, config, newHxNode, constants.CTO_PRICE)
			total_price += cpu_price
		case constants.RAM:
			newHxNode, ram_price = ram_parts_price_calculation(cap, config, newHxNode, constants.CTO_PRICE, partitionSizingDetails.SlotDic[cap])
			total_price += ram_price
		case constants.HDD:
			newHxNode, hdd_price = hdd_parts_price_calculation(cap, config, newHxNode, constants.CTO_PRICE, partitionSizingDetails.SlotDic[cap])
			total_price += hdd_price
		case constants.SSD:
			newHxNode, ssd_price = ssd_parts_price_calculation(cap, config, newHxNode, constants.CTO_PRICE)
			total_price += ssd_price

			//TODO: Need to work on
			// new_node.attrib[BaseConstants.IOPS_CONV_FAC] = \
			//         self.iops_conv_fac[new_node.attrib[HyperConstants.SSD_PART]][self.sizer_instance.threshold_factor]
			// newHxNode.Attrib.IopsConvFactor =
		case constants.VRAM:
			//TODO: AIML code to add
			// if self.wl_list[0].attrib[HyperConstants.INTERNAL_TYPE] == HyperConstants.AIML and \
			//             any(wl.attrib['input_type'] == "Video" and wl.attrib['expected_util'] == 'Serious Development'
			//                 for wl in self.wl_list):
			//         max_slots_per_node = 5
			//     else:
			//         max_slots_per_node = 2
			max_slots_per_node := 2
			newHxNode, gpu_price = gpu_parts_price_calculation(cap, config, newHxNode, constants.CTO_PRICE, max_slots_per_node)
			total_price += gpu_price
		}
	}
	newHxNode.Attrib.BasePrice = total_price

	for _, cap := range constants.CAP_LIST {
		newHxNode.CalculateOverhead(cap, partitionSizingDetails.Hypervisor, "", partitionSizingDetails.HxBoost)
		newHxNode.CalculateCapex(cap)
		newHxNode.CalculateCapexOpex()
	}
	return newHxNode
}
