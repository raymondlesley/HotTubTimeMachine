# HotTubTimeMachine
## Purpose
A Python abstraction of the Bestway cloud API to control and monitor a Lay-Z-Spa hot tub.

Fuelled by frustration at the limited control offered by the
Bestway API and Android app, the aim is to provide a level
of automation for Bestway / Lay-Z-Spa hot tubs.

In an effort to ensure the widest compatibility,
and easiest deployment, no additional libraries are used -
using only those shipped with Python.

## How to Use
Two main library elements are provided:
* Configuration - manage a JSON file to store key configuration data
* bestway - Package providing the API abstraction itself
Take a look at tub_control.py for more clues as to how this is used

N.B: the API hostname is set to the EU instance at present.
For use in USA, set the configuration element "gizwits_api"
to "https://usapi.gizwits.com"

## History
This project started out as an experiment to talk to the Bestway cloud API from Python.
It has taken inspiration from the Home Automation plugin
for Bestway:
https://github.com/cdpuk/ha-bestway/blob/main/custom_components/bestway/bestway.py

It has grown from a proof-of-concept (which initially could only successfully log in)
and now boasts a state logger: tub_log.py
and tbu controls for pump on/off, heat on/off, etc.: tub_control.py

These are designed to be run periodically (e.g. from cron)
to automatically turn the filter pump on and off at set times
or to record a history of tub status: temperature and pump/heat on/off

## Future Plans
The ambition is to expand the capabilities to include:
* control for turning the heater
on and off according to a configured schedule
* smart heating to automatically turn heater on in good time to
reach a set temperature at a given time
