#
# log_config - common logging setup
#

import logging

DEFAULT_LOG_LEVEL = "WARNING"
def prepare_logging(loglevel):
    if loglevel == None: loglevel = DEFAULT_LOG_LEVEL
    logging.basicConfig(level=loglevel, format='%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s')
    logging.debug(f"logging level = {loglevel}")
