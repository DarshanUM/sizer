package model

import (
	"fmt"

	"github.com/jinzhu/gorm"
)

type Threshold struct {
	ID                int    `gorm:"primaryKey"`
	ThresholdKey      string `gorm:"size:15"`
	ThresholdValue    int
	ThresholdCategory int
	WorkloadType      string `gorm:"size:11"`
}

// TableName overrides the table name used by User to `profiles`
func (Threshold) TableName() string {
	return "hyperconverged_thresholds"
}

func GetAllThreshold(db *gorm.DB, threshold *[]Threshold) (err error) {
	//db.Find(node, []int{1, 2, 3})
	err = db.Find(threshold).Error
	// err = db.Where("`name` IN (\"HXAF-240M5SX\",\"HX-C240-M5SX [CTO]\")").Find(node).Error
	if err != nil {
		fmt.Println(err)
		return err
	}
	return err
}

//get_threshold_value
func GetThreshold(db *gorm.DB, workloadType string, thresholdCategory int, thresholdKey string) (thresholdValue int, err error) {
	//db.Find(node, []int{1, 2, 3})
	var threshold Threshold
	err = db.Where("threshold_key = ? AND workload_type= ? AND threshold_category = ?", thresholdKey, workloadType, thresholdCategory).Find(threshold).Error
	// err = db.Where("`name` IN (\"HXAF-240M5SX\",\"HX-C240-M5SX [CTO]\")").Find(node).Error
	if err != nil {
		fmt.Println(err)
		return -1, err
	}
	return threshold.ThresholdValue, nil
}
