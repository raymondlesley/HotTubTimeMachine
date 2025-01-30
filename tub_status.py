#!/usr/bin/python3
# tub_status - output (raw) status data
#

import argparse
import logging
from tarfile import version

import log_config
import csv
import os
import sys
import datetime

from configuration import Configuration
from bestway.bestwayapi import BestwayAPI
from bestway.bestway_user_token import BestwayUserToken

# CONSTANTS
CFGFILENAME = 'configuration.json'
GIZWITS_URL = 'https://euapi.gizwits.com'
STATES      = ['on', 'off']
# parse arguments
argparser = argparse.ArgumentParser(prog="tub_control.py", description="Hot Tub filter pump control", epilog="with no control arguments [-P, -H, -T] prints current status")
argparser.add_argument('-c', '--cfgfile', help="location of configuration file; default='configuration.json'")
argparser.add_argument('-l', '--loglevel', help="logging level: INFO, DEBUG, WARNING, ERROR, CRITICAL")
argparser.add_argument('-r', '--raw', action='store_true', help="output raw JSON data")
argparser.add_argument('-s', '--sorted', action='store_true', help="sort raw JSON data")
args = argparser.parse_args()

# setup logging
log_config.prepare_logging(args.loglevel)
# setup logfile filename
if not args.cfgfile:
    args.cfgfile = os.path.join(os.path.dirname(sys.argv[0]), CFGFILENAME)
    logging.info(f"using configuration file {args.cfgfile}")

logging.info("Load configuration from file...")
cfg = Configuration.fromFile(args.cfgfile)

# check Gizwits URL
if not cfg['gizwits_url']:
    cfg.gizwits_url = GIZWITS_URL
    logging.info(f"Using {cfg.gizwits_url}")

logging.info("Logging in")
token = BestwayUserToken(cfg.token)
api = BestwayAPI(cfg.gizwits_url)
token = api.check_login(token, cfg.username, cfg.password)

raw_format = False
raw_sorted = False

if args.raw:
    logging.info(f"Output in raw JSON format")
    raw_format = True
if args.sorted:
    logging.info(f"Sort raw JSON output")
    raw_sorted = True

device = api.get_device(token, cfg.did)
logging.debug(f"Got device: {device}")

if raw_format:
    raw_data = device._get_raw_status(token)
    keys = raw_data.keys()
    if raw_sorted: keys = sorted(keys)
    print("{")
    for key in keys:
        print(f"  '{key}': '{raw_data[key]}',")
    print("}")
else:
    device_status = device.get_status(token)
    temp_now = device_status.get_temp()
    temp_unit = device_status.get_temp_unit()
    pump_state = device_status.get_pump_is_on()
    heat_state = device_status.get_heat_is_on()
    print(f"Temperature is {temp_now}{temp_unit}")
    print(f"Filter pump is {'ON' if pump_state else 'OFF'}")
    print(f"Heater is {'ON' if heat_state else 'OFF'}")

logging.info("Saving configuration")
cfg.token = dict(token)
cfg.toFile(args.cfgfile)

logging.info("Done.")
