package model

import (
	"time"

	"github.com/jinzhu/gorm"
	uuid "github.com/nu7hatch/gouuid"
)

type Token struct {
	Key     string `gorm:"column:key;size:100" json:"key"`
	UserId  int
	Created time.Time `gorm:"column:created;DEFAULT:current_timestamp;" json:"created"`
}

// TableName overrides the table name used by User to `profiles`
func (Token) TableName() string {
	return "authtoken_token"
}

//get GetAllToken
func GetAllToken(db *gorm.DB, Token *[]Token) (err error) {
	err = db.Find(Token).Error
	if err != nil {
		return err
	}
	return nil
}

func GetByKey(db *gorm.DB, Token *Token, key string) (err error) {

	err = db.Where("`key` = ?", key).First(Token).Error
	if err != nil {
		return err
	}
	return err
}

func GetKeyByUserId(db *gorm.DB, token *Token, userid int) (err error) {

	uuid_value, _ := uuid.NewV4()
	err = db.Where("user_id = ?", userid).Attrs(Token{Key: uuid_value.String()}).FirstOrCreate(token).Error
	if err != nil {
		return err
	}
	return err
}
