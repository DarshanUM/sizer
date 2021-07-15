package hyperconverged

import (
	"cisco_sizer/constants"
	"cisco_sizer/database"
	"cisco_sizer/model"
	"cisco_sizer/structure"
	"fmt"
	"math"
	"strconv"
	"strings"

	"github.com/mitchellh/mapstructure"
)

func InitializeWorkload(workloads []structure.Workload, herc_conf string) []structure.WorkloadCustom {
	var arrWorkload []structure.WorkloadCustom
	for _, workload := range workloads {
		switch internal_type := workload.InternalType; internal_type {

		case constants.RAW:
			arrWorkload = append(arrWorkload, process_raw_wl(workload, herc_conf))

		case constants.EXCHANGE:
			arrWorkload = append(arrWorkload, process_exchange_wl(workload, herc_conf))
		case constants.VDI:
			new_wl := process_vdi_wl(workload, herc_conf)
			arrWorkload = append(arrWorkload, new_wl)
			if workload.VdiDirectory != 0 {
				arrWorkload = append(arrWorkload, process_vdi_home(new_wl.Attrib, herc_conf))
			}
		case constants.RDSH:
			new_wl := process_rdsh_wl(workload, herc_conf)
			arrWorkload = append(arrWorkload, new_wl)
			if new_wl.Attrib.RdshDirectory != 0 {
				arrWorkload = append(arrWorkload, process_rdsh_home(new_wl.Attrib, herc_conf))
			}
		case constants.VSI:
			arrWorkload = append(arrWorkload, process_vsi_wl(workload, herc_conf))
		case constants.VDI_INFRA:
			arrWorkload = append(arrWorkload, process_infra_vdi_wl(workload, herc_conf))
		case constants.DB:
			arrWorkload = append(arrWorkload, process_db_wl(workload, herc_conf))
		}
	}
	return arrWorkload
}

func process_raw_wl(workload structure.Workload, herc_conf string) structure.WorkloadCustom {
	var wl structure.WorkloadCustom
	wl.InitWorkloadCustom(workload)

	wl.NumInstance = 1

	wl.Compression = (100 - workload.CompressionFactor) / 100
	wl.Dedupe = (100 - workload.DedupeFactor) / 100
	wl.HerculesComp = (100 - constants.HERCULES_COMP) / 100

	// s := reflect.ValueOf(&workload).Elem()
	// typeOfT := s.Type()
	// found_flag := false

	// for i := 0; i<s.NumField(); i++{
	// 	field_name := typeOfT.Field(i).Name
	// 	if field_name == constants.RAW_OVERHEAD_PERCENTAGE{
	// 		found_flag = true
	// 	}
	// }

	if workload.OverheadPercentage != 0 {
		if workload.WlType == constants.RAW_FILE {
			wl.Attrib.OverheadPercentage = 10
		} else {
			wl.Attrib.OverheadPercentage = 0
		}
	}

	raw_calculate_normal(&wl)

	if herc_conf != constants.DISABLED {
		raw_calculate_hercules(&wl)
	}

	return wl
}

func raw_calculate_normal(wl *structure.WorkloadCustom) {
	input_cpu := wl.Attrib.CpuModel

	var cpu_model model.SpecIntData
	var cpu_cores float64

	if input_cpu == "" {
		model.GetSpecIntBaseModel(database.Db, &cpu_model)
	} else {
		model.GetSpectIntModel(database.Db, input_cpu, &cpu_model)
	}

	wl.Capsum.Normal = make(structure.CustomDictionary)

	wl.OriginalIopsSum = make(structure.CustomDictionary)

	safety_overhead := wl.Attrib.OverheadPercentage / 100.0

	for _, cap := range constants.WL_CAP_LIST {

		switch cap {
		case constants.CPU:
			if wl.Attrib.CpuAttribute == constants.CPU_CLOCK {
				vcpus := wl.Attrib.CpuClock / cpu_model.Speed
				cpu_cores = vcpus / float64(wl.Attrib.VcpusPerCore)
			} else {
				cpu_cores = float64(wl.Attrib.Vcpus) / float64(wl.Attrib.VcpusPerCore)
			}
			normalized_cores := cpu_cores * NormalizeCpu(&cpu_model)
			wl.Capsum.Normal[cap] = int(normalized_cores * (1 + safety_overhead))

		case constants.RAM:
			ram_size := UnitConversion(wl.Attrib.RamSize, wl.Attrib.RamSizeUnit, "GiB")

			if wl.Attrib.RamOpratio != 0 {
				ram_size /= wl.Attrib.RamOpratio
			} else {
				ram_size /= 1
			}
			wl.Capsum.Normal[cap] = int(ram_size * (1 + safety_overhead))

		case constants.HDD:
			hdd_size := UnitConversion(wl.Attrib.HddSize, wl.Attrib.HddSizeUnit, "GB")

			effective_hdd := hdd_size * (1 + safety_overhead)

			wl.Capsum.Normal[cap] = effective_hdd * wl.Attrib.Compression * wl.Attrib.Dedupe

			wl.OriginalSize = effective_hdd

		case constants.SSD:
			continue

		case constants.IOPS:
			if wl.Attrib.IoBlockSize != "" {
				wl.OriginalIopsSum[wl.Attrib.IoBlockSize] = wl.Attrib.IopsValue
			} else {
				wl.OriginalIopsSum[wl.Attrib.InternalType] = 0
			}

		case constants.VRAM:
			continue
		}
	}

}

