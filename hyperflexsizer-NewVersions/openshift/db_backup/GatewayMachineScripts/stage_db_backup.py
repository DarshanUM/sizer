import subprocess
import sys


HOST="hyperflexsizer-g1ph863xstg-1@g1ph863xstg-hyperflexsizer.cloudapps.cisco.com"

# Ports are handled in ~/.ssh/config since we use OpenSSH
SCRIPT_CMD="python /tmp/stage_backup_database.py"
SCP_CMD = "scp hyperflexsizer-g1ph863xstg-1@g1ph863xstg-hyperflexsizer.cloudapps.cisco.com:/tmp/stage_database_backup.sql ."

def do_ssh(CMD):

    ssh = subprocess.Popen(CMD,
                           shell=False,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    result = ssh.stdout.readlines()
    if result == list():
        error = ssh.stderr.readlines()


def do_copy(CMD):

    ssh = subprocess.Popen(CMD,
                           shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)


do_ssh(["ssh", "%s" %HOST, SCRIPT_CMD])
do_copy(SCP_CMD)
#import os
#os.system(SCP_CMD)

