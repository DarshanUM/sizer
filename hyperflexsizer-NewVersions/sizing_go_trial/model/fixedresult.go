package model

import (
	"cisco_sizer/structure"
	"time"
)

type FixedResult struct {
	ID           int            `gorm:"primaryKey"`
	ResultJson   structure.JSON `sql:"type:json" json:"result_json"`
	ClusterName  string         `gorm:"size:45"`
	ScenarioId   int
	CreatedDate  time.Time      `sql:"DEFAULT:current_timestamp;type:datetime"`
	ErrorJson    structure.JSON `sql:"type:json" json:"error_json"`
	SettingsJson structure.JSON `sql:"type:json" json:"settings_json"`
}

// TableName overrides the table name used by User to `profiles`
func (FixedResult) TableName() string {
	return "hyperconverged_fixedresults"
}
