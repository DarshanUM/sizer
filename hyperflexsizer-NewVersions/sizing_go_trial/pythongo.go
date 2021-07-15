package main

import (
	"cisco_sizer/database"
	"cisco_sizer/hyperconverged"
	"cisco_sizer/model"
	"cisco_sizer/structure"
	"encoding/json"
	"fmt"
)

func SolveSizing(settingJson string, workloadJsonList string, filteredNode string, scenarioId int, nodeJsonList string) {
	// var workList map[string]interface{}
	// hyperconverged_node := hyperconverged.SetDeafultValue()

	// var lstNode []map[string]model.Node
	// err := json.Unmarshal([]byte(nodeJsonList), &lstNode)
	// if err != nil {
	// 	panic(err)
	// }

	var parts []model.Part
	part_err := model.GetAllPartsWithStatus(database.Db, &parts, true)
	if part_err != nil {
		panic(part_err)
	}
	// hyperconverged.InitializeParts(parts)
	hyperconverged.InitializeParts(parts)

	var setting_json structure.SettingJson
	err := json.Unmarshal([]byte(settingJson), &setting_json)
	if err != nil {
		panic(err)
	}

	//var lstWorkload []map[string]interface{}
	var lstWorkload []structure.Workload
	err_msg := json.Unmarshal([]byte(workloadJsonList), &lstWorkload)
	if err_msg != nil {
		fmt.Println(err_msg)
	}

	// //loop through
	// for _, workload := range lstWorkload {
	// 	fmt.Println(workload.WlName)

	// }

	// // hyperconverged_node := hyperconverged.SetDeafultValue()
	// var nodes []model.Node
	// err = model.GetAllNode(database.Db, &nodes)
	// if err != nil {
	// 	panic(err)
	// }
	// for _, node := range nodes {
	// 	// fmt.Println(strconv.Itoa(key) + "-->" + strconv.Itoa(value1.ID))
	// 	// hyperconverged_node := hyperconverged.SetDeafultValue()
	// 	var nodeAttrib hyperconverged.NodeAttrib
	// 	// err = json.Unmarshal(node.NodeJson, &hyperconverged_node.Attrib)
	// 	err = json.Unmarshal(node.NodeJson, &nodeAttrib)
	// 	if err != nil {
	// 		panic(err)
	// 	}

	// }

	// For Testing only temporiraly
	var nodeName = []string{"HXAF-240M5SX", "HXAF-240M5SX [1 CPU]", "HX-C240-M5SX [CTO]"}
	var nodesData []model.Node
	err = model.GetNodeByMultipleName(database.Db, &nodesData, nodeName)
	if err != nil {
		panic(err)
	}

	// err = json.Unmarshal(node.NodeJson, &hyperconverged_node.Attrib)
	// if err != nil {
	// 	panic(err)
	// }
	InitializeSizing(lstWorkload, nodesData, &setting_json)
	//get the filtered node from DB
	fmt.Println("")

}

func InitializeSizing(lstWorkload []structure.Workload, nodesData []model.Node, setting_json *structure.SettingJson) {
	//clusters := hyperconverged.InitializeCluster(lstWorkload)
	arrWorkload := hyperconverged.InitializeWorkload(lstWorkload, setting_json.HerculesConf)
	cluster := hyperconverged.InitializeCluster(arrWorkload)
	hyperNode := hyperconverged.LoadNode(nodesData) //
	// TODO: def solve(self, bundle_only): :::: function implemetation has to done inline
	// and also it will depend on the workload :::  ex: for vdi, vsi, ANTHOS, EPIC and AIML is already implemented

	hyperconverged.ValidateWorkload(&cluster, &hyperNode, setting_json)
	sizing_vdi(&cluster, setting_json, &hyperNode)
	sizing_vsi(&cluster, setting_json, &hyperNode)
}

func sizing_vdi(cluster *structure.ClusterType, setting_json *structure.SettingJson, hypernode *hyperconverged.HyperNodeType) {
	if len(cluster.Normal.VDI) == 0 {
		return
	}
	var wlClusterType string = "VDI"
	solve_multi_cluster_general(setting_json.Heterogenous, cluster.Normal.VDI, hypernode, setting_json.BundleOnly, wlClusterType, setting_json)
}

func sizing_vsi(cluster *structure.ClusterType, setting_json *structure.SettingJson, hypernode *hyperconverged.HyperNodeType) {
	var wlClusterType string
	if len(cluster.Normal.ORACLE) > 0 {
		wlClusterType = "ORACLE"
		cluster.Normal.VSI = append(cluster.Normal.VSI, cluster.Normal.ORACLE...)
	} else {
		wlClusterType = "VDI"
	}
	if len(cluster.Normal.VSI) == 0 {
		return
	}
	solve_multi_cluster_general(setting_json.Heterogenous, cluster.Normal.VSI, hypernode, setting_json.BundleOnly, wlClusterType, setting_json)

	// add stretch cluster sizing code base
}

func solve_multi_cluster_general(heterogenous bool, lstWorkload []structure.WorkloadCustom, hypernode *hyperconverged.HyperNodeType, bundleOnly string, wlClusterType string, setting_json *structure.SettingJson) {
	// generic sizing -- for all workload -- except EPIC workload
	filteredHxNode, filteredCoNode := hyperconverged.GetCompatibleNodes(wlClusterType, bundleOnly, &lstWorkload, hypernode)
	filteredHxNode, filteredCoNode = hyperconverged.PrePartitionFilter(&filteredHxNode, &filteredCoNode, &lstWorkload, wlClusterType)
}
