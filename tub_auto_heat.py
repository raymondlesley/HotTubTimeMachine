#!/usr/bin/python
# tub_auto_heat - calculate and program Hot Tub heating to reach target temp
#
# designed for heating on Economy-7 cheap, overnight electricity
#

import argparse
import logging
import log_config
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
STEP_RATE   = 10  # minutes per iteration for calculating heat time
HEAT_RATE   = 1.0/45  # degrees per minute
COOL_RATE   = 1.0/300 # degrees per minutes

# parse arguments
argparser = argparse.ArgumentParser(prog="tub_control.py", description="Hot Tub auto heat control", epilog="with no control arguments [-P, -H, -T] prints current status")
argparser.add_argument('-c', '--cfgfile', help="location of configuration file; default='configuration.json'")
argparser.add_argument('-l', '--loglevel', help="logging level: INFO, DEBUG, WARNING, ERROR, CRITICAL")
argparser.add_argument('-P', '--pump', choices=STATES, default='off', help="set pump 'on' or 'off' before scheduling, default 'off'")
argparser.add_argument('-T', '--temp', type=int, help="override target temperature")
argparser.add_argument('-7', '--economyseven', default='07:30', help="time on day when Economy 7 ends, default = '07:30'")
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
temp = None
eco = None

if args.pump:
    logging.info(f"Setting filter pump {'ON' if args.pump == 'on' else 'OFF'}")
    pump = args.pump == 'on'
    controlling = True
if args.temp:
    logging.info(f"Setting target temperature to {args.temp}")
    temp = args.temp
    controlling = True
if args.economyseven:
    logging.info(f"Programming target heat for {args.economyseven}")
    eco = args.economyseven

timenow = datetime.datetime.now()
minutes_now = timenow.hour * 60 + timenow.minute
logging.debug(f"Time now = {timenow.hour}:{timenow.minute} ({minutes_now} minutes)")
times = eco.split(':')
logging.debug(times)
minutes = int(times[0]) * 60 + int(times[1])
logging.debug(minutes)
minutes_to_go = minutes + 24 * 60 - minutes_now
logging.info(f"Economy 7 ends in {minutes_to_go} minutes")

logging.info("Getting device info")
info = api.get_device_info(token, cfg.did)
attrs = info['attr']
logging.debug(attrs)

if controlling:
    logging.info("calculating start and duration")
    time_to_heat = 0
    tracked_temp = float(attrs['temp_now'])
    target_temp = float(attrs['temp_set'])
    if args.temp: target_temp = float(args.temp)
    logging.debug(f"Temp now = {tracked_temp}")
    start_time = 0
    logging.debug(f"target temperature {target_temp} in {minutes_to_go} minutes")
    while (start_time + time_to_heat) < minutes_to_go:
        # walk forwards from now until the time to start heating is reached
        start_time += STEP_RATE
        tracked_temp -= STEP_RATE * COOL_RATE
        time_to_heat = int((target_temp - tracked_temp) / HEAT_RATE)
        logging.debug(f"temp after {start_time} minutes = {tracked_temp:.1f}; {time_to_heat} mins heating needed")
    start_time = minutes_to_go - time_to_heat
    logging.info(f"Setting timer to start in {start_time} minutes; heat for {time_to_heat} minutes")
    api.set_controls(token, cfg.did, pump, None, target_temp, None, start_time, time_to_heat)
else:
    # TODO: decide how to indicate "report-only" operation
    print(f"Target temperature {attrs['temp_set']}")
    print(f"Temperature now {attrs['temp_now']}")
    print(f"Programmed to heat for {attrs['heat_timer_min']} minutes, starting in {attrs['heat_appm_min']} minutes")
