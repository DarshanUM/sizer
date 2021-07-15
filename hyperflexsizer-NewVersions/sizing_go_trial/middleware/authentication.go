package middleware

import (
	"cisco_sizer/database"
	"cisco_sizer/model"
	"net/http"

	"github.com/gin-gonic/gin"
)

var Username string

func Authentication(c *gin.Context) {

	// c.JSON(http.StatusUnauthorized, gin.H{"status": "unauthorized"})
	c.Next()
}

func UserValidation(c *gin.Context) {
	var httpAuthUser = c.Request.Header.Get("HTTP_AUTH_USER")
	var tokenValue = c.Request.Header.Get("HTTP_AUTHORIZATION")
	if httpAuthUser != "" {
		Username = httpAuthUser
	} else if tokenValue != "" {
		var user model.User
		var keyToken model.Token
		err := model.GetByKey(database.Db, &keyToken, tokenValue)
		if err != nil {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized Access"})
		}
		err = model.GetByUserId(database.Db, &user, keyToken.UserId)
		if err != nil {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized Access"})
		}
		Username = user.Username
	} else {
		c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"status": "Unauthorized Access"})
	}

	c.Next()
}
