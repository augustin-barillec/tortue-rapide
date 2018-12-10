#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
#
# This is a CLI to train Franklin

import sys
import argparse
import logging

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.info("Job start")

    parser = argparse.ArgumentParser(description="Franklin CLI")
    parser.add_argument("--tub", required=True, help="Name of the exported tub")
    parser.add_argument("--pilot", help="Name of the exported pilot")
    parser.add_argument("--config", required=False,
                        help="Path to config file : /conf/config.yml")

    args = parser.parse_args()
    logger.info("Not yet impremented")