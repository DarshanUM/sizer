package model

import (
	"time"

	"github.com/jinzhu/gorm"
)

type User struct {
	ID                int    `gorm:"primaryKey"`
	Password          string `gorm:"size:100"`
	Username          string `gorm:"size:100;unique"`
	IsSuperUser       uint   `gorm:"default:0"`
	FirstName         string `gorm:"size:100"`
	LastName          string `gorm:"size:100"`
	Email             string `gorm:"size:100"`
	IsStaff           uint   `gorm:"default:0"`
	IsActive          uint   `gorm:"default:1"`
	EmpId             string `gorm:"size:10"`
	Company           string `gorm:"size:100"`
	AccessLevel       int
	IopsAccess        bool      `gorm:"default:false"`
	HomePageDesc      bool      `gorm:"default:true"`
	FixedSizingDesc   bool      `gorm:"default:true"`
	OptimalSizingDesc bool      `gorm:"default:true"`
	ScenarioPerPage   int       `gorm:"default:10"`
	Theme             string    `gorm:"size:20;default:light"`
	Language          string    `gorm:"size:20;default:english;check: language in ('english','japanese')"`
	BannerVersion     string    `gorm:"size:20;default:9.8.0"`
	HomeDisclaimer    time.Time `sql:"DEFAULT:current_timestamp;type:datetime"`
	DateJoined        time.Time `gorm:"column:date_joined;default:null" json:"date_joined"`
	LastLogin         time.Time `gorm:"column:last_login;default:null" json:"last_login"`
}

//   type Tabler interface {
// 	TableName() string
//   }

// TableName overrides the table name used by User to `profiles`
func (User) TableName() string {
	return "auth_user"
}

//get all users
func GetAllUser(db *gorm.DB, User *[]User) (err error) {
	err = db.Find(User).Error
	if err != nil {
		return err
	}
	return nil
}

func GetByUsername(db *gorm.DB, User *User, username string) (err error) {
	err = db.Where("username = ?", username).First(User).Error
	if err != nil {
		return err
	}
	return err
}

func GetByUserId(db *gorm.DB, User *User, userid int) (err error) {

	err = db.First(&User, "id = ?", userid).Error
	if err != nil {
		return err
	}
	return err
}
