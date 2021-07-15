package model

import (
	"cisco_sizer/structure"
	"time"

	"github.com/jinzhu/gorm"
)

type Scenario struct {
	ID             int            `gorm:"primaryKey"`
	Name           string         `gorm:"size:500"`
	WorkloadJson   structure.JSON `sql:"type:json" json:"workload_json,omitempty"`
	WorkloadResult structure.JSON `sql:"type:json" json:"workload_result"`
	Status         bool           `gorm:"default:true"`
	CreatedDate    time.Time      `sql:"DEFAULT:current_timestamp;type:datetime"`
	UpdatedDate    time.Time      `sql:"DEFAULT:current_timestamp;type:datetime"`
	SettingsJson   structure.JSON `sql:"type:json" json:"settings_json"`
	Username       string         `gorm:"size:500"`
	SizingType     string         `gorm:"column:sizing_type;size:15;default:general;check: sizing_type in ('optimal','fixed','hybrid')"`
	ScenLabel      string         `gorm:"column:scen_label;size:15;default:general;check: scen_label in ('general','archive','fav')"`
}

// TableName overrides the table name used by User to `profiles`
func (Scenario) TableName() string {
	return "hyperconverged_scenario"
}

func GetScenarioId(db *gorm.DB, scen *Scenario, scenario_id string) (err error) {
	err = db.First(&scen, "id = ?", scenario_id).Error
	if err != nil {
		return err
	}
	return err
}

// Used for landing page
func GetScenarioCount(db *gorm.DB, scenlabel string, username string) int {
	count := 0
	switch scenlabel {
	case "active":
		db.Model(&Scenario{}).Where("scen_label <> ? AND username = ? AND status = ?", "archive", username, true).Count(&count)
	case "fav":
		db.Model(&Scenario{}).Where("scen_label = ? AND username = ? AND status = ?", scenlabel, username, true).Count(&count)
	case "archive":
		db.Model(&Scenario{}).Where("scen_label = ? AND username = ? AND status = ?", scenlabel, username, true).Count(&count)

	}

	return count
}
