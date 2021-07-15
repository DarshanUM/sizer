package hyperconverged

import (
	"cisco_sizer/constants"
	"cisco_sizer/structure"
	"strings"
)

//validate teh workload -first
func ValidateWorkload(cluster *structure.ClusterType, hyperNode *HyperNodeType, setting_json *structure.SettingJson) {
	if (len(cluster.Normal.ROBO) > 0 || len(cluster.Normal.ROBO_BACKUP_SECONDARY) > 0 || len(cluster.Stretch.ROBO) > 0 || len(cluster.Stretch.ROBO_BACKUP_SECONDARY) > 0) && (len(hyperNode.CtoRoboNode) == 0 && len(hyperNode.BundleRoboNode) == 0) {
		panic("No_ROBO_Nodes |")
	}

	if setting_json.BundleOnly == constants.BUNDLE_ONLY && len(hyperNode.BundleHxNode) == 0 && len(hyperNode.BundleAFNode) == 0 && len(hyperNode.CtoRoboNode) == 0 && len(hyperNode.BundleRoboNode) == 0 {
		panic("No_HC_Nodes ")
	}
	if setting_json.BundleOnly == constants.BUNDLE_ONLY && setting_json.Heterogenous && len(hyperNode.BundleCoNode) == 0 {
		panic("No_Compute_Nodes")
	}

}

func ValidateNodeList(hxnodelist *[]HyperconvergedNode, wlClusterType *string, wl_list *[]structure.WorkloadCustom) {

	switch *wlClusterType {
	case constants.ORACLE:
		if len(*hxnodelist) == 0 {
			panic("No_DB_Nodes")
		}
	case constants.SPLUNK:
		if len(*hxnodelist) == 0 {
			panic("SPLUNK_AF_Nodes")
		}
	case constants.VDI, constants.RDSH:
		if SumWorkloadRequirement(wl_list, "VRAM", false) > 0 && !CheckNodesPcieSlots(hxnodelist) {
			panic("No_GPU_Nodes")
		}
	case constants.AIML:
		if !CheckNodesPcieSlots(hxnodelist) && !CheckAllAimlWorkload(wl_list) {
			panic("No_GPU_Nodes")
		}
	default:
		if len(*hxnodelist) == 0 {
			panic("No Hyperflex nodes could be selected due to filters, Please check the filters")
		}
	}

}

//
func checkForRDSHWorkload(lstWorkload *[]structure.WorkloadCustom) bool {
	for _, wl := range *lstWorkload {
		if wl.Attrib.GpuUsers {
			return true
		}
	}
	return false
}

func checkForAllM10VRam(partRam []PartJson) bool {

	for _, part := range partRam {
		if !strings.Contains(part.PartName, "M10") {
			return false
		}
	}
	return true
}

func checkForAny40G10GSsd(partRam []PartJson) bool {

	for _, part := range partRam {
		if strings.Contains(part.PartName, "40G-10G") {
			return true
		}
	}
	return false
}