func raw_calculate_hercules(wl *structure.WorkloadCustom) {
	wl.Capsum.Hercules = wl.Capsum.Normal
	wl.Capsum.Hercules[constants.HDD] = wl.Capsum.Normal.JsonParseFloat(constants.HDD) * wl.HerculesComp
}

func process_exchange_wl(workload structure.Workload, herc_conf string) structure.WorkloadCustom {
	var wl structure.WorkloadCustom

	wl.InitWorkloadCustom(workload)

	exchange_calculate_normal(&wl)

	exchange_calculate_hercules(&wl)

	return wl
}

func exchange_calculate_normal(wl *structure.WorkloadCustom) {

	safety_overhead := wl.Attrib.OverheadPercentage / 100.0

	wl.Capsum.Normal = make(structure.CustomDictionary)

	wl.OriginalIopsSum = make(structure.CustomDictionary)

	for _, cap := range constants.WL_CAP_LIST {

		switch cap {
		case constants.CPU:
			cpu_cores := float64(wl.Attrib.Vcpus) / float64(wl.Attrib.VcpusPerCore) * NormalizeCpu(nil)

			wl.Capsum.Normal[cap] = int(cpu_cores * (1 + safety_overhead))

		case constants.RAM:
			if wl.Attrib.RamSizeUnit == "" {
				wl.Attrib.RamSizeUnit = "GiB"
			}
			ram_size := UnitConversion(wl.Attrib.RamSize, wl.Attrib.RamSizeUnit, "GiB")

			wl.Capsum.Normal[cap] = int(ram_size * (1 + safety_overhead))

		case constants.HDD:
			effective_hdd := wl.Attrib.HddSize * (1 + safety_overhead)

			wl.Capsum.Normal[cap] = effective_hdd * wl.Attrib.Compression * wl.Attrib.Dedupe

			wl.OriginalSize = effective_hdd

		case constants.SSD:
			wl.Capsum.Normal[cap] = wl.Attrib.SsdSize * wl.Attrib.Dedupe * float64(wl.Attrib.WorkingSet) / 100.0

		case constants.IOPS:
			wl.OriginalIopsSum[constants.EXCHANGE_32KB] = wl.Attrib.EXCHANGE_32KB
			wl.OriginalIopsSum[constants.EXCHANGE_16KB] = wl.Attrib.EXCHANGE_16KB
			wl.OriginalIopsSum[constants.EXCHANGE_64KB] = wl.Attrib.EXCHANGE_64KB

		case constants.VRAM:
			continue
		}
	}

}

func exchange_calculate_hercules(wl *structure.WorkloadCustom) {
	wl.Capsum.Hercules = wl.Capsum.Normal
	wl.Capsum.Hercules[constants.HDD] = wl.Capsum.Normal.JsonParseFloat(constants.HDD) * wl.HerculesComp
}

func process_vdi_wl(workload structure.Workload, herc_conf string) structure.WorkloadCustom {
	var wl structure.WorkloadCustom
	var HerculesComp int = 10

	wl.InitWorkloadCustom(workload)
	wl.NumInstance = float64((workload.Concurrency / 100) * workload.NumDesktops)

	//TODO: max(6, self.attrib[HyperConstants.RAM_PER_DT] * 2)
	wl.Attrib.InflightDataSize = float64(workload.RamPerDesktop * 2)
	if workload.ReplicationFactor == 0 {
		wl.Attrib.ReplicationFactor = 1
	} else {
		wl.Attrib.ReplicationFactor = workload.ReplicationFactor
	}
	wl.Compression = (100 - workload.CompressionFactor) / 100.0
	wl.Dedupe = (100 - workload.DedupeFactor) / 100.0
	wl.HerculesComp = float64(100-HerculesComp) / 100.0

	vdi_calculate_normal(&wl)
	vdi_calculate_hercules(&wl)
	return wl
}

