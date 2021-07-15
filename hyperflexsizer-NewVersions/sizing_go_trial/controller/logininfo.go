package controller

import (
	"cisco_sizer/database"
	"cisco_sizer/middleware"
	"cisco_sizer/model"
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"
)

type Credential struct {
	Username string
	Password string
}

func AuthInfo(c *gin.Context) {
	var httpAuthUser = c.Request.Header.Get("HTTP_AUTH_USER")
	// for local code base
	if httpAuthUser == "" {
		var cred Credential
		// jsonData, _ := ioutil.ReadAll(c.Request.Body)
		// c.ShouldBind()
		c.Bind(&cred)
		fmt.Println(cred)
		var user model.User
		err := model.GetByUsername(database.Db, &user, cred.Username)
		if err != nil {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized Access"})
		}
		var keyToken model.Token
		err = model.GetKeyByUserId(database.Db, &keyToken, user.ID)
		if err != nil {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized Access"})
		}
		middleware.Username = cred.Username
		c.JSON(http.StatusOK, gin.H{"auth_token": keyToken.Key, "iops_access": true})

	} else {
		middleware.Username = httpAuthUser

		var isAvailable bool = true
		var user model.User
		err := model.GetByUsername(database.Db, &user, httpAuthUser)
		if err != nil {
			isAvailable = false
		}

		if isAvailable {
			c.JSON(http.StatusOK, gin.H{"status": "success", "iops_access": user.IopsAccess})
		} else {
			//TODO : get details from LDAP
		}
	}
	c.Next()
}
