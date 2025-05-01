#!/usr/bin/python3
# tub_heat - control Hot Tub filter heater
#

import argparse
import logging
from tarfile import version

import bestway.bestway_device
import log_config
import csv
import os
import sys
import time
import datetime

from configuration import Configuration
from bestway.bestwayapi import BestwayAPI
from bestway.bestway_user_token import BestwayUserToken

# CONSTANTS
CFGFILENAME = 'configuration.json'
GIZWITS_URL = 'https://euapi.gizwits.com'
STATES      = ['on', 'off']
# parse arguments
argparser = argparse.ArgumentParser(prog="tub_control.py", description="Hot Tub filter heat control", epilog="with no control arguments [-P, -H, -T] prints current status")
argparser.add_argument('-c', '--cfgfile', help="location of configuration file; default='configuration.json'")
argparser.add_argument('-l', '--loglevel', help="logging level: INFO, DEBUG, WARNING, ERROR, CRITICAL")
argparser.add_argument('-D', '--duration', type=int, help="heat for specified duration (in minutes)")
argparser.add_argument('-T', '--temp', type=int, help="heat to target temperature")
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

controlling = False
duration = None
temp = None

if args.duration:
    logging.info(f"Heating for {args.duration} minutes")
    duration = args.duration
    controlling = True
if args.temp:
    logging.info(f"heating to {args.temp} degrees")
    temp = args.temp
    controlling = True

device = api.get_device(token, cfg.did)
logging.debug(f"Got device: {device}")

if controlling:
    device_status = device.get_status(token)
    temp_unit = device_status.get_temp_unit()
    start_temp = device_status.get_temp()
    logging.info(f"Initial temperature {start_temp}{temp_unit}")
    logging.info("applying controls")
    commands = bestway.bestway_device.BestwayCommand()
    if temp: commands.set_target_temp(temp)
    commands.set_heat(True)
    device.send_controls(token, commands)

    if duration:
      end_time = time.time() + duration * 60  # loop until duration seconds
      while time.time() < end_time:
        time.sleep(2)
    elif temp:
      device_status = device.get_status(token)
      temp_now = device_status.get_temp()
      while temp_now < temp:
        time.sleep(60)
        device_status = device.get_status(token)
        temp_now = device_status.get_temp()
      
    commands = bestway.bestway_device.BestwayCommand()
    commands.set_heat(False)
    if temp: commands.set_target_temp(temp)
    device.send_controls(token, commands)
    device_status = device.get_status(token)
    temp_now = device_status.get_temp()
    logging.info(f"Temperature now {temp_now}{temp_unit}")

else:
    # report status
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
