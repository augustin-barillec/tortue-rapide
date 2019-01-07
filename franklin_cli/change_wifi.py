#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
#
# This is a script to change Franklin's WiFi settings

import argparse
import subprocess
from helpers import logger

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Franklin WiFi settings")
    parser.add_argument("--name", help="""New WiFi name.""")
    parser.add_argument("--password", help="""New WiFi password""")

    args = parser.parse_args()

    logger.error("Not implemented yet!")
