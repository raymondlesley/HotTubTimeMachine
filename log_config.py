import sys
import logging

loglevel = "DEBUG" # default

for arg in sys.argv[1:]:  # ignore program name
    if arg[:6] == "--log=":
        logging.basicConfig(level=arg[6:], format='%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s')
        logging.warning(f"Logging level={arg[6:]}")