# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from configuration import Configuration
import datetime
import time
from testbed import testbed
import logging
import log_config

logging.info("Configuration from file...")
cfg = Configuration.fromFile("configuration.json")
logging.info(f"username=\"{cfg.username}\"")
logging.info(cfg)

logging.info("Store configuration to file")
cfg.datetime = datetime.datetime.now().isoformat()
cfg.toFile("configuration.json")

logging.info("test nonexistent file")
nocfg = Configuration.fromFile("doesnotexist")
logging.info(nocfg)

from bestway import Bestway
from bestway_user_token import BestwayUserToken

logging.info("Test token from dict")
token = BestwayUserToken(cfg.token)
logging.info(token)

logging.info("Test dict from token")
d = dict(token)
logging.info(d)

logging.info("Check token validity")
try:
    token = BestwayUserToken(cfg.token)
except:
    token = BestwayUserToken.from_values("", "", 0)
logging.info("init Bestway API")
api = Bestway("https://euapi.gizwits.com")
if api.isTokenExpired(token):
    logging.warning("Token expired - renewing...")
    token = api.get_user_token(cfg.username, cfg.password)
    logging.info(token)
else:
    logging.info(f"Token OK - expires: {time.asctime(time.gmtime(token.expiry))}")

results = api.get_devices(token)
logging.info(results)
for device in results["devices"]:
    logging.info(f"found: {device['dev_alias']} ({device['product_name']}): {device['did']}")

results = api.get_device_info(token, cfg.did)
logging.info(results)

logging.info("Store valid token")
cfg.token = dict(token)
cfg.toFile("configuration.json")

logging.debug("done.")