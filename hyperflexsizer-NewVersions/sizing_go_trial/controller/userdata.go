package controller

import (
	"cisco_sizer/database"
	"cisco_sizer/middleware"
	"cisco_sizer/model"
	"net/http"
	"os"
	"time"

	"github.com/gin-gonic/gin"
)

//    "errors"

// type UserRepo struct {
// 	Db *gorm.DB
// }

// func New() *UserRepo {
// 	db := database.InitDb()
// 	// db.AutoMigrate(&models.User{})
// 	return &UserRepo{Db: db}
// }

//get users
// func (repository *UserRepo) GetUsers(c *gin.Context) {
// 	var user []model.User
// 	err := model.GetUsers(repository.Db, &user)
// 	if err != nil {
// 		c.AbortWithStatusJSON(http.StatusInternalServerError, gin.H{"error": err})
// 		return
// 	}
// 	c.JSON(http.StatusOK, user)
// }

func GetUsers(c *gin.Context) {
	var user []model.User
	err := model.GetAllUser(database.Db, &user)
	if err != nil {
		c.AbortWithStatusJSON(http.StatusInternalServerError, gin.H{"error": err})
		return
	}

	c.JSON(http.StatusOK, user)
}

func GetUserData(c *gin.Context) {
	var user model.User
	err := model.GetByUsername(database.Db, &user, middleware.Username)
	if err != nil {
		c.AbortWithStatusJSON(http.StatusInternalServerError, gin.H{"error": err})
		return
	}

	var logout_url, estimatetokenapi_url string = "", ""
	var hxpreinstaller_url string = "HX_PREINSTALLER_PROD_URL"
	sizerInstance := os.Getenv("SIZER_INSTANCE")
	if sizerInstance == "STAGE" {
		logout_url = "STAGE_LOGOUT_URL"
		hxpreinstaller_url = "HX_PREINSTALLER_STAGE_URL"
		estimatetokenapi_url = "STAGE_REDIRECT_TOKEN_URL"
	} else {
		logout_url = "PROD_LOGOUT_URL"
		hxpreinstaller_url = "HX_PREINSTALLER_PROD_URL"
		estimatetokenapi_url = "PROD_REDIRECT_TOKEN_URL"
	}

	//TODO : utf string issue need to fix
	var firstName string = user.FirstName
	if firstName == "" {
		firstName = "anonymous"
	}

	var homeDisclaimer bool = false
	defaultDate, _ := time.Parse("2006-01-02", "2001-01-01")
	if DateEqual(user.HomeDisclaimer, defaultDate) {
		homeDisclaimer = true
	}

	// if else condition for the below json response is not reuquired becuase of admin

	favCount := model.GetScenarioCount(database.Db, "fav", middleware.Username)
	archiveCount := model.GetScenarioCount(database.Db, "archive", middleware.Username)
	activeCount := model.GetScenarioCount(database.Db, "active", middleware.Username)
	sharedCount := model.GetSharedScenarioCount(database.Db, middleware.Username)

	//TODO: check with access_token if any logic is written in UI
	c.JSON(http.StatusOK, gin.H{
		"home_page_desc":       user.HomePageDesc,
		"optimal_sizing_desc":  user.OptimalSizingDesc,
		"fixed_sizing_desc":    user.FixedSizingDesc,
		"scenario_per_page":    user.ScenarioPerPage,
		"language":             user.Language,
		"theme":                user.Theme,
		"banner_version":       user.BannerVersion,
		"user_firstname":       firstName,
		"home_disclaimer":      homeDisclaimer,
		"logout_url":           logout_url,
		"hxpreinstaller_url":   hxpreinstaller_url,
		"access_token":         "Nc1cJMLeWoMSRJHrCYMHBMV3IEqZ",
		"estimatetokenapi_url": estimatetokenapi_url,
		"scenario_count":       map[string]interface{}{"active": activeCount, "favorite": favCount, "archive": archiveCount, "shared": sharedCount},
	})
}

func DateEqual(date1, date2 time.Time) bool {
	y1, m1, d1 := date1.Date()
	y2, m2, d2 := date2.Date()
	return y1 == y2 && m1 == m2 && d1 == d2
}
