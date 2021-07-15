GATEWAY MACHINE:
1.Copy GatewayMachineScripts/* files to  $home_dir/scripts/  on Gateway machine


SERVER MACHINE:
1.Keep ServerSideScripts   /tmp/ ( actual server where code is running)


FROM WINDOWS MACHINE:

1.At some working directory make sure, plink.exe and pscp.exe file are existed(say this dir is workspace)
2.keep prod_db_backup.bat and stage_db_backup.bat at the workspace
3.run the bat scripts from command prompt, it will copy the db backup files to workspace(prod_database_backup.sql, stage_database_backup.sql)
