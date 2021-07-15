package controller

import (
	"cisco_sizer/database"
	"cisco_sizer/hyperconverged"
	"cisco_sizer/middleware"
	"cisco_sizer/model"
	"encoding/json"
	"net/http"

	"github.com/gin-gonic/gin"
)

func SolveSizingCtrl(c *gin.Context) {
	var node model.Node
	err := model.GetFirstNode(database.Db, &node)
	if err != nil {
		c.AbortWithStatus(http.StatusNotFound)
	}
	hyperconverged_node := hyperconverged.InitializeHyperconvergedNode(&node)
	err = json.Unmarshal(node.NodeJson, &hyperconverged_node.Attrib)
	if err != nil {
		panic(err)
	}
	c.JSON(http.StatusOK, "test")
}

func GetScenarioDetail(c *gin.Context) {
	var id string = c.Param("id")
	var scenario model.Scenario
	err := model.GetScenarioId(database.Db, &scenario, id)
	if err != nil {
		c.AbortWithStatus(http.StatusNotFound)
		// c.AbortWithStatusJSON(http.Statu, gin.H{"error": err})
		return
	}
	var shareCount int = model.GetSharedScenarioCountById(database.Db, middleware.Username, id)
	if shareCount == 0 && scenario.Username == middleware.Username {
		c.AbortWithStatusJSON(http.StatusBadRequest, gin.H{"status": "error",
			"errorMessage": "Unauthorized Access"})
	}
	responseData := hyperconverged.FetchScenarioDetail(scenario)
	jsonData, _ := json.Marshal(responseData)
	c.JSON(http.StatusOK, string(jsonData))
}
