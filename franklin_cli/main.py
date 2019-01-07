#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
#
# This is a CLI to train Franklin

import argparse
import subprocess
from helpers import logger

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Franklin CLI")
    parser.add_argument("--local_tub", help="""Path to local tub on your local machine.""")
    parser.add_argument("--user", help="""The username for tensorflow-gpu (i.e. tristan_letrou_ysance_com).
    Needs path to use a tub on this machine.""")

    args = parser.parse_args()
    local_tub, user = args.local_tub, args.user

    logger = logger()
    logger.info("Start training!")

    clean_working_tub = "rm -rf tub && rm -f tub.zip"
    subprocess.call(clean_working_tub, shell=True)

    if(local_tub is None):
        get_tub_cmd = "sshpass -p raspberry rsync -r pi@192.168.43.200:~/mycar/tub ."
    else:
        get_tub_cmd = "cp -r {} .".format(local_tub)
    subprocess.call(get_tub_cmd, shell=True)

    cmd = """zip -r tub.zip tub &&\
            gcloud compute scp --project dmp-y-tests --zone europe-west1-d  tub.zip {user}@tensorflow-gpu:~/mycar &&\
            gcloud compute ssh --project dmp-y-tests --zone europe-west1-d {user}@tensorflow-gpu \
            -- 'source env/bin/activate &&\
                cd ~/mycar &&\
                rm -rf tub && rm -f mypilot &&\
                unzip tub &&\
                python manage.py train --tub tub --model mypilot' &&\
            gcloud compute scp --project dmp-y-tests --zone europe-west1-d {user}@tensorflow-gpu:~/mycar/mypilot . &&\
            sshpass -p raspberry rsync mypilot pi@192.168.43.200:~/mycar/mypilot
    """.format(user=user)

    subprocess.call(cmd, shell=True)

    logger.info("Finished!")
