package model

import (
	"cisco_sizer/structure"
	"time"
)

type Result struct {
	ID           int `gorm:"primaryKey"`
	ScenarioId   int
	Name         string
	ResultJson   structure.JSON `sql:"type:json" json:"result_json"`
	SettingsJson structure.JSON `sql:"type:json" json:"settings_json"`
	ErrorJson    structure.JSON `sql:"type:json" json:"error_json"`
	CreatedDate  time.Time      `sql:"DEFAULT:current_timestamp;type:datetime"`
}

// TableName overrides the table name used by User to `profiles`
func (Result) TableName() string {
	return "hyperconverged_results"
}
