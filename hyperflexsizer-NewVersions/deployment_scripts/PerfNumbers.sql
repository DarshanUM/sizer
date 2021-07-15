# OLTP/OOLTP/VSI workload

INSERT INTO hx_perf_numbers (server_type, hypervisor, wl_type, threshold, node_substring, ssd_string, replication_factor, iops_type, iops_value) VALUES ("M5",0,"OLTP/VSI",1,"All-Flash","SAS","RF3","8K|70% Read|30% Write|100% Random (IOPS)",17600);

INSERT INTO hx_perf_numbers (server_type, hypervisor, wl_type, threshold, node_substring, ssd_string, replication_factor, iops_type, iops_value) VALUES ("M5",0,"OLTP/VSI",1,"All-Flash","Optane","RF3","8K|70% Read|30% Write|100% Random (IOPS)",18612);

INSERT INTO hx_perf_numbers (server_type, hypervisor, wl_type, threshold, node_substring, ssd_string, replication_factor, iops_type, iops_value) VALUES ("M5",0,"OLTP/VSI",1,"All-Flash","ALL NVMe","RF3","8K|70% Read|30% Write|100% Random (IOPS)",31677);

# OLAP/OOLAP workload

INSERT INTO hx_perf_numbers (server_type, hypervisor, wl_type, threshold, node_substring, ssd_string, replication_factor, iops_type, iops_value) VALUES ("M5",0,"OLAP",1,"All-Flash","SAS","RF3","64K|100% Seq Read (MB/s)",1100);

INSERT INTO hx_perf_numbers (server_type, hypervisor, wl_type, threshold, node_substring, ssd_string, replication_factor, iops_type, iops_value) VALUES ("M5",0,"OLAP",1,"All-Flash","Optane","RF3","64K|100% Seq Read (MB/s)",1100);

INSERT INTO hx_perf_numbers (server_type, hypervisor, wl_type, threshold, node_substring, ssd_string, replication_factor, iops_type, iops_value) VALUES ("M5",0,"OLAP",1,"All-Flash","ALL NVMe","RF3","64K|100% Seq Read (MB/s)",1500);