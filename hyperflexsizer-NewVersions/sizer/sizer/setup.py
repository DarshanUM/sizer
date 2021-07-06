import os
import sys
import subprocess


global DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

DB_NAME = "maplesizer"
DB_USER = "root"
DB_PASSWORD = "maplelabs"
DB_HOST = "localhost"
DB_PORT = "3306"

DB_CONF_FILE = os.path.join(os.getcwd(), "sizer", "conf.py")
CREATE_TABLE_SQL_FILE = os.path.join(os.getcwd(), "../../deployment_scripts", "createTables.sql")
DROP_TABLE_SQL_FILE = os.path.join(os.getcwd(), "../../deployment_scripts", "mapleSizerDeleteData.sql")
INSERT_TABLE_SQL_FILE = os.path.join(os.getcwd(), "../../deployment_scripts", "mapleSizerCisco.sql")


def exec_cmds(CMD_LIST):
    for (name, cmd) in CMD_LIST:
        sys.stdout.write(name + " - ")
        sys.stdout.flush()

        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        out, err = proc.communicate()

        if not err:
            sys.stdout.write("[OK]\n")
            sys.stdout.flush()
        else:
            sys.stdout.write("[ERROR]\n")
            sys.stdout.write(err)
            sys.stdout.flush()



def set_db_variables():
    if os.environ.has_key("DB_NAME"):
        global DB_NAME
        DB_NAME = os.environ.get("DB_NAME")
        cmd = ("Seting DB NAME", "sed -i 's/^DB_NAME = \".*\"/DB_NAME = \""  + DB_NAME + "\"/' " + DB_CONF_FILE)
        exec_cmds([cmd])

    if os.environ.has_key("DB_USER"):
        global DB_USER
        DB_USER =  os.environ.get("DB_USER")
        cmd = ("Seting DB USER", "sed -i 's/^DB_USER = \".*\"/DB_USER = \""  + DB_USER + "\"/' " + DB_CONF_FILE)
        exec_cmds([cmd])

    if os.environ.has_key("DB_PASSWORD"):
        global DB_PASSWORD
        DB_PASSWORD = os.environ.get("DB_PASSWORD")
        cmd = ("Seting DB PASSWORD", "sed -i 's/^DB_PASSWORD = \".*\"/DB_PASSWORD = \""  + DB_PASSWORD + "\"/' " + DB_CONF_FILE)
        exec_cmds([cmd])

    if os.environ.has_key("DB_HOST"):
        global DB_HOST
        DB_HOST = os.environ.get("DB_HOST")
        cmd = ("Seting DB HOST", "sed -i 's/^DB_HOST = \".*\"/DB_HOST = \""  + DB_HOST + "\"/' " + DB_CONF_FILE)
        exec_cmds([cmd])

    if os.environ.has_key("DB_PORT"):
        global DB_PORT
        DB_PORT = os.environ.get("DB_PORT")
        cmd = ("Seting DB PORT", "sed -i 's/^DB_PORT = \".*\"/DB_PORT = \""  + DB_PORT + "\"/' " + DB_CONF_FILE)
        exec_cmds([cmd])

"""
def set_env():
    os.environ["DB_NAME"] = "test"
    os.environ["DB_USER"] = "root"
    os.environ["DB_PASSWORD"] = "maplelabs"
    os.environ["DB_HOST"] = "localhost"
    os.environ["DB_PORT"] = "3306"
"""

def load_db():
    global DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
    cmd_list = []
    comments = ["Creating tables", "drop node and parts tables", "insert nodes and parts"]
    sql_files = [CREATE_TABLE_SQL_FILE, DROP_TABLE_SQL_FILE, INSERT_TABLE_SQL_FILE]
    for sql_file, comment in zip(sql_files, comments):
        command = "mysql -u " + DB_USER + " -p" + DB_PASSWORD + " " + DB_NAME + " -h " + DB_HOST + " -P " + DB_PORT + " < " + sql_file
        cmd  =(comment, command)
        cmd_list.append(cmd)

    exec_cmds(cmd_list)



if __name__ == "__main__":
    # This function sets db variables
    set_db_variables()

    # This function load the new database with the sql file, assuming that database is created
    load_db()
