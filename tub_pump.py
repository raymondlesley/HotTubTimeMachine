#!/usr/bin/python
# log_tub - control Hot Tub filter pump
#

import argparse
import logging
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
argparser = argparse.ArgumentParser(prog="tub_pump.py", description="Hot Tub filter pump control")
argparser.add_argument('state', nargs='?', choices=STATES, help="set pump 'on' or 'off' (default = report state)")
argparser.add_argument('-c', '--cfgfile', help="location of configuration file; default='configuration.json'")
argparser.add_argument('-l', '--loglevel', help="logging level: INFO, DEBUG, WARNING, ERROR, CRITICAL")
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

if not args.state:
    logging.info("Getting device info")
    info = api.get_device_info(token, cfg.did)
    attrs = info['attr']
    logging.debug(attrs)
    print(f"Temperature is {attrs['temp_now']}°{'C' if attrs['temp_set_unit'] == '摄氏' else 'F'}")
    print(f"Filter pump is {'ON' if attrs['filter_power'] else 'OFF'}")
    print(f"Heater is {'ON' if attrs['heat_power'] else 'OFF'}")
elif args.state not in STATES:
    logging.error(f"{args.state} is an invalid state - must be one of: on, off")
else:
    logging.info("Setting filter pump {'ON' if args.state == 'on' else 'OFF'}")
    api.set_filter(token, cfg.did, args.state=='on')

logging.info("Saving configuration")
cfg.token = dict(token)
cfg.toFile(args.cfgfile)

logging.info("Done.")
