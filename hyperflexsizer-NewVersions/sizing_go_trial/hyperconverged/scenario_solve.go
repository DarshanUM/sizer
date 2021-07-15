package hyperconverged

import (
	"cisco_sizer/constants"
	"cisco_sizer/database"
	"cisco_sizer/model"
	"cisco_sizer/utilities"
	"encoding/json"
	"fmt"
	_ "go/constant"
	"reflect"
	"strings"

	"github.com/juliangruber/go-intersect"
)

func FilterNodeAndPartData(filters string, result_name string, disk_option, cache_option string, server_type string, hypervisor string,
	hercules string, cpu_ram_gen string, hx_boost string, free_disk_slots int) []model.Node {

	var return_Nodes []model.Node

	var Nodes []model.Node
	var Parts []model.Part

	node_err := model.GetAllNodesWithStatus(database.Db, &Nodes, true)
	if node_err != nil {
		return return_Nodes
	}

	part_err := model.GetAllPartsWithStatus(database.Db, &Parts, true)
	if part_err != nil {
		return return_Nodes
	}

	InitializeParts(Parts)

	hx_cpu_clock := GetHxCpuClock()

	for _, each_node := range Nodes {
		node_json := NodeAttrib{}
		value, err := each_node.NodeJson.MarshalJSON()
		if err == nil {
			json.Unmarshal(value, &node_json)
		} else {
			fmt.Println(err)
			continue
		}
		if server_type != "ALL" {
			if !(strings.Contains(node_json.Name, server_type)) {
				continue
			}
		}

		if hypervisor == "hyperv" {
			for i, hdd_part := range node_json.HddOptions {
				if strings.Contains(hdd_part, "12TB") {
					node_json.HddOptions = append(node_json.HddOptions[:i], node_json.HddOptions[i+1:]...)
				}
			}
			each_node.HerculesAvail = false
			each_node.HxBoostAvail = false

			if strings.Contains(each_node.Name, "[SED]") || strings.Contains(each_node.Name, "[NVME]") {
				continue
			}
		}

		switch result_name {
		case "All-Flash":
			if !(utilities.StringInSlice(node_json.Subtype, []string{constants.COMPUTE, constants.AIML_NODE})) && !(strings.Contains(each_node.Name, "AF")) {
				continue
			}
		case "All NVMe":
			if !(utilities.StringInSlice(node_json.Subtype, []string{constants.COMPUTE})) && !(strings.Contains(each_node.Name, "NVME")) {
				continue
			}
		}

		// if result_name == "All-Flash" && !(utilities.StringInSlice(node_json.Subtype, []string{constants.COMPUTE, constants.AIML_NODE})) && !(strings.Contains(each_node.Name, "AF")) {
		// 	continue
		// }

		// if result_name == "All NVMe" && !(utilities.StringInSlice(node_json.Subtype, []string{constants.COMPUTE})) && !(strings.Contains(each_node.Name, "NVME")) {
		// 	continue
		// }

		var filters_json map[string]interface{}

		// Remove this replace when passing json.dumps(filter) from python code
		filters = strings.Replace(filters, "'", "\"", 100)

		er := json.Unmarshal([]byte(filters), &filters_json)
		if er != nil {
			fmt.Println(err)
			return return_Nodes
		}

		if val, ok := filters_json["Node_Type"]; ok && val != nil {
			if !(utilities.StringInSlice(node_json.Subtype, []string{"compute", "veeam", constants.AIML_NODE})) {
				node_interfaces := val.([]interface{})
				if len(node_interfaces) > 0 {
					node_filters := utilities.SliceInterfaceToSliceString(node_interfaces)
					for_else_bool := false
					for _, node_filter := range node_filters {
						if strings.Contains(node_filter, "[LFF]") && node_json.Subtype == constants.LFF_NODE {
							node_filter_part := strings.Split(node_filter, " ")
							if strings.Contains(each_node.Name, node_filter_part[0]) {
								for_else_bool = true
								break
							} else {
								continue
							}
						} else if strings.Contains(node_filter, "[7.6TB]") && node_json.Subtype == constants.ALL_FLASH_7_6TB {
							node_filter_part := strings.Split(node_filter, " ")
							if strings.Contains(each_node.Name, node_filter_part[0]) {
								for_else_bool = true
								break
							} else {
								continue
							}
						} else if strings.Contains(node_filter, "[NVME]") && node_json.Subtype == constants.ALLNVME_NODE {
							node_filter_part := strings.Split(node_filter, " ")
							if strings.Contains(each_node.Name, node_filter_part[0]) {
								for_else_bool = true
								break
							} else {
								continue
							}
						} else if strings.Contains(node_filter, "[1 CPU]") && strings.Contains(each_node.Name, "1 CPU") {
							node_filter_part := strings.Split(node_filter, " ")
							if strings.Contains(each_node.Name, node_filter_part[0]) {
								for_else_bool = true
								break
							} else {
								continue
							}
						} else if utilities.StringInSlice(node_json.Subtype, []string{constants.ROBO_NODE, constants.AF_ROBO_NODE}) {
							if strings.Contains(node_filter, "[SD EDGE]") {
								node_filter_part := strings.Split(node_filter, " ")
								if strings.Contains(each_node.Name, node_filter_part[0]) {
									for_else_bool = true
									break
								} else {
									continue
								}
							}
							if !(strings.Contains(each_node.Name, "M5SD")) {
								if strings.Contains(each_node.Name, node_filter) {
									for_else_bool = true
									break
								}
							}
						} else if !(utilities.StringInSlice(node_json.Subtype, []string{constants.ALLNVME_NODE, constants.LFF_NODE})) && strings.Contains(each_node.Name, node_filter) && node_json.DiskCage == "SFF" {
							for_else_bool = true
							break
						}
					}
					if !(for_else_bool) {
						continue
					}
				}
			}
		}

		if val, ok := filters_json["Compute_Type"]; ok && val != nil && utilities.StringInSlice(node_json.Subtype, []string{constants.COMPUTE, constants.AIML_NODE}) {
			compute_interfaces := val.([]interface{})
			if len(compute_interfaces) > 0 {
				compute_filters := utilities.SliceInterfaceToSliceString(compute_interfaces)
				for_else_bool := false
				for _, compute_filter := range compute_filters {
					compute_filter_split := strings.Split(compute_filter, "-")
					if strings.Contains(each_node.Name, compute_filter_split[0]) && strings.Contains(each_node.Name, compute_filter_split[1]) {
						for_else_bool = true
						break
					}
				}
				if !(for_else_bool) {
					continue
				}
			}
		}

		if cpu_ram_gen != "ALL" {
			var cpu_intersect_list []string
			for _, node_cpu := range node_json.CpuOptions {
				filter_tag_interface := GetPartAttrib(node_cpu, "filter_tag")
				filter_tag := utilities.SliceInterfaceToSliceString(filter_tag_interface.([]interface{}))
				if utilities.StringInSlice(cpu_ram_gen, filter_tag) {
					cpu_intersect_list = append(cpu_intersect_list, node_cpu)
				}
			}
			if len(cpu_intersect_list) == 0 {
				continue
			}

			node_json.CpuOptions = cpu_intersect_list

			var ram_intersect_list []string
			for _, node_ram := range node_json.RamOptions {
				filter_tag_interface := GetPartAttrib(node_ram, "filter_tag")
				filter_tag := utilities.SliceInterfaceToSliceString(filter_tag_interface.([]interface{}))
				if utilities.StringInSlice(cpu_ram_gen, filter_tag) {
					ram_intersect_list = append(ram_intersect_list, node_ram)
				}
			}
			if len(ram_intersect_list) == 0 {
				continue
			}

			node_json.RamOptions = ram_intersect_list

		}

		if val, ok := filters_json["CPU_Type"]; ok && val != nil {
			cpu_interfaces := val.([]interface{})
			if len(cpu_interfaces) > 0 {
				cpu_filters := utilities.SliceInterfaceToSliceString(cpu_interfaces)
				var cpu_intersect_list []string
				for _, node_cpu := range node_json.CpuOptions {
					filter_tag_interface := GetPartAttrib(node_cpu, "filter_tag")
					filter_tag := utilities.SliceInterfaceToSliceString(filter_tag_interface.([]interface{}))
					for _, cpu_type := range cpu_filters {
						if utilities.StringInSlice(strings.Split(cpu_type, " (")[0], filter_tag) {
							cpu_intersect_list = append(cpu_intersect_list, node_cpu)
							break
						}
					}
				}
				if len(cpu_intersect_list) == 0 {
					continue
				}

				node_json.CpuOptions = cpu_intersect_list
			}
		}

		if val, ok := filters_json["Clock"]; ok && val != nil {
			clock_interfaces := val.([]interface{})
			if len(clock_interfaces) > 0 {
				clock_filters := utilities.SliceInterfaceToSliceString(clock_interfaces)
				cpu_options := node_json.CpuOptions
				var cpu_intersect_list []string
				for _, cpu_part := range cpu_options {
					if utilities.StringInSlice(fmt.Sprintf("%.1f", hx_cpu_clock[strings.Split(cpu_part, "_")[0]]), clock_filters) {
						cpu_intersect_list = append(cpu_intersect_list, cpu_part)
					}
				}
				if len(cpu_intersect_list) == 0 {
					continue
				}

				node_json.CpuOptions = cpu_intersect_list
			}
		}

		if val, ok := filters_json["RAM_Slots"]; ok && val != nil {
			ram_interfaces := val.([]interface{})
			if len(ram_interfaces) > 0 {
				ram_filters := make([]int, len(ram_interfaces))
				for i, v := range ram_interfaces {
					ram_filters[i] = int(v.(float64))
				}
				intersection := intersect.Simple(node_json.RamSlots, ram_filters).([]interface{})
				intersection_slice := utilities.SliceInterfaceToSliceInt(intersection)

				if len(intersection_slice) == 0 {
					continue
				}
				node_json.RamSlots = intersection_slice
			}
		}

		if val, ok := filters_json["RAM_Options"]; ok && val != nil {
			ram_interfaces := val.([]interface{})
			if len(ram_interfaces) > 0 {
				ram_filters := utilities.SliceInterfaceToSliceString(ram_interfaces)
				var ram_intersect_list []string
				for _, node_ram := range node_json.RamOptions {
					filter_tag_interface := GetPartAttrib(node_ram, "filter_tag")
					filter_tag := utilities.SliceInterfaceToSliceString(filter_tag_interface.([]interface{}))
					var slot_filters []int

					if val, ok := filters_json["RAM_Slots"]; ok && val != nil {
						slot_interfaces := val.([]interface{})
						for _, v := range slot_interfaces {
							slot_filters = append(slot_filters, int(v.(float64)))
						}
					}

					for _, ram_type := range ram_filters {
						if utilities.StringInSlice(ram_type, filter_tag) {
							if !(strings.Contains(node_ram, "[CUSTOM]")) || len(slot_filters) == 0 || utilities.IntInSlice(12, slot_filters) || strings.Contains(node_ram, "[CUSTOM_6SLOT]") {
								ram_intersect_list = append(ram_intersect_list, node_ram)
							}
							break
						}
					}
				}

				if len(ram_intersect_list) == 0 {
					continue
				}
				node_json.RamOptions = ram_intersect_list
			}
		}

		if val, ok := filters_json["GPU_Type"]; ok && val != nil {
			gpu_interfaces := val.([]interface{})
			if len(gpu_interfaces) > 0 {
				gpu_filters := utilities.SliceInterfaceToSliceString(gpu_interfaces)
				zero_int_list := []int{0}
				if !(reflect.DeepEqual(node_json.PcieSlots, zero_int_list)) {
					var gpu_intersect_list []string
					for _, node_gpu := range node_json.GpuOptions {
						filter_tag_interface := GetPartAttrib(node_gpu, "filter_tag")
						filter_tag := filter_tag_interface.(string)
						for _, gpu_type := range gpu_filters {
							if gpu_type == filter_tag {
								gpu_intersect_list = append(gpu_intersect_list, node_gpu)
								break
							}
						}
					}
					if len(gpu_intersect_list) == 0 {
						node_json.PcieSlots = zero_int_list
						node_json.GpuOptions = make([]string, 0)
					} else {
						node_json.GpuOptions = gpu_intersect_list
					}
				} else {
					node_json.GpuOptions = make([]string, 0)
				}
			}
		}

		if !(utilities.StringInSlice(node_json.Subtype, []string{"compute", constants.AIML_NODE})) {
			if hercules == "disabled" {
				each_node.HerculesAvail = false
			} else if hercules == "forced" {
				if !(each_node.HerculesAvail) {
					continue
				}
				node_json.PcieSlots = []int{0}
			}

			if hx_boost == "disabled" {
				each_node.HxBoostAvail = false
			} else if hx_boost == "forced" {
				if !(each_node.HxBoostAvail) {
					continue
				}
			}

			min_hdd_slots := utilities.MinInt(node_json.HddSlots)
			max_hdd_slots := utilities.MaxInt(node_json.HddSlots)

			if (free_disk_slots > max_hdd_slots) || ((max_hdd_slots - min_hdd_slots) < free_disk_slots) {
				continue
			}

			if (disk_option == "LFF" && node_json.DiskCage != "LFF") || (disk_option == "SED" && !(strings.Contains(each_node.Name, "[SED]"))) || (disk_option == "NON-SED" && !(strings.Contains(each_node.Name, "[SED]"))) {
				continue
			}

			if disk_option == "FIPS" {
				var disk_intersect_list []string
				for _, node_hdd := range node_json.HddOptions {
					if strings.Contains(node_hdd, disk_option) {
						disk_intersect_list = append(disk_intersect_list, node_hdd)
					}
				}
				if len(disk_intersect_list) == 0 {
					continue
				}

				node_json.HddOptions = disk_intersect_list
			}

			if val, ok := filters_json["Disk_Options"]; ok && val != nil {
				disk_interfaces := val.([]interface{})
				if len(disk_interfaces) > 0 {
					disk_filters := make([]string, len(disk_interfaces))
					for i, v := range disk_interfaces {
						disk_filters[i] = fmt.Sprint(v)
					}
					var disk_intersect_list []string
					for _, node_hdd := range node_json.HddOptions {
						for _, disk_type := range disk_filters {
							if strings.Contains(node_hdd, strings.Split(disk_type, " ")[0]) && ((strings.Contains(disk_type, "NVMe") && strings.Contains(node_hdd, "NVMe")) || (strings.Contains(disk_type, "SSD") && strings.Contains(node_hdd, "SSD")) || (strings.Contains(disk_type, "HDD") && strings.Contains(node_hdd, "HDD"))) {
								disk_intersect_list = append(disk_intersect_list, node_hdd)
								break
							}
						}
					}
					if len(disk_intersect_list) == 0 {
						continue
					}

					node_json.HddOptions = disk_intersect_list
				}
			}
			if cache_option != "ALL" {
				var ssd_intersect_list []string
				for _, ssd := range node_json.SsdOptions {
					if strings.Contains(ssd, cache_option) {
						ssd_intersect_list = append(ssd_intersect_list, ssd)
					}
				}
				if len(ssd_intersect_list) == 0 {
					continue
				}
				node_json.SsdOptions = ssd_intersect_list
			}

			if val, ok := filters_json["Cache_Options"]; ok && val != nil {
				cache_interfaces := val.([]interface{})
				if len(cache_interfaces) > 0 {
					cache_filters := make([]string, len(cache_interfaces))
					for i, v := range cache_interfaces {
						cache_filters[i] = fmt.Sprint(v)
					}
					var cache_intersect_list []string
					for _, node_ssd := range node_json.SsdOptions {
						for _, cache_type := range cache_filters {
							if strings.Contains(node_ssd, strings.Split(cache_type, " ")[0]) {
								cache_intersect_list = append(cache_intersect_list, node_ssd)
								break
							}
						}
					}
					if len(cache_intersect_list) == 0 {
						continue
					}

					node_json.SsdOptions = cache_intersect_list
				}
			}

			gen_list := []string{"Sky", "Cascade"}
			for _, gen := range gen_list {
				if utilities.All(node_json.CpuOptions, gen) {
					var ram_list []string
					for _, ram := range node_json.RamOptions {
						if strings.Contains(ram, gen) {
							ram_list = append(ram_list, ram)
						}
					}
					node_json.RamOptions = ram_list
				} else if utilities.All(node_json.RamOptions, gen) {
					var cpu_list []string
					for _, cpu := range node_json.CpuOptions {
						if strings.Contains(cpu, gen) {
							cpu_list = append(cpu_list, cpu)
						}
					}
					node_json.CpuOptions = cpu_list
				}
			}

			if !(len(node_json.CpuOptions) > 0 && len(node_json.RamOptions) > 0) {
				continue
			}
		}

		returnNode := each_node
		returnNode.NodeJson, err = json.Marshal(node_json)
		if err != nil {
			fmt.Println(err)
			fmt.Println("Error updating the node_json into Node")
		}
		return_Nodes = append(return_Nodes, returnNode)
		fmt.Println(each_node.ID)

	}
	data, err := json.Marshal(return_Nodes)
	if err == nil {
		fmt.Println(string(data))
	}
	return return_Nodes
}