func vdi_calculate_normal(wl *structure.WorkloadCustom) {
	attrib := wl.Attrib
	if wl.Capsum.Normal == nil {
		wl.Capsum.Normal = make(structure.CustomDictionary)
	}
	var image_size, ssd_multiplier, inflight_dedupe, image_dedupe, snapshot_factor, hdd_size float64

	var baseCpu model.SpecIntData
	err := model.GetSpecIntBaseModel(database.Db, &baseCpu)
	if err != nil {
		panic(err)
	}
	for _, cap := range []string{"CPU", "RAM", "HDD", "SSD", "IOPS", "VRAM"} {
		switch cap {
		case "CPU":
			clock := float64((attrib.ClockPerDesktop / 1000.0) * wl.NumInstance)

			wl.Capsum.Normal["CLOCK"] = clock
			wl.Capsum.Normal[cap] = (clock / baseCpu.Speed) * NormalizeCpu(nil)

		case "RAM":
			if attrib.RamPerDesktopUnit == "" {
				attrib.RamPerDesktopUnit = "GiB"
			}
			var ramPerDesktop float64 = UnitConversion(attrib.RamPerDesktop, attrib.RamPerDesktopUnit, "GiB")
			wl.Capsum.Normal[cap] = ramPerDesktop * wl.NumInstance

		case "HDD":
			inflight_dedupe = (100 - attrib.InflightDedupeFactor) / 100.0
			image_dedupe = (100 - attrib.ImageDedupeFactor) / 100.0
			// inflight_size = attrib.InflightDataSize

			if attrib.VdiDirectory == 0 {
				hdd_size = 0
			} else {
				hdd_size = UnitConversion(attrib.DiskPerDesktop, attrib.DiskPerDesktopUnit, "GB")
			}

			image_size = UnitConversion(attrib.GoldImageSize, attrib.GoldImageSizeUnit, "GB")
			snapshot_factor = attrib.Snapshots*0.02 + 1

			if strings.Contains("Persistent Desktops", attrib.ProvisioningType) {

				wl.UserData = hdd_size * wl.Compression * wl.Dedupe
				wl.OsData = (image_dedupe * image_size)

				wl.Capsum.Normal[cap] = wl.NumInstance * (wl.UserData + wl.OsData) * snapshot_factor

				wl.OriginalSize = wl.NumInstance * (hdd_size + image_size) * snapshot_factor
			} else {

				wl.UserData = hdd_size * wl.Compression * wl.Dedupe
				wl.OsData = attrib.InflightDataSize * inflight_dedupe

				wl.Capsum.Normal[cap] = wl.NumInstance*(wl.UserData+wl.OsData)*snapshot_factor + image_size

				wl.OriginalSize = wl.NumInstance*(hdd_size+attrib.InflightDataSize)*snapshot_factor + image_size
			}

		case "SSD":
			ssd_multiplier = float64(attrib.WorkingSet) / 100.0
			if strings.Contains("Persistent Desktops", attrib.ProvisioningType) {
				wl.Capsum.Normal[cap] = (wl.UserData + wl.OsData) * wl.NumInstance * ssd_multiplier
			} else {
				wl.Capsum.Normal[cap] = ((wl.UserData+wl.OsData)*wl.NumInstance + image_size) * ssd_multiplier
			}

		case "IOPS":
			total_os_iops := attrib.AvgIopsPerDesktop * wl.NumInstance
			wl.OriginalIopsSum[attrib.InternalType] = total_os_iops

		case "VRAM":
			var frame_buff float64 = 0
			//TODO:  make sure UI is sending this property as bool
			if attrib.GpuUsers {
				frame_buff, _ = strconv.ParseFloat(attrib.VideoRAM, 64)
			}
			// As UI Parses Data in MiB, converting data to GiB
			wl.Capsum.Normal[cap] = attrib.NumDesktops * frame_buff / 1024
		}
	}
}

func vdi_calculate_hercules(wl *structure.WorkloadCustom) {
	var image_size, snapshot_factor, ssd_multiplier float64
	attrib := wl.Attrib

	if wl.Capsum.Hercules == nil {
		wl.Capsum.Hercules = make(structure.CustomDictionary)
	}

	wl.Capsum.Hercules = wl.Capsum.Normal

	for _, cap := range []string{"HDD", "SSD"} {
		switch cap {
		case "HDD":
			image_size = UnitConversion(attrib.GoldImageSize, attrib.GoldImageSizeUnit, "GB")
			snapshot_factor = attrib.Snapshots*0.02 + 1
			wl.UserData = wl.UserData * wl.HerculesComp

			if strings.Contains("Persistent Desktops", attrib.ProvisioningType) {
				wl.Capsum.Hercules[cap] = wl.NumInstance * (wl.UserData + wl.OsData) * snapshot_factor
			} else {
				wl.Capsum.Hercules[cap] = wl.NumInstance*(wl.UserData+wl.OsData)*snapshot_factor + image_size
			}
		case "SSD":
			ssd_multiplier = float64(attrib.WorkingSet) / 100.0

			if strings.Contains("Persistent Desktops", attrib.ProvisioningType) {
				wl.Capsum.Hercules[cap] = (wl.UserData + wl.OsData) * wl.NumInstance * ssd_multiplier
			} else {
				wl.Capsum.Hercules[cap] = ((wl.UserData+wl.OsData)*wl.NumInstance + image_size) * ssd_multiplier
			}

		}
	}
}

func process_vdi_home(workload structure.Workload, herc_conf string) structure.WorkloadCustom {
	var wl structure.WorkloadCustom
	wl.InitWorkloadCustom(workload)

	wl.NumInstance = workload.NumDesktops
	vdi_home_calculate_normal(&wl)
	if herc_conf != "disabled" {
		vdi_home_calculate_hercules(&wl)
	}
	wl.Attrib.InternalType = "VDI_HOME"

	// below code base need to check if it is required to add
	// self.attrib = {attr: self.attrib[attr] for attr in ["profile","primary_wl_name","replication_factor",
	//                                                     "wl_name","wl_type", "fault_tolerance", "number_of_vms",
	//                                                     "internal_type", "cluster_type", "concurrency",
	//                                                     "storage_protocol"]}
	return wl
}

