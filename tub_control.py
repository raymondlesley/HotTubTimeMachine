#!/usr/bin/python3
# tub_control - control Hot Tub filter pump
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

logging.info("checking devices")
devices = api.get_devices(token)
logging.debug(f"Devices: {devices}")

device_info = {}
logging.info("Found devices:")
for device in devices:
    logging.info(f"  Device: {device['dev_alias']} ({device['product_name']} = {device['did']})")
    device_info[device['did']] = {'name': device['dev_alias'], 'type': device['product_name']}

# check configured device exists
if not cfg.did in device_info.keys():
    logging.error(f"No device with did {cfg.did} associated with account")
    sys.exit("Unable to continue. Exiting.")
else:
    our_device = device_info[cfg.did]
    device_type = our_device['type']
    if device_type == 'Airjet':
        logging.info(f"Device type: {device_type}")
    elif device_type == 'Airjet_V01':
        logging.info(f"Device type: {device_type}")
    else:
        info.error(f"Device type {device_type} unknown")
        sys.exit("Unable to continue. Exiting.")

if controlling:
    logging.info("applying controls")
    if our_device['type'] == 'Airjet':
        api.set_Airjet_controls(token, cfg.did, pump, heat, temp, bubbles, delay, timer)
    elif our_device['type'] == 'Airjet_V01':
        api.set_Airjet_V01_controls(token, cfg.did, pump, heat, temp, bubbles, delay, timer)

else:
    logging.info("Getting device info")
    info = api.get_device_info(token, cfg.did)
    logging.debug(f"Device Info: {info}")
    attrs = info['attr']
    # check protocol version
    if device_type == 'Airjet':
        # older version
        temp_now = attrs['temp_now']
        if ['temp_set_unit'] == '摄氏':
            temp_unit = '°C'
        else:
            temp_unit = '°F'
        if attrs['filter_power']:
            pump_state = 'ON'
        else:
            pump_state = 'OFF'
        if attrs['heat_power']:
            heat_state = 'ON'
        else:
            heat_state = 'OFF'
    elif device_type == 'Airjet_V01':
        # newer version
        temp_now = attrs['Tnow']
        if attrs['Tunit'] == 1:
            temp_unit = '°C'
        else:
            temp_unit = '°F'
        if attrs['filter']:
            pump_state = 'ON'
        else:
            pump_state = 'OFF'
        if attrs['heat']:
            heat_state = 'ON'
        else:
            heat_state = 'OFF'

        print(f"Temperature is {temp_now}{temp_unit}")
    print(f"Filter pump is {pump_state}")
    print(f"Heater is {heat_state}")

logging.info("Saving configuration")
cfg.token = dict(token)
cfg.toFile(args.cfgfile)

logging.info("Done.")
