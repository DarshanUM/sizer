package structure

type SettingJson struct {
	Filters             map[string]interface{}
	Sed_only            bool
	Threshold           float64
	Dr_enabled          bool
	Hx_version          string
	Hypervisor          string
	Bundle_only         string
	Disk_option         string
	License_yrs         int
	Modular_lan         string
	Result_name         string
	Server_type         string
	Cache_option        string
	Heterogenous        bool
	Hercules_conf       string
	Hx_boost_conf       string
	Sizer_version       string
	IncludeSoftwareCost bool
}
