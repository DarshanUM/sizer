package sizerinfo

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

func VersionDetail(c *gin.Context) {
	//TODO add config file implementation
	// name := os.Getenv("OPENSHIFT_REPO_DIR")
	c.JSON(http.StatusOK, gin.H{"Sizer_Version": "10.3.8", "HX_Version": "4.5", "HXBench_Version": "1.3"})

}
