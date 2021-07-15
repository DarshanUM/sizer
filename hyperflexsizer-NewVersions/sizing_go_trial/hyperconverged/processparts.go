package hyperconverged

import (
	"cisco_sizer/constants"
	"cisco_sizer/model"
	"encoding/json"
	"fmt"
	"strconv"
)

var lstParts map[string]PartJson
var lstPartsCapSum = make(map[string][]PartJson)

type PartJson struct {
	PartName          string
	Speclnt           float64     `json:"speclnt"`
	Capacity          int         `json:"capacity"`
	OutputCapacity    string      `json:"output_capacity"`
	Description       string      `json:"description"`
	ServerType        string      `json:"server_type"`
	Type              string      `json:"type"`
	UnitPrice         int         `json:"unit_price"`
	Frequency         string      `json:"frequency"`
	BomName           string      `json:"bom_name"`
	BomDescription    string      `json:"bom_description"`
	CtoPrice          int         `json:"cto_price"`
	Tdp               string      `json:"tdp"`
	L3Cache           string      `json:"l3_cache"`
	FilterTag         interface{} `json:"filter_tag"`
	FrameBuffer       []int       `json:"frame_buff"`
	RamLimit          int         `json:"ram_limit"`
	PcieReq           float64     `json:"pcie_req"`
	BomAddMemoryName  string      `json:"bom_add_memory_name"`
	HddAdditionalPart string      `json:"hdd_add_part"`
	HddType           string      `json:"hdd_type"`
}

// var lstParts []CustomParts

// type CustomParts struct {
// 	Name   string `json:"name"`
// 	Attrib model.PartJson
// }

// func (customPart *CustomParts) Initialize(part model.Part) {
// 	customPart.Name = part.Name
// 	json.Unmarshal(part.PartJson, &customPart.Attrib)
// }

// func InitializeParts(arrParts []model.Part) {
// 	var newPart CustomParts
// 	for _, part := range arrParts {
// 		newPart.Initialize(part)
// 		lstParts = append(lstParts, newPart)
// 	}
// }

func InitializeParts(arrParts []model.Part) {
	if lstParts != nil {
		return
	}
	for _, part := range arrParts {
		var part_json PartJson
		if lstParts == nil {
			lstParts = make(map[string]PartJson)
		}
		err := json.Unmarshal(part.PartJson, &part_json)
		if err != nil {
			fmt.Println("Error unmarshal", err)
		}
		json.Unmarshal(part.PartJson, &part_json)
		part_json.PartName = part.Name
		lstParts[part.Name] = part_json

		switch part_json.Type {
		case constants.CPU:
			lstPartsCapSum[constants.CPU] = append(lstPartsCapSum[constants.CPU], part_json)
		case constants.RAM:
			lstPartsCapSum[constants.RAM] = append(lstPartsCapSum[constants.RAM], part_json)
		case constants.HDD:
			lstPartsCapSum[constants.HDD] = append(lstPartsCapSum[constants.HDD], part_json)
		case constants.SSD:
			lstPartsCapSum[constants.SSD] = append(lstPartsCapSum[constants.SSD], part_json)
		case constants.VRAM:
			lstPartsCapSum[constants.VRAM] = append(lstPartsCapSum[constants.VRAM], part_json)
		}
	}
}

func GetPartAttrib(partName string, attribName string) interface{} {
	PartJson := lstParts[partName]
	switch attribName {
	case constants.FREQUENCY:
		return PartJson.GetCPUFrequency()
	case constants.CAPACITY:
		return PartJson.GetCapacity()
	case constants.FilterTag:
		return PartJson.GetPartFilterTag()
	case constants.FRAME_BUFF:
		return PartJson.GetGPUFrameBuffer()
	case constants.SPECLNT:
		return PartJson.GetCPUSpecLnt()
	case constants.RAM_LIMIT:
		return PartJson.GetCPURamLimit()
	case constants.PCIE_REQ:
		return PartJson.GetPcieRequirement()
	case constants.CTO_PRICE:
		return PartJson.GetCtoPrice()
	case constants.TDP:
		return PartJson.GetTdp()
	case constants.BOM_NAME:
		return PartJson.GetBomName()
	case constants.BOM_DESCR:
		return PartJson.GetBomDescription()
	case constants.DESCRIPTION:
		return PartJson.GetPartDescription()
	case constants.BOM_ADD_MEM:
		return PartJson.GetBomAdditionalMemoryName()
	case constants.HDD_TYPE:
		return PartJson.GetHddType()
	case constants.OUTPUT_CAPACITY:
		return PartJson.GetSsdOutputCapacity()
	}

	return ""
}

func (partAttrib *PartJson) GetSsdOutputCapacity() string {
	return partAttrib.OutputCapacity
}

func (partAttrib *PartJson) GetHddType() string {
	return partAttrib.HddType
}

func (partAttrib *PartJson) GetBomAdditionalMemoryName() string {
	return partAttrib.BomAddMemoryName
}

func (partAttrib *PartJson) GetPartDescription() string {
	return partAttrib.Description
}

func (partAttrib *PartJson) GetBomName() string {
	return partAttrib.BomName
}

func (partAttrib *PartJson) GetBomDescription() string {
	return partAttrib.BomDescription
}

func (partAttrib *PartJson) GetTdp() string {
	return partAttrib.Tdp
}

func (partAttrib *PartJson) GetCPUFrequency() string {
	return partAttrib.Frequency
}

// for all parts
func (partAttrib *PartJson) GetCapacity() int {
	return partAttrib.Capacity
}

// for all parts - GPU and HDD = string and rest of the parts = []string
func (partAttrib *PartJson) GetPartFilterTag() interface{} {
	return partAttrib.FilterTag
}

func (partAttrib *PartJson) GetGPUFrameBuffer() []int {
	return partAttrib.FrameBuffer
}

func (partAttrib *PartJson) GetCPUSpecLnt() float64 {
	return partAttrib.Speclnt
}

func (partAttrib *PartJson) GetCPURamLimit() float64 {
	return float64(partAttrib.RamLimit)
}

func (partAttrib *PartJson) GetPcieRequirement() float64 {
	return partAttrib.PcieReq
}

func (partAttrib *PartJson) GetCtoPrice() float64 {
	return float64(partAttrib.CtoPrice)
}

func GetHxCpuClock() map[string]float64 {
	hx_cpu_clock := make(map[string]float64)
	for part_name, part_json := range lstParts {
		frequency, err := strconv.ParseFloat(part_json.Frequency, 64)
		if err == nil {
			hx_cpu_clock[part_name] = frequency
		}
	}
	return hx_cpu_clock
}
