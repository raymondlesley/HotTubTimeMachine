#!/usr/bin/python3
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
HEAT_RATE   = 45  # minutes per degree
COOL_RATE   = 300 # minutes per degree
ECO_MINS    = 7 * 60
ECO_END     = "07:30"

# parse arguments
argparser = argparse.ArgumentParser(prog="tub_control.py", description="Hot Tub auto heat control", epilog="with no control arguments [-P, -H, -T] prints current status")
argparser.add_argument('-c', '--cfgfile', help="location of configuration file; default='configuration.json'")
argparser.add_argument('-l', '--loglevel', help="logging level: INFO, DEBUG, WARNING, ERROR, CRITICAL")
argparser.add_argument('-P', '--pump', choices=STATES, default='off', help="set pump 'on' or 'off' before scheduling, default 'off'")
argparser.add_argument('-T', '--temp', type=int, help="override target temperature")
argparser.add_argument('-7', '--economyseven', default=ECO_END, help="time on day when Economy 7 ends, default = '07:30'")
argparser.add_argument('-d', '--display', action='store_true', help="ONLY display current schedule settings")
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

# open API
api = BestwayAPI(cfg.gizwits_url)

logging.info("Logging in")
token = BestwayUserToken(cfg.token)
token = api.check_login(token, cfg.username, cfg.password)
cfg.token = dict(token)

# check thermal coefficients
if not cfg['thermal'] or type(cfg['thermal']) != dict:
    cfg.thermal = {}
    heat_rate = cfg.thermal['heat_rate'] = HEAT_RATE
    cool_rate = cfg.thermal['cool_rate'] = COOL_RATE
else:
    heat_rate = cfg.thermal.get('heat_rate')
    cool_rate = cfg.thermal.get('cool_rate')
if heat_rate is None:
    cfg.thermal['heat_rate'] = heat_rate = HEAT_RATE
if cool_rate is None:
    cfg.thermal['cool_rate'] = cool_rate = COOL_RATE

controlling = False
pump = None
temp = None
eco = None

if args.display:
    logging.info("Displaying current schedule settings")
else:
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
info = api._get_device_info(token, cfg.did)
attrs = info['attr']
logging.debug(attrs)

logging.info("checking devices")
devices = api._get_devices(token)
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
        TEMP_NOW = 'temp_now'
        TARGET_TEMP = 'temp_set'
        TIMER_DURN = 'heat_timer_min'
        TIMER_DELAY = 'heat_appm_min'
    elif device_type == 'Airjet_V01':
        logging.info(f"Device type: {device_type}")
        TEMP_NOW = 'Tnow'
        TARGET_TEMP = 'Tset'
        TIMER_DURN = 'word1'
        TIMER_DELAY = 'word0'
    else:
        info.error(f"Device type {device_type} unknown")
        sys.exit("Unable to continue. Exiting.")

if controlling:
    logging.info("calculating start and duration")
    time_to_heat = 0
    tracked_temp = float(attrs[TEMP_NOW])
    target_temp = float(attrs[TARGET_TEMP])
    if args.temp: target_temp = float(args.temp)
    logging.debug(f"Temp now = {tracked_temp}")
    start_time = 0
    logging.debug(f"target temperature {target_temp} in {minutes_to_go} minutes")
    # TODO: convert iterative algorithm to use algebraic calculation
    #       From symbolab.com/solver: heat_time = (Tend - Tstart + cool_rate * total_time) /  (heat_rate + cool_rate)
    #       (See my Google sheet "Hot Hub Heating Timer")
    while (start_time + time_to_heat) < minutes_to_go:
        # walk forwards from now until the time to start heating is reached
        start_time += STEP_RATE
        tracked_temp -= STEP_RATE / cool_rate
        time_to_heat = int((target_temp - tracked_temp) * heat_rate)
        logging.debug(f"temp after {start_time} minutes = {tracked_temp:.1f}; {time_to_heat} mins heating needed")
    if time_to_heat > 0:
        if time_to_heat > ECO_MINS: time_to_heat = ECO_MINS
        start_time = minutes_to_go - time_to_heat
        logging.info(f"Setting timer to start in {start_time} minutes; heat for {time_to_heat} minutes")
    elif time_to_heat <= 0:
        # -ve heating time - indicates will still be > target temperature after cooling
        start_time = None
        time_to_heat= None
        logging.info(f"temperature ({float(attrs['temp_now'])}) projected to end at {tracked_temp:.1f} - over setpoint {target_temp}")
    logging.info("Sending to Hot Tub")
    if device_type == 'Airjet':
        api.set_Airjet_controls(token, cfg.did, pump, None, target_temp, None, start_time, time_to_heat)
    elif device_type == 'Airjet_V01':
        api.set_Airjet_V01_controls(token, cfg.did, pump, None, target_temp, None, start_time, time_to_heat)
else:
    # TODO: decide how to indicate "report-only" operation
    print(f"Target temperature {attrs[TARGET_TEMP]}")
    print(f"Temperature now {attrs[TEMP_NOW]}")
    print(f"Programmed to heat for {attrs[TIMER_DURN]} minutes, starting in {attrs[TIMER_DELAY]} minutes")

logging.info("Saving configuration")
cfg.toFile(args.cfgfile)

logging.info("Done.")
