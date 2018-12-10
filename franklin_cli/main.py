#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
#
# This is a CLI to train Franklin

import os
import sys
import argparse
import logging
from subprocess import run, Popen, PIPE
from helpers import load_yaml_config, logger
import pexpect

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Franklin CLI")
    parser.add_argument("--tub", required=True,
                        help="Name of the exported tub")
    parser.add_argument("--pilot", required=True,
                        help="Name of the exported pilot")
    parser.add_argument("--config", default="conf/default.yaml",
                        help="Path to config file : conf/my_config.yaml")
    parser.add_argument("--local_tub", help="""Use local tub on your local machine.
    Needs path to use a tub on this machine.""")

    args = parser.parse_args()
    config_path, tub, pilot, localSource = args.config, args.tub, args.pilot, args.local_tub

    logger = logger()
    logger.info("Start training!")

    # "Absolutize" the conf path
    absolute_config_path = os.path.join(os.path.dirname(__file__), config_path)
    config = load_yaml_config(absolute_config_path)

    # Get the tub with ssh with rsync
    if localSource is None:
        rsync_cmd = "rsync -r {}@{}:{} {}".format(config['machine']['user'], config['machine']['address'], config['machine']['tub_path'], "~/" + tub)                               
        print(rsync_cmd)                   
        child = pexpect.spawn(rsync_cmd)
        # child.logfile = sys.stdout
        child.expect('password:')
        child.sendline(config['machine']['password'])

        print('cvzavz')
        # result = run(rsync_cmd.split(" "))
        # print(config['machine']['password'], file=PIPE)

        # with Popen(rsync_cmd, stdin=PIPE, stdout=PIPE,
        #            universal_newlines=True) as p:
        #     for line in p.stdout:
        #         if line.startswith("Please enter the name of the project"):
        #         print(answer, file=p.stdin)  # Answer password
        #         p.stdin.flush()

        # call(rsync_cmd)

    logger.info("Not yet implemented")

    logger.info("Finished!")
