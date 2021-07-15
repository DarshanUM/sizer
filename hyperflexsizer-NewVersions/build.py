import sys
import subprocess
from sys import argv

CMD_LIST_STG = (
           ('Clean py~ files', 'find . -name "*.py~" -exec rm -rf {} \;'),
           ('Clean pyc files', 'find . -name "*.pyc" -exec rm -rf {} \;'),
           ('Building distribution', 'sh dist.sh'),
           ('Copy CAE Stage Dockerfile', 'cp sizer/buildfiles/Stage_Dockerfile  sizer/Dockerfile'),
           ('Build tar file', 'tar -zcvf hyperflexsizer.tar.gz sizer --exclude sizer/sizer/webapps/node_modules --exclude sizer/sizer/webapps/bower_components')
           )

CMD_LIST_PROD = (
           ('Clean py~ files', 'find . -name "*.py~" -exec rm -rf {} \;'),
           ('Clean pyc files', 'find . -name "*.pyc" -exec rm -rf {} \;'),
           ('Building distribution', 'sh dist.sh'),
           ('Copy CAE Prod Dockerfile', 'cp sizer/buildfiles/Prod_Dockerfile  sizer/Dockerfile'),
           ('Build tar file', 'tar -zcvf hyperflexsizer.tar.gz sizer --exclude sizer/sizer/webapps/node_modules --exclude sizer/sizer/webapps/bower_components')
           )

def exec_cmd():

    if len(sys.argv) > 1:
        CMD_LIST = CMD_LIST_STG if argv[1] == "stage" else CMD_LIST_PROD
    else:
        CMD_LIST = CMD_LIST_STG


    for (name, cmd) in CMD_LIST:
        sys.stdout.write(name + " - ")
        #    sys.stdout.flush()
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        out, err = proc.communicate()
        if not err:
            sys.stdout.write("[OK]\n")
            sys.stdout.write(out)
            #sys.stdout.flush()
        else:
            sys.stdout.write("[ERROR]\n")
            sys.stdout.write(err)
            sys.stdout.flush()


exec_cmd()
