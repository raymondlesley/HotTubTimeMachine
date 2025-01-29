#!/usr/bin/python3
# log_tub - log Hot Tub current temperature, status to file
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
LOGFILENAME = 'tub_log.csv'
GIZWITS_URL = 'https://euapi.gizwits.com'

# parse arguments
argparser = argparse.ArgumentParser(prog="tub_log.py", description="Hot Hub logger")
argparser.add_argument('-c', '--cfgfile', help="location of configuration file; default='configuration.json'")
argparser.add_argument('-l', '--loglevel', help="logging level: INFO, DEBUG, WARNING, ERROR, CRITICAL")
argparser.add_argument('-o', '--output', help=f"full pathname of output CSV file; default='{LOGFILENAME}'")
args = argparser.parse_args()

# setup logging
log_config.prepare_logging(args.loglevel)
# setup logfile filename
if not args.cfgfile:
    args.cfgfile = os.path.join(os.path.dirname(sys.argv[0]), CFGFILENAME)
    logging.info(f"using configuration file {args.cfgfile}")
if not args.output:
    args.output = os.path.join(os.path.dirname(sys.argv[0]), LOGFILENAME)

logging.info("Load configuration from file...")
cfg = Configuration.fromFile(args.cfgfile)

logging.info(f"preparing CSV file: {args.output}")
csvfile = None
newfile = True
try:
    csvfile = open(args.output, newline='')
    newfile = False
    firstline = csvfile.readline(256)
    if not csv.Sniffer().has_header(firstline):
        logging.warning("CSV badly formatted? Overwriting...")
        csvfile.close()
        newfile = True
except FileNotFoundError as err:
    logging.warning("Log file not found. Starting a new file")
    newfile = True
except csv.Error as err:
    logging.warning("Log file empty? Starting a new file")
    newfile = True

if newfile:
    logging.info("Starting new log file")
    csvfile = open(args.output, 'w')
    writer = csv.writer(csvfile, delimiter=',', quotechar='"', lineterminator="\n")
    writer.writerow(['TIME', 'TEMP_C', 'FILTER', 'HEAT'])
else:
    logging.info("Preparing to append to log file")
    csvfile = open(args.output, 'a')
    writer = csv.writer(csvfile, delimiter=',', quotechar='"', lineterminator="\n")

# check Gizwits URL
if not cfg['gizwits_url']:
    cfg.gizwits_url = GIZWITS_URL
    logging.info(f"Using {cfg.gizwits_url}")

logging.info("Logging in")
token = BestwayUserToken(cfg.token)
api = BestwayAPI(cfg.gizwits_url)
token = api.check_login(token, cfg.username, cfg.password)

"""
logging.info("Getting device info")
info = api._get_device_info(token, cfg.did)
"""
device = api.get_device(token, cfg.did)
logging.info(f"Got device: {device}")

device_status = device.get_status(token)
temp_now = device_status.get_temp()
pump_state = device_status.get_pump_is_on()
heat_state = device_status.get_heat_is_on()

logging.info("Logging")
# ['TIME', 'TEMP_C', 'FILTER', 'HEAT']
writer.writerow([datetime.datetime.now().isoformat(),
                 temp_now,
                 'ON' if pump_state else 'OFF',
                 'ON' if heat_state else 'OFF'
                ])

logging.info("Saving configuration")
cfg.token = dict(token)
cfg.toFile(args.cfgfile)

logging.info("Done.")
