#
# log_tub - log Hot Tub current temperature, status to file
#

import logging
import log_config
import csv
import time
import datetime

from configuration import Configuration
from bestway import Bestway
from bestway_user_token import BestwayUserToken

logging.info("Configuration from file...")
cfg = Configuration.fromFile("configuration.json")

logging.info("preparing CSV file")
LOGFILE = 'tub_log.csv'
csvfile = None
newfile = True
try:
    csvfile = open(LOGFILE, newline='')
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
    csvfile = open(LOGFILE, 'w')
    writer = csv.writer(csvfile, delimiter=',', quotechar='"', lineterminator="\n")
    writer.writerow(['TIME', 'TEMP_C', 'FILTER', 'HEAT'])
else:
    logging.info("Preparing to append to log file")
    csvfile = open(LOGFILE, 'a')
    writer = csv.writer(csvfile, delimiter=',', quotechar='"', lineterminator="\n")

logging.info("Logging in")
token = BestwayUserToken(cfg.token)
api = Bestway("https://euapi.gizwits.com")
token = api.check_login(token, cfg.username, cfg.password)

logging.info("Getting device info")
info = api.get_device_info(token, cfg.did)
logging.info(info)

# ['TIME', 'TEMP_C', 'FILTER', 'HEAT']
writer.writerow([datetime.datetime.now().isoformat(),
                 info['attr']['temp_now'],
                 info['attr']['filter_power'],
                 info['attr']['heat_power']
                ])