func vdi_home_calculate_normal(wl *structure.WorkloadCustom) {
	attrib := wl.Attrib
	attrib.PrimaryWlName = attrib.WlName
	attrib.WlName += "_HOME"
	var total_iops float64 = attrib.UserIops * float64(wl.NumInstance)
	var total_hdd_size float64 = UnitConversion(attrib.DiskPerDesktop, attrib.DiskPerDesktopUnit, "GB") * float64(wl.NumInstance)
	var homeConfig = structure.GetHomeConfig()

	if wl.Capsum.Normal == nil {
		wl.Capsum.Normal = make(structure.CustomDictionary)
	}

Profileloop:
	for profile, vm_detail := range homeConfig {
		switch profile {
		case "Small", "Medium":
			if vm_detail.MaxData >= total_hdd_size && vm_detail.MaxIops >= total_iops {
				attrib.NumberOfVms = 1
				attrib.Profile = profile
				break Profileloop
			}
		case "Large":
			attrib.NumberOfVms = int(math.Ceil(math.Max(total_hdd_size/vm_detail.MaxData, total_iops/vm_detail.MaxIops)))
			attrib.Profile = profile
		}
	}
	num_active_vms := attrib.Concurrency / 100.0 * float64(attrib.NumberOfVms)

	for _, cap := range []string{"CPU", "RAM", "HDD", "SSD", "IOPS", "VRAM"} {
		switch cap {
		case "CPU":
			wl.Capsum.Normal[cap] = (homeConfig[attrib.Profile].Cpu) * NormalizeCpu(nil) * num_active_vms

		case "RAM":
			wl.Capsum.Normal[cap] = (homeConfig[attrib.Profile].Ram) * num_active_vms
		case "HDD":
			wl.OriginalSize = 0

		case "IOPS":
			wl.OriginalIopsSum["VDI_HOME"] = attrib.UserIops * wl.NumInstance
		}
	}
}

func vdi_home_calculate_hercules(wl *structure.WorkloadCustom) {
	wl.Capsum.Hercules = wl.Capsum.Normal
}

func process_rdsh_wl(workload structure.Workload, herc_conf string) structure.WorkloadCustom {
	var wl structure.WorkloadCustom

	wl.InitWorkloadCustom(workload)

	var min_cores_per_vm int

	wl.Compression = (100 - workload.CompressionFactor) / 100.0
	wl.Dedupe = (100 - workload.DedupeFactor) / 100.0
	wl.HerculesComp = float64(100-constants.HERCULES_COMP) / 100.0

	if wl.Attrib.SessionsPerVm != 0 {
		wl.Attrib.NumVms = float64(wl.Attrib.TotalUsers / wl.Attrib.SessionsPerVm)
	}

	// Amount of GHz required by one VM
	wl.ClockPerVM = float64(wl.Attrib.ClockPerSession / 1000 * wl.Attrib.SessionsPerVm)

	if wl.Attrib.MaxVcpusPerCore != 0 {
		min_cores_per_vm = wl.Attrib.VcpusPerVm / wl.Attrib.MaxVcpusPerCore
	}

	if min_cores_per_vm != 0 {
		wl.MaxClockPerCore = wl.ClockPerVM / float64(min_cores_per_vm)
	}

	wl.OriginalSize = 0

	rdsh_calculate_normal(&wl)
	if herc_conf != constants.DISABLED {
		rdsh_calculate_hercules(&wl)
	}

	return wl
}

func rdsh_calculate_normal(wl *structure.WorkloadCustom) {
	attrib := wl.Attrib
	var image_size, ssd_multiplier, hdd_size float64

	if wl.Capsum.Normal == nil {
		wl.Capsum.Normal = make(structure.CustomDictionary)
	}

	var baseCpu model.SpecIntData
	err := model.GetSpecIntBaseModel(database.Db, &baseCpu)
	if err != nil {
		panic(err)
	}
	for _, cap := range constants.WL_CAP_LIST {
		switch cap {
		case constants.CPU:

			wl.Capsum.Normal[cap] = (float64(attrib.ClockPerSession) / 1000) * float64(attrib.TotalUsers) / baseCpu.Speed * NormalizeCpu(nil)

		case constants.RAM:
			if attrib.RamPerDesktopUnit == "" {
				wl.Attrib.RamPerDesktopUnit = "GiB"
			}
			ram_per_vm := UnitConversion(attrib.RamPerVm, attrib.RamPerVmUnit, "GiB")
			wl.Capsum.Normal[cap] = ram_per_vm * float64(wl.NumVms)

		case constants.HDD:
			if attrib.RdshDirectory == 0 {
				hdd_size = 0
			} else {
				hdd_size = UnitConversion(float64(attrib.HddPerUser), attrib.HddPerUserUnit, "GB")
			}

			image_size = UnitConversion(float64(attrib.OsPerVm), attrib.OsPerVmUnit, "GB")

			wl.UserData = hdd_size * float64(attrib.TotalUsers)
			wl.OsData = image_size * float64(wl.NumVms)

			wl.Capsum.Normal[cap] = (wl.UserData + wl.Compression*wl.Dedupe) + wl.OsData

			wl.OriginalSize = wl.UserData + wl.OsData

		case constants.SSD:

			ssd_multiplier = float64(attrib.WorkingSet) / 100.0
			wl.Capsum.Normal[cap] = (wl.UserData + wl.OsData) * ssd_multiplier

		case constants.IOPS:
			wl.OriginalIopsSum[attrib.InternalType] = 0

		case constants.VRAM:
			if attrib.GpuUsers {
				wl.FrameBuffer, _ = strconv.ParseFloat(attrib.VideoRAM, 64)
			}
			// As UI Parses Data in MiB, converting data to GiB
			wl.Capsum.Normal[cap] = float64(attrib.NumVms) * wl.FrameBuffer / 1024
		}
	}
}

