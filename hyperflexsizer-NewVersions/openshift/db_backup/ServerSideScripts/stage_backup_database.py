import os


USER = os.environ['OPENSHIFT_MYSQL_DB_USERNAME']
PASS =os.environ['OPENSHIFT_MYSQL_DB_PASSWORD']
DB =  os.environ['OPENSHIFT_APP_NAME']
HOST = os.environ['OPENSHIFT_MYSQL_DB_HOST']
PORT = os.environ['OPENSHIFT_MYSQL_DB_PORT']
FILE_NAME = "/tmp/stage_database_backup.sql"

cmd = "mysqldump -u " +USER +" -p"+PASS+" " + DB+ " -h " + HOST + " -P "+PORT +" >"+FILE_NAME

os.system(cmd)
