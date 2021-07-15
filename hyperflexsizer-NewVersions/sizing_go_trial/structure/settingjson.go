package structure

type SettingJson struct {
	Filters             map[string][]string `json:"filters"`
	SedOnly             bool                `json:"sed_only"`
	Threshold           int                 `json:"threshold"`
	DrEnabled           bool                `json:"dr_enabled"`
	HxVersion           string              `json:"hx_version"`
	Hypervisor          string              `json:"hypervisor"`
	BundleOnly          string              `json:"bundle_only"`
	DiskOption          string              `json:"disk_option"`
	LicenseYrs          int                 `json:"license_yrs"`
	ModularLan          string              `json:"modular_lan"`
	ResultName          string              `json:"result_name"`
	ServerType          string              `json:"server_type"`
	CacheOption         string              `json:"cache_option"`
	Heterogenous        bool                `json:"heterogenous"`
	HerculesConf        string              `json:"hercules_conf"`
	HxBoostConf         string              `json:"hx_boost_conf"`
	SizerVersion        string              `json:"sizer_version"`
	IncludeSoftwareCost bool                `json:"includeSoftwareCost"`
	CpuGeneration       string              `json:"cpu_generation"`
}
