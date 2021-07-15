package model

import "cisco_sizer/structure"

type Rules struct {
	RuleId   int            `gorm:"primaryKey;column:rule_id"`
	RuleJson structure.JSON `sql:"type:json" json:"rule_json"`
}

func (Rules) TableName() string {
	return "hyperconverged_rules"
}
