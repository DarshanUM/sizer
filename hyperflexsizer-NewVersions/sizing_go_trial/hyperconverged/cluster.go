package hyperconverged

import (
	"cisco_sizer/structure"
	"strings"
)

func InitializeCluster(workloads []structure.WorkloadCustom) structure.ClusterType {
	var cluster structure.ClusterType

	for _, workload := range workloads {
		attrib := workload.Attrib
		switch cluster_type := attrib.ClusterType; strings.ToLower(cluster_type) {

		case "normal":
			switch wl_type := attrib.WlType; wl_type {
			case "VDI", "VDI_INFRA", "RDSH":
				cluster.Normal.VDI = append(cluster.Normal.VDI, workload)
			case "VSI":
				cluster.Normal.VSI = append(cluster.Normal.VSI, workload)
			case "AWR_FILE", "ORACLE", "DB":
				cluster.Normal.ORACLE = append(cluster.Normal.ORACLE, workload)
			case "RAW_FILE":
				cluster.Normal.RAW = append(cluster.Normal.RAW, workload)
			case "SPLUNK":
				cluster.Normal.SPLUNK = append(cluster.Normal.SPLUNK, workload)
			case "CONTAINER":
				cluster.Normal.CONTAINER = append(cluster.Normal.CONTAINER, workload)
			case "ROBO_BACKUP":
				cluster.Normal.ROBO_BACKUP = append(cluster.Normal.ROBO_BACKUP, workload)
			case "ROBO":
				//TODO: checked if taggeg_workload is nil
				if attrib.TaggedWorkload {
					cluster.Normal.ROBO_BACKUP_SECONDARY = append(cluster.Normal.ROBO_BACKUP_SECONDARY, workload)
				} else {
					cluster.Normal.ROBO = append(cluster.Normal.ROBO, workload)
				}
				// case "ROBO_BACKUP_SECONDARY":
			}
		case "stretch":
			switch wl_type := attrib.WlType; wl_type {
			case "VDI", "VDI_INFRA", "RDSH":
				cluster.Normal.VDI = append(cluster.Normal.VDI, workload)
			case "DB", "ORACLE", "VSI", "AWR_FILE":
				cluster.Normal.VSI = append(cluster.Normal.VSI, workload)
			// case "AWR_FILE", "ORACLE":
			// 	cluster.Normal.ORACLE = append(cluster.Normal.ORACLE, workload)
			case "RAW_FILE":
				cluster.Normal.RAW = append(cluster.Normal.RAW, workload)
			case "SPLUNK":
				cluster.Normal.SPLUNK = append(cluster.Normal.SPLUNK, workload)
			case "CONTAINER":
				cluster.Normal.CONTAINER = append(cluster.Normal.CONTAINER, workload)
			case "ROBO_BACKUP":
				cluster.Normal.ROBO_BACKUP = append(cluster.Normal.ROBO_BACKUP, workload)
			case "ROBO":
				//TODO: checked if taggeg_workload is nil
				if attrib.TaggedWorkload {
					cluster.Normal.ROBO_BACKUP_SECONDARY = append(cluster.Normal.ROBO_BACKUP_SECONDARY, workload)
				} else {
					cluster.Normal.ROBO = append(cluster.Normal.ROBO, workload)
				}
				// case "ROBO_BACKUP_SECONDARY":
			}
		}

	}
	return cluster
}

// func InitializeCluster(workloads []structure.WorkloadCustom) structure.ClusterType {
// 	var cluster structure.ClusterType

// 	for _, workload := range workloads {
// 		attrib := workload.Attrib
// 		switch cluster_type := attrib.ClusterType; strings.ToLower(cluster_type) {

// 		case "normal":
// 			switch wl_type := attrib.WlType; wl_type {
// 			case "VDI":
// 				cluster.Normal.VDI = append(cluster.Normal.VDI, workload)
// 			case "VSI":
// 				cluster.Normal.VSI = append(cluster.Normal.VSI, workload)
// 			case "AWR_FILE", "ORACLE":
// 				cluster.Normal.ORACLE = append(cluster.Normal.ORACLE, workload)
// 			case "RAW_FILE":
// 				cluster.Normal.RAW = append(cluster.Normal.RAW, workload)
// 			case "ROBO":
// 				//TODO: checked if taggeg_workload is nil
// 				if attrib.TaggedWorkload {
// 					cluster.Normal.RAW = append(cluster.Normal.RAW, workload)
// 				} else {
// 					cluster.Normal.ROBO_BACKUP_SECONDARY = append(cluster.Normal.ROBO_BACKUP_SECONDARY, workload)
// 				}
// 				// case "ROBO_BACKUP_SECONDARY":
// 			}
// 		case "stretch":
// 			switch wl_type := attrib.WlType; wl_type {
// 			case "VDI":
// 				cluster.Stretch.VDI = append(cluster.Stretch.VDI, workload)
// 			case "VSI":
// 				cluster.Stretch.VSI = append(cluster.Stretch.VSI, workload)
// 			case "AWR_FILE", "ORACLE":
// 				cluster.Stretch.ORACLE = append(cluster.Stretch.ORACLE, workload)
// 			case "RAW_FILE":
// 				cluster.Stretch.RAW = append(cluster.Stretch.RAW, workload)
// 			case "ROBO":
// 				//TODO: checked if taggeg_workload is nil
// 				if attrib.TaggedWorkload {
// 					cluster.Stretch.RAW = append(cluster.Stretch.RAW, workload)
// 				} else {
// 					cluster.Stretch.ROBO_BACKUP_SECONDARY = append(cluster.Stretch.ROBO_BACKUP_SECONDARY, workload)
// 				}
// 				// case "ROBO_BACKUP_SECONDARY":
// 			}
// 		}

// 	}
// 	return cluster
// }

// func InitializeCluster1(workloads []structure.WorkloadCustom) structure.ClusterType {
// 	var cluster structure.ClusterType

// 	for _, workload := range workloads {
// 		attrib := workload.Attrib
// 		switch cluster_type := attrib.ClusterType; strings.ToLower(cluster_type) {

// 		case "normal":
// 			cluster.Normal = append(cluster.Normal, workload)
// 		case "stretch":
// 			cluster.Stretch = append(cluster.Normal, workload)
// 		}

// 	}
// 	return cluster
// }
