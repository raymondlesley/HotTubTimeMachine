#!/usr/bin/python
# log_tub - log Hot Tub current temperature, status to file
#

# TODO: add config options for gizwits API URL, output filename
# TODO: refactor log_config to be fn(), taking options (gleaned from command-line here)
# TODO: refactor Bestway API class(es) into library

import argparse
import logging
import log_config
import csv
import os
import sys
import time
import datetime

from configuration import Configuration
from bestway import Bestway
from bestway_user_token import BestwayUserToken

# CONSTANTS
CFGFILENAME = 'configuration.json'
LOGFILENAME = 'tub_log.csv'

# parse arguments
argparser = argparse.ArgumentParser(prog="log_tub.py", description="Hot Hub logger")
argparser.add_argument('-c', '--cfgfile', help="location of configuration file; default='configuration.json'")
argparser.add_argument('-l', '--loglevel', help="logging level: INFO, DEBUG, WARNING, ERROR, CRITICAL")
argparser.add_argument('-f', '--logfile', help="full pathname of output log file")
argparser.add_argument('--log=INFO', help="(deprecated - for backward compatibility)", action='store_true')
args = argparser.parse_args()

if not args.cfgfile:
    args.cfgfile = os.path.join(os.path.dirname(sys.argv[0]), CFGFILENAME)
    logging.info(f"using configuration file {args.cfgfile}")
if not args.logfile:
    args.logfile = os.path.join(os.path.dirname(sys.argv[0]), LOGFILENAME)

logging.info("Load configuration from file...")
cfg = Configuration.fromFile(args.cfgfile)

logging.info(f"preparing CSV file: {args.logfile}")
csvfile = None
newfile = True
try:
    csvfile = open(args.logfile, newline='')
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
    csvfile = open(args.logfile, 'w')
    writer = csv.writer(csvfile, delimiter=',', quotechar='"', lineterminator="\n")
    writer.writerow(['TIME', 'TEMP_C', 'FILTER', 'HEAT'])
else:
    logging.info("Preparing to append to log file")
    csvfile = open(args.logfile, 'a')
    writer = csv.writer(csvfile, delimiter=',', quotechar='"', lineterminator="\n")

logging.info("Logging in")
token = BestwayUserToken(cfg.token)
api = Bestway("https://euapi.gizwits.com")
token = api.check_login(token, cfg.username, cfg.password)

logging.info("Getting device info")
info = api.get_device_info(token, cfg.did)

logging.info("Logging")
# ['TIME', 'TEMP_C', 'FILTER', 'HEAT']
writer.writerow([datetime.datetime.now().isoformat(),
                 info['attr']['temp_now'],
                 info['attr']['filter_power'],
                 info['attr']['heat_power']
                ])
logging.info("Done.")
