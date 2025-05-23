#!/usr/bin/python3
# tub_control - control Hot Tub filter pump
#

import argparse
import logging
from tarfile import version

import bestway.bestway_device
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
argparser.add_argument('-P', '--pump', choices=STATES, help="set pump 'on' or 'off'")
argparser.add_argument('-H', '--heat', choices=STATES, help="set heater 'on' or 'off'")
argparser.add_argument('-T', '--temp', type=int, help="set target temperature")
argparser.add_argument('-B', '--bubbles', choices=STATES, help="turn bubbles 'on' or 'off'")
argparser.add_argument('-S', '--schedule', type=int, nargs=2, help="schedule heater: delay, runtime in minutes")
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
pump = None
heat = None
temp = None
bubbles = None
delay = None
timer = None

if args.pump:
    logging.info(f"Setting filter pump {'ON' if args.pump == 'on' else 'OFF'}")
    pump = args.pump == 'on'
    controlling = True
if args.heat:
    logging.info(f"Setting heater {'ON' if args.heat == 'on' else 'OFF'}")
    heat = args.heat == 'on'
    controlling = True
if args.temp:
    logging.info(f"Setting target temperature to {args.temp}")
    temp = args.temp
    controlling = True
if args.bubbles:
    logging.info(f"Turning bubbles {'ON' if args.bubbles == 'on' else 'OFF'}")
    bubbles = args.bubbles == 'on'
    controlling = True
if args.schedule:
    logging.info(f"Setting schedule: delay={args.schedule[0]} duration={args.schedule[1]}")
    delay = args.schedule[0]
    timer = args.schedule[1]
    controlling = True

device = api.get_device(token, cfg.did)
logging.debug(f"Got device: {device}")

if controlling:
    logging.info("applying controls")
    commands = bestway.bestway_device.BestwayCommand()
    if pump: commands.set_pump(pump)
    if heat: commands.set_heat(heat)
    if temp: commands.set_target_temp(temp)
    if bubbles: commands.set_bubbles(bubbles)
    if delay and timer: commands.set_schedule(delay, timer)
    device.send_controls(token, commands)

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
