package hyperconverged

import (
	"cisco_sizer/model"
	"cisco_sizer/structure"
	"time"
)

type GetDetail struct {
	Id                 int
	Name               string
	Sizing_type        string
	Workload_json      structure.JSON
	Updated_date       time.Time
	Ddl_sizing_res_arr []string
	Sharedcount        int
	Scen_label         string
	Workload_result    structure.JSON
	Settings_json      structure.JSON
	Scenario_warning   bool
	Estimate_id_res    []string
}

//TODO:
func FetchScenarioDetail(scenario model.Scenario) GetDetail {
	var detail GetDetail
	return detail

}
