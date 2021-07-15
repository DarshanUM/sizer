package sizerinfo

import (
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"
)

type EnvInfo struct {
	Lae            bool
	Username       string
	Email          string
	Profiler_email string
	Bench_email    string
}

func GetEnvInfo(c *gin.Context) {
	var httpAuthUser = c.Request.Header.Get("HTTP_AUTH_USER")
	fmt.Println(httpAuthUser)
	var envInfo EnvInfo
	if httpAuthUser != "" {
		envInfo = EnvInfo{
			Lae:            true,
			Username:       httpAuthUser,
			Email:          "hx-sizer@external.cisco.com",
			Profiler_email: "hx-profiler@external.cisco.com",
			Bench_email:    "hx-bench@external.cisco.com"}
	} else {
		envInfo = EnvInfo{
			Lae:            false,
			Username:       "",
			Email:          "hx-sizer@maplelabs.com",
			Profiler_email: "hx-profiler@maplelabs.com",
			Bench_email:    "hx-bench@maplelabs.com"}
	}
	// c.Header("Content-Type", "application/json")
	fmt.Println(envInfo)
	c.JSON(http.StatusOK, envInfo)
}
