#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
#
# This is a CLI to train Franklin

import os
import sys
import argparse
import logging
from helpers import load_yaml_config, logger

if __name__ == "__main__":
    logger = logger()
    logger.info("Start training!")

    parser = argparse.ArgumentParser(description="Franklin CLI")
    parser.add_argument("--tub", required=True, help="Name of the exported tub")
    parser.add_argument("--pilot", help="Name of the exported pilot")
    parser.add_argument("--config", required=False, default="conf/default.yaml",
                        help="Path to config file : /conf/my_config.yml")

    args = parser.parse_args()
    config_path, tub, pilot = args.config, args.tub, args.pilot

    absolute_config_path = os.path.join(os.path.dirname(__file__), config_path)
    config = load_yaml_config(absolute_config_path)

    logger.info("Not yet implemented")

    logger.info("Finished!")