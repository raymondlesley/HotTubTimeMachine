# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from configuration import Configuration
import datetime
import time
import logging

logging.info("Configuration from file...")
cfg = Configuration.fromFile("../configuration.json")
logging.info(f"username=\"{cfg.username}\"")
#logging.info(cfg)

logging.info("Store configuration to file")
cfg.datetime = datetime.datetime.now().isoformat()
cfg.toFile("configuration.json")

logging.info("test nonexistent file")
nocfg = Configuration.fromFile("doesnotexist")
logging.info(nocfg)

from bestway.bestway import Bestway
from bestway.bestway_user_token import BestwayUserToken

logging.info("Test token from dict")
token = BestwayUserToken(cfg.token)
logging.info(f"user_id={token.user_id}")

logging.info("Test dict from token")
d = dict(token)
logging.info(f"['user_id']='{d['user_id']}")

logging.info("Check token validity")
try:
    token = BestwayUserToken(cfg.token)
    logging.info("token is valid")
except:
    token = BestwayUserToken.from_values("", "", 0)
    logging.info("error: using empty token")
logging.info("init Bestway API")
api = Bestway("https://euapi.gizwits.com")
if api.is_token_expired(token):
    logging.warning("Token expired - renewing...")
    token = api.get_user_token(cfg.username, cfg.password)
    logging.info(token)
else:
    logging.info(f"Token OK - expires: {time.asctime(time.gmtime(token.expiry))}")

logging.info("Getting devices")
results = api.get_devices(token)
#logging.info(results)
devices = {}
for device in results:
    devices[device['did']] = {"name": device['dev_alias'], "product": device['product_name']}
    #logging.info(f"found: {device['dev_alias']} ({device['product_name']}): {device['did']}")
    logging.info(f"{device['did']}: {devices[device['did']]}")

logging.info("Getting device info")
info = api.get_device_info(token, cfg.did)
logging.info(info)
logging.info(f"{devices[cfg.did]['name']}:"
             f" {info['attr']['temp_now']}'C"
             f" filter={'ON' if info['attr']['filter_power'] else 'OFF'}"
             f" heater={'ON' if info['attr']['heat_power'] else 'OFF'}"
             )

"""
logging.info("using http library")
import http.client
conn = http.client.HTTPSConnection("www.bbc.co.uk")
conn.request("GET", "/nosuchendpoint", headers={"Host": "www.bbc.co.uk"})
response = conn.getresponse()
print(response.status, response.reason)
print(response)
"""

logging.info("Store valid token")
cfg.token = dict(token)
cfg.toFile("configuration.json")

logging.debug("done.")