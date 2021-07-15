package model

import (
	"cisco_sizer/structure"
	"time"

	"github.com/jinzhu/gorm"
)

type Part struct {
	ID          int            `gorm:"primaryKey"`
	Name        string         `gorm:"size:500" db:"name" json:"name,omitempty"`
	PartJson    structure.JSON `sql:"type:json" db:"part_json" json:"part_json,omitempty"`
	PartName    string         `gorm:"size:100" db:"part_name" json:"part_name,omitempty"`
	Status      int            `gorm:"default:true" db:"status" json:"status,omitempty"`
	CreatedDate time.Time      `sql:"DEFAULT:current_timestamp;type:datetime" db:"created_date" json:"created_date,omitempty"`
	UpdatedDate time.Time      `sql:"DEFAULT:current_timestamp;type:datetime" db:"updated_date" json:"updated_date,omitempty"`
}

// TableName overrides the table name used by User to `profiles`
func (Part) TableName() string {
	return "hyperconverged_part"
}

func GetAllPartsWithStatus(db *gorm.DB, parts *[]Part, status bool) (err error) {
	err = db.Where("status = ?", status).Find(&parts).Error
	if err != nil {
		return err
	}
	return nil
}
