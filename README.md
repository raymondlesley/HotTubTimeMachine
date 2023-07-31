# HotTubTimeMachine
## Purpose
A Python abstraction of the Bestway cloud API to control and monitor a Lay-Z-Spa hot tub.
## How to use
Two main library elements are provided:
* Configuration - manage a JSON file to store key configuration data
* bestway - Package providing the API abstraction itself

Take a look at log_tub.py for more clues as to how this is used
## History
This project started out as an experiment to talk to the Bestway cloud API from Python.
It has grown from there and now boasts a single, useful script: log_tub.py.
This is designed to be run periodically (e.g. from cron) to log tub status: temperature and pump heat on/off