func rdsh_calculate_hercules(wl *structure.WorkloadCustom) {

	wl.Capsum.Hercules = wl.Capsum.Normal

	for _, cap := range constants.WL_CAP_LIST {
		switch cap {
		case constants.HDD:
			wl.Capsum.Hercules[cap] = (wl.UserData * wl.Compression * wl.Dedupe * wl.HerculesComp) + wl.OsData
		}
	}
}

func process_rdsh_home(workload structure.Workload, herc_conf string) structure.WorkloadCustom {
	var wl structure.WorkloadCustom
	wl.InitWorkloadCustom(workload)

	wl.NumInstance = float64(workload.TotalUsers)
	rdsh_home_calculate_normal(&wl)
	if herc_conf != constants.DISABLED {
		rdsh_home_calculate_hercules(&wl)
	}
	wl.Attrib.InternalType = constants.RDSH_HOME

	// below code base need to check if it is required to add
	// self.attrib = {attr: self.attrib[attr] for attr in ["profile","primary_wl_name","replication_factor",
	//                                                     "wl_name","wl_type", "fault_tolerance", "number_of_vms",
	//                                                     "internal_type", "cluster_type", "concurrency",
	//                                                     "storage_protocol"]}
	return wl
}

func rdsh_home_calculate_normal(wl *structure.WorkloadCustom) {
	attrib := wl.Attrib
	wl.Attrib.PrimaryWlName = attrib.WlName
	wl.Attrib.WlName += "_HOME"

	var total_iops float64 = attrib.UserIops * float64(wl.NumInstance)
	var total_hdd_size float64 = UnitConversion(float64(attrib.HddPerUser), attrib.HddPerUserUnit, "GB") * float64(wl.NumInstance)
	var homeConfig = structure.GetHomeConfig()

	if wl.Capsum.Normal == nil {
		wl.Capsum.Normal = make(structure.CustomDictionary)
	}

Profileloop:
	for profile, vm_detail := range homeConfig {
		switch profile {
		case "Small", "Medium":
			if vm_detail.MaxData >= total_hdd_size && vm_detail.MaxIops >= total_iops {
				wl.Attrib.NumberOfVms = 1
				wl.Attrib.Profile = profile
				break Profileloop
			}
		case "Large":
			wl.Attrib.NumberOfVms = int(math.Ceil(math.Max(total_hdd_size/vm_detail.MaxData, total_iops/vm_detail.MaxIops)))
			attrib.Profile = profile
		}
	}

	for _, cap := range constants.WL_CAP_LIST {
		switch cap {
		case constants.CPU:
			wl.Capsum.Normal[cap] = (homeConfig[attrib.Profile].Cpu) * NormalizeCpu(nil) * float64(wl.Attrib.NumberOfVms)

		case constants.RAM:
			wl.Capsum.Normal[cap] = (homeConfig[attrib.Profile].Ram) * float64(wl.Attrib.NumberOfVms)
		case constants.HDD:
			wl.OriginalSize = 0

		case constants.IOPS:
			wl.OriginalIopsSum[constants.RDSH_HOME] = attrib.UserIops * wl.NumInstance
		}
	}
}

func rdsh_home_calculate_hercules(wl *structure.WorkloadCustom) {
	wl.Capsum.Hercules = wl.Capsum.Normal
}

func process_vsi_wl(workload structure.Workload, herc_conf string) structure.WorkloadCustom {
	var HerculesComp int = 10
	var wl structure.WorkloadCustom
	wl.InitWorkloadCustom(workload)

	wl.NumInstance = 0
	//Need to check below codebase
	// wl.Attrib.Snapshots
	// if HyperConstants.VM_SNAPSHOTS not in self.attrib:
	//     self.attrib[HyperConstants.VM_SNAPSHOTS] = 0
	// if 'remote' not in self.attrib:
	// self.attrib['remote'] = False
	if wl.Attrib.ReplicationFactor == 0 {
		wl.Attrib.ReplicationMult = 1
	} else {
		wl.Attrib.ReplicationMult = float64(wl.Attrib.ReplicationFactor)
	}
	if wl.Attrib.ReplicationAmount == 0 {
		wl.Attrib.ReplicationMult = 100
	}

	wl.Compression = (100 - workload.CompressionFactor) / 100.0
	wl.Dedupe = (100 - workload.DedupeFactor) / 100.0
	wl.HerculesComp = float64(100-HerculesComp) / 100.0

	vsi_calculate_normal(&wl, "normal")

	if herc_conf != "disabled" {
		vsi_calculate_hercules(&wl)
	}
	return wl
}

