from hyperconverged.models import IopsConvFactor
output_script_file = open("output.sql", "w")

WL_Type = ["VEEAM", "SPLUNK"]
Threshold = [0, 1, 2]
filtered_parts = list()
parts = [iops.part_name for iops in IopsConvFactor.objects.all().order_by('id')]

for part in parts:
    if part not in filtered_parts:
        filtered_parts.append(part)

RF_String = ["RF2", "RF3"]
hyp_list = [0,1]

for hypervisor in hyp_list:
    for part in filtered_parts:
        for workload in WL_Type:
            for threshold in Threshold:
                for rf in RF_String:
                    output_script_file.write("INSERT INTO hyperconverged_iopsconvfactor (threshold, iops_conv_factor, replication_factor, workload_type, part_name, hypervisor) VALUES (" + str(threshold) + ",10000,'" + rf + "','" + workload + "','" + part + "'," + str(hypervisor) + ");\n")
        output_script_file.write("\n\n\n")
    output_script_file.write("\n\n\n\n\n\n\n\n\n\n\n\n\n\n")

output_script_file.close()
