package main

import (
	"C"
	"encoding/json"

	"fmt"

	"github.com/pramurthy/gorefactor/structure"
)

//export Hello
func Hello(test_s string, test *C.char) {
	fmt.Println(test_s)
	fmt.Println(C.GoString(test))
	// fmt.Println("Hello " + C.GoString(s) + "!")
}

//export SolveSizing
func SolveSizing(settingJson string, workloadJsonList string, filteredNode string, scenarioId int, nodeJsonList string) {
	// var workList map[string]interface{}
	// hyperconverged_node := hyperconverged.SetDeafultValue()

	// var lstNode []map[string]model.Node
	// err := json.Unmarshal([]byte(nodeJsonList), &lstNode)
	// if err != nil {
	// 	panic(err)
	// }

	// fmt.Println(settingJson)
	fmt.Println(filteredNode)
	var setting_json structure.SettingJson
	err := json.Unmarshal([]byte(settingJson), &setting_json)
	if err != nil {
		fmt.Println(err)
		// panic(err)
	}
	fmt.Println(setting_json.Sizer_version)

	var lstWorkload structure.Workload
	err = json.Unmarshal([]byte(workloadJsonList), &lstWorkload)
	if err != nil {
		println(err)
	}
	println("finished")

}

//export fun
func fun(x int, y int) int {
	return x + y
}

func main() {}
