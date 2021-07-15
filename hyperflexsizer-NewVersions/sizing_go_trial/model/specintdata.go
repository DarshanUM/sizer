package model

import "github.com/jinzhu/gorm"

type SpecIntData struct {
	ID              int     `gorm:"primaryKey"`
	Model           string  `gorm:"size:128"`
	Speed           float64 `gorm:"defautl:0"`
	Cores           int     `gorm:"defautl:0"`
	BlendedCore2006 float64 `gorm:"column:blended_core_2006;defautl:0"`
	BlendedCore2017 float64 `gorm:"column:blended_core_2017;defautl:0"`
	IsBaseModel     bool    `gorm:"defautl:false"`
}

// TableName overrides the table name used by User to `profiles`
func (SpecIntData) TableName() string {
	return "hyperconverged_specintdata"
}

func GetSpecIntBaseModel(db *gorm.DB, specInt *SpecIntData) (err error) {
	err = db.Where("is_base_model = true").First(specInt).Error
	if err != nil {
		return err
	}
	return nil
}

func GetSpectIntModel(db *gorm.DB, value string, specInt *SpecIntData) (err error) {
	err = db.Where("model = ?", value).First(specInt).Error
	if err != nil {
		return err
	}
	return nil
}
