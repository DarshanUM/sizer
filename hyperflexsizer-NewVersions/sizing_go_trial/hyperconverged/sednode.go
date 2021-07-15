package hyperconverged

import "cisco_sizer/constants"

//price_factor
func cpu_parts_price_calculation(cap string, config map[string]PartitionPart, hyperNode HyperconvergedNode, priceFactor string) (HyperconvergedNode, float64) {
	newHyperNode, partName := update_part_name_price_details(cap, config, hyperNode, priceFactor)
	newHyperNode.Attrib.CoresPerCpu = newHyperNode.Attrib.CoresPerCpu * newHyperNode.Attrib.SpecInt
	newHyperNode.Attrib.CpuSocketValue = 2
	cpu_price := GetPartAttrib(partName, constants.CTO_PRICE).(float64)
	cpu_total_price := calculate_total_part_price(cpu_price, float64(newHyperNode.Attrib.CpuSocketValue))
	return newHyperNode, cpu_total_price
}

func ram_parts_price_calculation(cap string, config map[string]PartitionPart, hyperNode HyperconvergedNode, priceFactor string, slots []int) (HyperconvergedNode, float64) {
	return hyperNode, 0
}

func hdd_parts_price_calculation(cap string, config map[string]PartitionPart, hyperNode HyperconvergedNode, priceFactor string, slots []int) (HyperconvergedNode, float64) {
	return hyperNode, 0
}

func ssd_parts_price_calculation(cap string, config map[string]PartitionPart, hyperNode HyperconvergedNode, priceFactor string) (HyperconvergedNode, float64) {
	return hyperNode, 0
}

func gpu_parts_price_calculation(cap string, config map[string]PartitionPart, hyperNode HyperconvergedNode, priceFactor string, maxSlotsPerNode int) (HyperconvergedNode, float64) {
	return hyperNode, 0
}

func update_part_name_price_details(cap string, config map[string]PartitionPart, newHyperNode HyperconvergedNode, priceFactor string) (HyperconvergedNode, string) {
	var configData PartitionPart = config[cap]
	switch cap {
	case constants.CPU:
		newHyperNode.Attrib.CpuPart = configData.Name
		newHyperNode.Attrib.CpuPriceFactor = priceFactor
	case constants.RAM:
		newHyperNode.Attrib.RamPart = configData.Name
		newHyperNode.Attrib.RamPriceFactor = priceFactor
	case constants.HDD:
		newHyperNode.Attrib.HddPart = configData.Name
		newHyperNode.Attrib.HddPriceFactor = priceFactor
	case constants.SSD:
		newHyperNode.Attrib.SsdPart = configData.Name
		newHyperNode.Attrib.SsdPriceFactor = priceFactor
	case constants.VRAM:
		newHyperNode.Attrib.GpuPart = configData.Name
		newHyperNode.Attrib.GpuPriceFactor = priceFactor
	}
	newHyperNode = update_part_details_to_node(cap, configData.Name, newHyperNode)
	return newHyperNode, configData.Name
}

func update_part_details_to_node(cap string, partName string, hyperhxNode HyperconvergedNode) HyperconvergedNode {
	switch cap {
	case constants.CPU:
		hyperhxNode.Attrib.Frequency = GetPartAttrib(partName, constants.FREQUENCY).(float64) //may not work
		hyperhxNode.Attrib.CoresPerCpu = GetPartAttrib(partName, constants.CAPACITY).(float64)
		hyperhxNode.Attrib.SpecInt = GetPartAttrib(partName, constants.SPECLNT).(float64)
		hyperhxNode.Attrib.CpuDescription = GetPartAttrib(partName, constants.DESCRIPTION).(string)
		hyperhxNode.Attrib.Tdp = GetPartAttrib(partName, constants.TDP).(float64)
		hyperhxNode.Attrib.CpuBomName = GetPartAttrib(partName, constants.BOM_NAME).(string)
		hyperhxNode.Attrib.CpuBomDescription = GetPartAttrib(partName, constants.BOM_DESCR).(string)
	case constants.RAM:
		hyperhxNode.Attrib.RamSize = GetPartAttrib(partName, constants.CAPACITY).(float64)
		hyperhxNode.Attrib.RamDescription = GetPartAttrib(partName, constants.DESCRIPTION).(string)
		hyperhxNode.Attrib.RamBomName = GetPartAttrib(partName, constants.BOM_NAME).(string)
		hyperhxNode.Attrib.RamBomDescription = GetPartAttrib(partName, constants.BOM_DESCR).(string)
		hyperhxNode.Attrib.RamBomAddMemoryname = GetPartAttrib(partName, constants.BOM_ADD_MEM).(string)
	case constants.HDD:
		hyperhxNode.Attrib.HddSize = GetPartAttrib(partName, constants.CAPACITY).(float64)
		hyperhxNode.Attrib.HddDescription = GetPartAttrib(partName, constants.DESCRIPTION).(string)
		hyperhxNode.Attrib.HddType = GetPartAttrib(partName, constants.HDD_TYPE).(string)
		hyperhxNode.Attrib.HddBomName = GetPartAttrib(partName, constants.BOM_NAME).(string)
		hyperhxNode.Attrib.HddBomDescription = GetPartAttrib(partName, constants.BOM_DESCR).(string)
	case constants.SSD:
		hyperhxNode.Attrib.SsdSize = GetPartAttrib(partName, constants.CAPACITY).(float64)
		hyperhxNode.Attrib.SsdDescription = GetPartAttrib(partName, constants.DESCRIPTION).(string)
		hyperhxNode.Attrib.SsdOutputCapacity = GetPartAttrib(partName, constants.OUTPUT_CAPACITY).(float64)
		hyperhxNode.Attrib.SsdBomName = GetPartAttrib(partName, constants.BOM_NAME).(string)
		hyperhxNode.Attrib.SsdBomDescription = GetPartAttrib(partName, constants.BOM_DESCR).(string)
	case constants.VRAM:
		hyperhxNode.Attrib.GpuSize = GetPartAttrib(partName, constants.CAPACITY).(float64)
		hyperhxNode.Attrib.GpuDescription = GetPartAttrib(partName, constants.DESCRIPTION).(string)
		hyperhxNode.Attrib.GpuBomName = GetPartAttrib(partName, constants.BOM_NAME).(string)
		hyperhxNode.Attrib.GpuBomDescription = GetPartAttrib(partName, constants.BOM_DESCR).(string)
	}
	return hyperhxNode
}

func calculate_total_part_price(component_price float64, components_required float64) float64 {
	return component_price * components_required
}
