package model

import "github.com/jinzhu/gorm"

type SharedScenario struct {
	ID         int    `gorm:"primaryKey"`
	ScenarioId int    `gorm:"not null"`
	Username   string `gorm:"size:128"`
	Userid     string `gorm:"size:128"`
	Acl        bool   `gorm:"default:true"`
	Email      string `gorm:"size:150"`
	IsSecure   bool   `gorm:"default:false"`
}

// TableName overrides the table name used by User to `profiles`
func (SharedScenario) TableName() string {
	return "hyperconverged_sharedscenario"
}

func GetSharedScenarioCount(db *gorm.DB, username string) int {
	count := 0
	db.Model(&Scenario{}).Where("username = ?", username).Count(&count)
	return count
}

func GetSharedScenarioCountById(db *gorm.DB, username string, scenario_id string) int {
	count := 0
	db.Model(&Scenario{}).Where("username = ? AND scenario_id = ?", username, scenario_id).Count(&count)
	return count
}
