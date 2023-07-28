import sys
import logging

loglevel = "DEBUG" # default

for arg in sys.argv[1:]:  # ignore program name
    if arg[:6] == "--log=":
        logging.basicConfig(level=arg[6:])
        logging.warning(f"Logging level={arg[6:]}")