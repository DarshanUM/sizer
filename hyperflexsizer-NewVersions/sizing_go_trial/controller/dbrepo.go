package controller

import (
	"cisco_sizer/database"

	"github.com/jinzhu/gorm"
)

type DbRepo struct {
	Db *gorm.DB
}

// var Db *gorm.DB

func New() *DbRepo {
	db := database.InitDb()
	// db.AutoMigrate(&models.User{})
	return &DbRepo{Db: db}
}

// func (repo *DbRepo) SetConnection() {
// 	Db = database.InitDb()
// 	// db.AutoMigrate(&models.User{})

// }

// func (repo DbRepo) GetConnection() *gorm.DB {
// 	return repo.Db
// }
