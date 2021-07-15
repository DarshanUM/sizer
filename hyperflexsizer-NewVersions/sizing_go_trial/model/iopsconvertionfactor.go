package model

import (
	"fmt"

	"github.com/jinzhu/gorm"
)

type IopsConvertionFactor struct {
	ID int `gorm:"primaryKey"`

	Threshold         int    `gorm:"check: threshold in (0,1,2)"`
	IopsConvFactor    int    `gorm:"default:0"`
	ReplicationFactor string `gorm:"column:replication_factor;size:10;default:general;check: scen_label in ('general','archive','fav')"`
	WorkloadType      string `gorm:"size:30;"`
	PartName          string `gorm:"size:30;"`
	Hypervisor        int    `gorm:"default:0;check: threshold in (0,1)"`
	IscsiIops         int    `gorm:"default:0"`
}

// TableName overrides the table name used by User to `profiles`
func (IopsConvertionFactor) TableName() string {
	return "hyperconverged_iopsconvfactor"
}

func GetAllIopsConvertionFactor(db *gorm.DB, iopsConvFactor *[]IopsConvertionFactor) (err error) {
	err = db.Find(iopsConvFactor).Error
	if err != nil {
		fmt.Println(err)
		return err
	}
	return err
}
