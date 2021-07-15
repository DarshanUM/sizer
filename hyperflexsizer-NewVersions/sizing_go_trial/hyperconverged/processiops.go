package hyperconverged

import (
	"cisco_sizer/constants"
	"cisco_sizer/database"
	"cisco_sizer/model"
)

var iopsTableData []model.IopsConvertionFactor

func LoadIopsConvFactor() {
	if iopsTableData != nil || len(iopsTableData) > 0 {
		return
	}
	err := model.GetAllIopsConvertionFactor(database.Db, &iopsTableData)
	if err != nil {
		panic(err)
	}
}

func fetchIopsConvData(partName string, threshold int, rfString string, workloadType string, wlProtocol string) float64 {
	switch workloadType {
	case constants.ROBO_BACKUP_SECONDARY:
		workloadType = constants.ROBO
	case constants.ROBO_BACKUP:
		workloadType = constants.VSI
	}

	switch workloadType {
	case constants.CONTAINER, constants.AIML, constants.ANTHOS:
		for _, iopsData := range iopsTableData {
			switch iopsData.PartName {
			case partName:
				switch iopsData.Threshold {
				case threshold:
					switch iopsData.ReplicationFactor {
					case rfString:
						switch iopsData.WorkloadType {
						case constants.VSI:
							var iops_val float64
							switch wlProtocol {
							case constants.NFS:
								iops_val = float64(iopsData.IopsConvFactor) * 0.5
							default:
								iops_val = float64(iopsData.IscsiIops) * 0.5
							}
							return iops_val
						}

					}

				}
			}
		}
	default:
		for _, iopsData := range iopsTableData {
			switch iopsData.PartName {
			case partName:
				switch iopsData.Threshold {
				case threshold:
					switch iopsData.ReplicationFactor {
					case rfString:
						switch iopsData.WorkloadType {
						case workloadType:
							switch wlProtocol {
							case constants.NFS:
								return float64(iopsData.IopsConvFactor)
							default:
								return float64(iopsData.IscsiIops)
							}
						}

					}

				}
			}
		}

	}

	return 0.0
}