func vsi_calculate_normal(wl *structure.WorkloadCustom, workloadType string) {
	attrib := wl.Attrib
	var ssd_multiplier float64
	if wl.Capsum.Normal == nil {
		wl.Capsum.Normal = make(structure.CustomDictionary)
	}
	if workloadType == "replicated" {
		wl.NumInstance = (math.Ceil(attrib.ReplicationAmount * float64(attrib.NumVms) / 100.0))
	} else {
		wl.NumInstance = float64(attrib.NumVms)
	}

	for _, cap := range []string{"CPU", "RAM", "HDD", "SSD", "IOPS", "VRAM"} {
		switch cap {
		case "CPU":
			if attrib.VcpusPerCore != 0 {
				wl.Capsum.Normal[cap] = (float64(attrib.VcpusPerVm) / float64(attrib.VcpusPerCore)) * NormalizeCpu(nil) * float64(wl.NumInstance)
			}

		case "RAM":
			if attrib.RamPerVmUnit == "" {
				attrib.RamPerVmUnit = "GiB"
			}

			ram_per_vm := UnitConversion(attrib.RamPerVm, attrib.RamPerVmUnit, "GiB")

			wl.Capsum.Normal[cap] = ram_per_vm * float64(wl.NumInstance)
		case "HDD":
			hdd_size := UnitConversion(attrib.DiskPerVm, attrib.DiskPerVmUnit, "GB")
			image_size := UnitConversion(attrib.BaseImageSize, attrib.BaseImageSizeUnit, "GB")

			wl.OriginalSize = wl.NumInstance * (hdd_size + image_size + (0.02 * hdd_size * attrib.Snapshots))
			wl.Capsum.Normal[cap] = wl.OriginalSize * wl.Compression * wl.Dedupe

		case "SSD":
			if wl.Dedupe != 0 {
				ssd_multiplier = float64(attrib.WorkingSet) / 100.0 * wl.Dedupe
			}
			wl.Capsum.Normal[cap] = wl.OriginalSize * ssd_multiplier

		case "IOPS":
			var total_iops, iops_per_vm float64
			iops_per_vm = float64(attrib.AvgIopsPerVm)
			switch workloadType {
			case "normal":
				num_replicated_vms := math.Ceil(attrib.NumVms * attrib.ReplicationAmount / 100.0)
				total_iops = iops_per_vm * ((wl.NumInstance - num_replicated_vms) + (num_replicated_vms * 1.3))
				wl.ReplicationTraffic = iops_per_vm * num_replicated_vms * 0.3

			default:
				if workloadType == "replicated" && attrib.ReplicationAmount > 0 {
					total_iops = iops_per_vm * wl.NumInstance * 1.3
					wl.ReplicationTraffic = iops_per_vm * wl.NumInstance * 0.3
				} else {
					total_iops = iops_per_vm * wl.NumInstance
				}
			}
			wl.OriginalIopsSum[attrib.InternalType] = total_iops
		}
	}
}
func vsi_calculate_hercules(wl *structure.WorkloadCustom) {
	wl.Capsum.Hercules = wl.Capsum.Normal
	wl.Capsum.Hercules["HDD"] = wl.Capsum.Hercules.JsonParseFloat("HDD") * wl.HerculesComp

}

func process_infra_vdi_wl(workload structure.Workload, herc_conf string) structure.WorkloadCustom {
	var wl structure.WorkloadCustom
	wl.InitWorkloadCustom(workload)

	wl.NumInstance = 1

	wl.Compression = (100 - workload.CompressionFactor) / 100
	wl.Dedupe = (100 - workload.DedupeFactor) / 100
	wl.HerculesComp = (100 - constants.HERCULES_COMP) / 100

	wl.OriginalIopsSum = nil

	infra_vdi_calculate_normal(&wl)

	if herc_conf != constants.DISABLED {
		infra_vdi_calculate_hercules(&wl)
	}

	return wl
}

func infra_vdi_calculate_normal(wl *structure.WorkloadCustom) {

	wl.Capsum.Normal = make(structure.CustomDictionary)
	wl.OriginalIopsSum = make(structure.CustomDictionary)

	for _, cap := range constants.WL_CAP_LIST {
		for _, detail := range wl.Attrib.VmDetails {
			vm_detail_interface := detail.(map[string]interface{})
			var vm_detail structure.CustomDictionary
			err := mapstructure.Decode(vm_detail_interface, &vm_detail)
			if err != nil {
				fmt.Println(err)
			}
			switch cap {
			case constants.CPU:
				if wl.Capsum.Normal[cap] != nil {
					wl.Capsum.Normal[cap] = wl.Capsum.Normal[cap].(float64) + vm_detail.JsonParseFloat(constants.VCPUS_PER_VM)/float64(wl.Attrib.VcpusPerCore)*NormalizeCpu(nil)*vm_detail.JsonParseFloat(constants.NUM_VM)
				} else {
					wl.Capsum.Normal[cap] = vm_detail.JsonParseFloat(constants.VCPUS_PER_VM) / float64(wl.Attrib.VcpusPerCore) * NormalizeCpu(nil) * vm_detail.JsonParseFloat(constants.NUM_VM)
				}

			case constants.RAM:
				if _, ok := vm_detail[constants.RAM_PER_VM_UNIT]; !ok {
					vm_detail[constants.RAM_PER_VM_UNIT] = "GiB"
				}
				ram_per_vm := UnitConversion(vm_detail.JsonParseFloat(constants.RAM_PER_VM), vm_detail.JsonParseString(constants.RAM_PER_VM_UNIT), "GiB")

				if wl.Capsum.Normal[cap] != nil {
					wl.Capsum.Normal[cap] = wl.Capsum.Normal[cap].(float64) + (ram_per_vm/wl.Attrib.RamOpratio)*vm_detail.JsonParseFloat(constants.NUM_VM)
				} else {
					wl.Capsum.Normal[cap] = (ram_per_vm / wl.Attrib.RamOpratio) * vm_detail.JsonParseFloat(constants.NUM_VM)
				}

			case constants.HDD:
				hdd_size := UnitConversion(vm_detail.JsonParseFloat(constants.HDD_PER_VM), vm_detail.JsonParseString(constants.HDD_PER_VM_UNIT), "GB")

				if wl.Capsum.Normal[cap] != nil {
					wl.Capsum.Normal[cap] = wl.Capsum.Normal[cap].(float64) + (vm_detail.JsonParseFloat(constants.NUM_VM) * hdd_size * wl.Compression * wl.Dedupe)
				} else {
					wl.Capsum.Normal[cap] = (vm_detail.JsonParseFloat(constants.NUM_VM) * hdd_size * wl.Compression * wl.Dedupe)
				}

				wl.OriginalSize += hdd_size * vm_detail.JsonParseFloat(constants.NUM_VM)

			case constants.SSD:
				continue

			case constants.IOPS:
				wl.OriginalIopsSum[wl.Attrib.InternalType] = 0

			case constants.VRAM:
				continue
			}
		}
	}

}

