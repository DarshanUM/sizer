package database

import (
	"fmt"
	//    "gorm.io/driver/mysql"
	// "github.com/go-sql-driver/mysql"
	_ "github.com/go-sql-driver/mysql"
	"github.com/jinzhu/gorm"
)

const DB_USERNAME = "root"
const DB_PASSWORD = "maplelabs"
const DB_NAME = "maplesizer"
const DB_HOST = "127.0.0.1"
const DB_PORT = "3306"

var Db *gorm.DB

func InitDb() *gorm.DB {
	Db = connectDB()

	return Db
}

func connectDB() *gorm.DB {
	var err error
	//    dsn := DB_USERNAME +":"+ DB_PASSWORD +"@tcp"+ "(" + DB_HOST + ":" + DB_PORT +")/" + DB_NAME + "?" + "parseTime=true&loc=Local"
	//    db, err := gorm.Open(mysql.Open(dsn), &gorm.Config{})

	dsn := DB_USERNAME + ":" + DB_PASSWORD + "@tcp(" + DB_HOST + ":" + DB_PORT + ")/" + DB_NAME + "?charset=utf8&parseTime=true&loc=Local"
	db, err := gorm.Open("mysql", dsn)

	if err != nil {
		fmt.Println("Error connecting to database : error=%v", err)
		return nil
	}

	// Disable table name's pluralization, if set to true, `User`'s table name will be `user`
	db.SingularTable(true)
	fmt.Println("open connection successfully to the DB::::")
	return db
}
