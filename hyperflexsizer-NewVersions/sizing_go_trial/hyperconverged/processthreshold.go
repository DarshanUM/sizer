package hyperconverged

import (
	"cisco_sizer/constants"
	"cisco_sizer/database"
	"cisco_sizer/model"
	"cisco_sizer/structure"
)

var thresholdTable map[string]interface{}
var thresholdsData []model.Threshold

func LoadThreshold() {
	// var thresholds []model.Threshold
	err := model.GetAllThreshold(database.Db, &thresholdsData)
	if err != nil {
		panic(err)
	}

	// for _, threshold := range thresholdTable {
	// 	thresholdTable[threshold.WorkloadType][threshold.ThresholdCategory][threshold.ThresholdKey] = threshold.ThresholdValue
	// }

}

func FetchThresholdData(workloadType string, thresholdCategory int, thresholdKey string, lstWorkload []structure.WorkloadCustom) (thresholdResult float64) {

	num_infra := 0
	switch workloadType {
	case constants.ROBO_BACKUP_SECONDARY:
		workloadType = constants.ROBO
	case constants.ROBO_BACKUP:
		workloadType = constants.VSI
	case constants.VDI, constants.VDI_INFRA:
		if len(lstWorkload) > 0 && thresholdCategory != 3 {
			// TODO : need to start from here 2moro
			num_infra = func() (vdiInfraCount int) {
				for _, workload := range lstWorkload {
					if workload.Attrib.InternalType == constants.VDI_INFRA {
						vdiInfraCount++
					}
				}
				return
			}()

		}
	}

	for _, threshold := range thresholdsData {
		switch threshold.WorkloadType {
		case workloadType:
			switch threshold.ThresholdCategory {
			case thresholdCategory:
				switch threshold.ThresholdKey {
				case thresholdKey:
					if num_infra != 0 {
						thresholdResult -= float64(10 * num_infra)
					}
					return thresholdResult / 100.0
				}
			}
		}
	}
	return 0
}