func infra_vdi_calculate_hercules(wl *structure.WorkloadCustom) {
	wl.Capsum.Hercules = wl.Capsum.Normal
	wl.Capsum.Hercules[constants.HDD] = wl.Capsum.Normal.JsonParseFloat(constants.HDD) * wl.HerculesComp
}

func process_db_wl(workload structure.Workload, herc_conf string) structure.WorkloadCustom {
	var wl structure.WorkloadCustom
	wl.InitWorkloadCustom(workload)

	wl.NumInstance = 0

	if wl.Attrib.ReplicationFactor == 0 {
		wl.Attrib.ReplicationMult = 1
	} else {
		wl.Attrib.ReplicationMult = float64(wl.Attrib.ReplicationFactor)
	}

	if wl.Attrib.ReplicationAmount == 0 {
		wl.Attrib.ReplicationAmount = 100
	}

	//Ignoring because the default value is always false for bool field in struct
	// if !(wl.Attrib.Remote) {
	// wl.Attrib.Remote = false
	// }

	db_calculate_normal(&wl, "")

	if herc_conf != constants.DISABLED {
		db_calculate_hercules(&wl, "")
	}

	return wl
}

func db_calculate_normal(wl *structure.WorkloadCustom, workload_type string) bool {
	if wl.Attrib.WlType == constants.AWR_FILE {
		wl.Attrib.NumDbInstances = 1
	}

	if workload_type == "" {
		workload_type = constants.NORMAL
	}

	if workload_type == constants.REPLICATED {
		wl.NumInstance = wl.Attrib.ReplicationAmount * wl.Attrib.NumDbInstances / 100
	} else {
		wl.NumInstance = wl.Attrib.NumDbInstances
	}

	ComputeDedupe(wl, wl.Attrib.CompressionFactor, wl.Attrib.DedupeFactor)

	for _, cap := range constants.WL_CAP_LIST {
		switch cap {
		case constants.HDD:
			wl.Capsum.Normal[cap], wl.OriginalSize = get_hdd_value(wl, "normal")
		case constants.IOPS:
			wl.OriginalIopsSum[wl.Attrib.InternalType] = get_iops_value(wl, workload_type)
		case constants.CPU:
			wl.Capsum.Normal[cap] = get_cpu_value(wl)
		case constants.RAM:
			wl.Capsum.Normal[cap] = get_ram_value(wl)
		case constants.SSD:
			wl.Capsum.Normal[cap] = get_ssd_value(wl)
		}
	}
	return true

}

func db_calculate_hercules(wl *structure.WorkloadCustom, workload_type string) {
	wl.Capsum.Hercules = wl.Capsum.Normal
	for _, cap := range constants.WL_CAP_LIST {
		switch cap {
		case constants.HDD:
			wl.Capsum.Normal[cap], wl.OriginalSize = get_hdd_value(wl, "normal")
		case constants.IOPS:
			wl.OriginalIopsSum[wl.Attrib.InternalType] = get_iops_value(wl, workload_type)
		case constants.CPU:
			wl.Capsum.Normal[cap] = get_cpu_value(wl)
		case constants.RAM:
			wl.Capsum.Normal[cap] = get_ram_value(wl)
		case constants.SSD:
			wl.Capsum.Normal[cap] = get_ssd_value(wl)
		}
	}
	wl.Capsum.Hercules[constants.HDD] = wl.Capsum.Normal.JsonParseFloat(constants.HDD) * wl.HerculesComp
}

func ComputeDedupe(wl *structure.WorkloadCustom, compute_factor float64, dedupe_factor float64) {
	wl.Compression = (100 - compute_factor) / 100.0
	wl.Dedupe = (100 - dedupe_factor) / 100.0
	wl.HerculesComp = (100 - constants.HERCULES_COMP) / 100.0
}

