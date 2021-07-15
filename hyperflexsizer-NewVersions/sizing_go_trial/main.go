package main

import (
	"cisco_sizer/controller"
)

func main() {
	controller.New()
	var setting_json string = "{\"account\": \"\", \"filters\": {\"Clock\": [], \"CPU_Type\": [], \"GPU_Type\": [], \"Node_Type\": [], \"RAM_Slots\": [], \"RAM_Options\": [], \"Compute_Type\": [\"HX-B200\", \"HX-C220\", \"HX-C240\", \"HX-C480\"], \"Disk_Options\": [], \"Cache_Options\": []}, \"threshold\": 1, \"dr_enabled\": false, \"hx_version\": \"4.5\", \"hypervisor\": \"esxi\", \"bundle_only\": \"ALL\", \"disk_option\": \"NON-SED\", \"license_yrs\": 3, \"modular_lan\": \"ALL\", \"result_name\": \"Lowest_Cost\", \"server_type\": \"M5\", \"cache_option\": \"ALL\", \"heterogenous\": true, \"hercules_conf\": \"enabled\", \"hx_boost_conf\": \"enabled\", \"sizer_version\": \"10.3.8\", \"cpu_generation\": \"recommended\", \"includeSoftwareCost\": true, \"ddl_sizing_res_arr\": [\"All-Flash\", \"Lowest_Cost\", \"All NVMe\", \"Fixed_Config\"], \"free_disk_slots\": 0}"

	var workload_list string = "[{\"wl_type\": \"VDI\", \"wl_name\": \"VDI-1\", \"wl_cluster_name\": \"\", \"profile_type\": \"Task Worker\", \"provisioning_type\": \"Pooled Desktops\", \"os_type\": \"win_7\", \"num_desktops\": 1, \"concurrency\": 100, \"gpu_users\": 0, \"video_RAM\": \"1024\", \"vdi_directory\": 0, \"user_iops\": 0, \"disk_per_desktop\": 0, \"disk_per_desktop_unit\": \"GiB\", \"vcpus_per_desktop\": 1, \"clock_per_desktop\": 325, \"ram_per_desktop\": 1, \"ram_per_desktop_unit\": \"GiB\", \"snapshots\": 0, \"avg_iops_per_desktop\": 6, \"working_set\": 10, \"gold_image_size\": 20, \"gold_image_size_unit\": \"GB\", \"cluster_type\": \"normal\", \"replication_factor\": 3, \"fault_tolerance\": 1, \"compression_factor\": 10, \"dedupe_factor\": 30, \"compression_saved\": 90, \"dedupe_saved\": 63, \"isDirty\": true, \"internal_type\": \"VDI\", \"storage_protocol\": \"NFS\"}]"

	SolveSizing(setting_json, workload_list, "", 1, "")

	// Nodes := hyperconverged.FilterNodeAndPartData("{'Clock': ['2.1', '2.4'], 'CPU_Type': ['6230R (26, 2.1)'], 'GPU_Type': ['M10', 'V100', 'T4', 'P40', 'RTX8000'], 'Node_Type': ['HXAF-240', 'HXAF-220'], 'RAM_Slots': [12, 24, 8], 'RAM_Options': ['128GiB DDR4', '32GiB DDR4', '16GiB DDR4'], 'Compute_Type': ['HX-C220', 'HX-C240', 'HX-B200'], 'Disk_Options': ['800GB [SSD]', '960GB [SSD]', '1.2TB [HDD]', '3.8TB [SSD]'], 'Cache_Options': ['800GB'], 'Riser_options': 'Storage'}", "Lowest_Cost", "SED", "SED", "M5", "esxi", "enabled", "ALL", "enabled", 0)
	// fmt.Println(Nodes)

	// router := gin.Default()
	// // router.LoadHTMLGlob("webapps/*")
	// // router.GET("/", func(c *gin.Context) {
	// //     c.HTML(http.StatusOK, "index.html", nil)
	// // })
	// // r.GET("/login", func(c *gin.Context) {
	// //     c.HTML(http.StatusOK, "login.html", nil)
	// // })

	// // middleware.AuthenticationInfo
	// // userRepo := userinfo.New()

	// // var p = controller.DbRepo{}
	// // p.SetConnection()
	// // admin := router.Group("/admin")
	// // admin.GET("/", fun c(c *gin.Context) {
	// //     c.HTML(http.StatusOK, "admin-overview.html", nil)
	// // })

	// router.POST("/auth/login", controller.AuthInfo)

	// // router.Use(middleware.UserValidation)
	// router.Use(static.Serve("/", static.LocalFile("./webapps/dist/", true)))

	// router.GET("/envinfo", sizerinfo.GetEnvInfo)
	// router.GET("/version", sizerinfo.VersionDetail)
	// router.GET("/userdata", controller.GetUsers)
	// router.GET("/testapp", controller.SolveSizingCtrl)

	// router.GET("/test", func(c *gin.Context) {
	// 	c.JSON(http.StatusOK, gin.H{"data": "hello world"})
	// })
	// router.Run(":3001")
}