func get_cpu_value(wl *structure.WorkloadCustom) float64 {
	cpu_capacity := wl.Attrib.VcpusPerDb / float64(wl.Attrib.VcpusPerCore)
	var cpu_model model.SpecIntData
	input_cpu := ""
	if wl.Attrib.WlType == constants.AWR_FILE {
		input_cpu = wl.Attrib.CpuModel
	}
	if input_cpu == "" {
		err := model.GetSpecIntBaseModel(database.Db, &cpu_model)
		if err != nil {
			fmt.Println("Error in GetSpecIntBaseModel")
			panic(err)
		}
	} else {
		err := model.GetSpectIntModel(database.Db, input_cpu, &cpu_model)
		if err != nil {
			fmt.Println("Error in GetSpectIntModel")
			panic(err)
		}
	}

	cpu_capacity *= NormalizeCpu(&cpu_model)
	return wl.NumInstance * cpu_capacity

}

func get_ram_value(wl *structure.WorkloadCustom) float64 {
	if wl.Attrib.RamPerDbUnit == "" {
		wl.Attrib.RamPerDbUnit = "GiB"
	}
	ram_capacity := UnitConversion(wl.Attrib.RamPerDb, wl.Attrib.RamPerDbUnit, "GiB")

	return wl.NumInstance * ram_capacity
}

func get_ssd_value(wl *structure.WorkloadCustom) float64 {
	ssd_capacity := UnitConversion(wl.Attrib.DbSize, wl.Attrib.DbSizeUnit, "GB") * 0.2 * wl.Dedupe
	return wl.NumInstance * ssd_capacity
}

func get_hdd_value(wl *structure.WorkloadCustom, node_type string) (float64, float64) {
	var total_hdd_capacity float64

	db_size := UnitConversion(wl.Attrib.DbSize, wl.Attrib.DbSizeUnit, "GB")
	total_base_size := db_size * (1 + wl.Attrib.MetaDataSize/100.0)
	original_size := wl.NumInstance * total_base_size

	switch node_type {
	case "normal":
		hdd_capacity := total_base_size * wl.Compression * wl.Dedupe
		total_hdd_capacity = wl.NumInstance * hdd_capacity
	case "hercules":
		hdd_capacity := total_base_size * wl.Compression * wl.Dedupe * wl.HerculesComp
		total_hdd_capacity = wl.NumInstance * hdd_capacity
	}
	return total_hdd_capacity, original_size
}

func get_iops_value(wl *structure.WorkloadCustom, workload_type string) float64 {
	var iops_value float64
	iops_cap := wl.Attrib.AvgIopsPerDb

	switch workload_type {
	case constants.NORMAL:
		num_replicated_dbs := (wl.NumInstance * wl.Attrib.ReplicationAmount) / 100.0
		iops_value = iops_cap*(wl.NumInstance-num_replicated_dbs) + (num_replicated_dbs * 1.3)
		wl.ReplicationTraffic = iops_cap * num_replicated_dbs * 0.3
	case constants.REPLICATED:
		if wl.Attrib.ReplicationAmount != 0 {
			iops_value = iops_cap * wl.NumInstance * 1.3
			wl.ReplicationTraffic = iops_cap * wl.NumInstance * 0.3
		}
	default:
		iops_value = iops_cap * wl.NumInstance
	}
	return iops_value
}

func SumWorkloadRequirement(lstWorkload *[]structure.WorkloadCustom, cap string, hercules bool) float64 {
	var totalReq float64 = 0
	switch cap {
	case constants.CPU:
		for _, workload := range *lstWorkload {
			totalReq += workload.GetWorkloadCapsum(cap, hercules)
		}
	}
	return totalReq
}

// used in validation.go and processnode.go file  --- used for validation
func CheckAllAimlWorkload(lstWorkload *[]structure.WorkloadCustom) bool {
	var count int
	for _, workload := range *lstWorkload {
		if workload.Attrib.InputType == "Video" && workload.Attrib.ExpectedUtil == "Serious Development" {
			count++
		}
	}
	return count == len(*lstWorkload)
}

func CheckAnyAimlWorkload(lstWorkload *[]structure.WorkloadCustom) bool {
	for _, workload := range *lstWorkload {
		if workload.Attrib.InputType == "Video" && workload.Attrib.ExpectedUtil == "Serious Development" {
			return true
		}
	}
	return false
}

// check if all the aiml workloads has  ['input_type'] == 'Text Input', then return true else false
func CheckAllAimlInputType(lstWorkload *[]structure.WorkloadCustom) bool {
	var count int
	for _, workload := range *lstWorkload {
		if workload.Attrib.InputType == "Text Input" {
			count++
		}
	}
	return count == len(*lstWorkload)
}

//TODO need to move the below files to common place
func NormalizeCpu(hostCpu *model.SpecIntData) float64 {
	// if (model.SpecIntData{}) == hostCpu {
	if hostCpu == nil {
		return 1
	}
	var base_blended_core, host_blended_core float64
	var baseCpu model.SpecIntData
	model.GetSpecIntBaseModel(database.Db, &baseCpu)
	if hostCpu.BlendedCore2017 != 0 {
		base_blended_core = baseCpu.BlendedCore2017
		host_blended_core = hostCpu.BlendedCore2017
	} else {
		base_blended_core = baseCpu.BlendedCore2006
		host_blended_core = hostCpu.BlendedCore2006
	}
	return host_blended_core / base_blended_core
}
