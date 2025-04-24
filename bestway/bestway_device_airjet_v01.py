"""
Bestway Device Airjet_V01 - implementation of JSON protocol for
                        Lay-z-Spa Airjet_V01 models

devised by reverse-engineering the JSON data exchanged
"""

import logging
import time

import bestway.bestway_device
import bestway.bestway_exceptions as bestway_exceptions

# -- ----------------------------------------------------------------------- --
# 'Airjet' JSON tags for device info:
TEMP_NOW = 'Tnow'
TEMP_UNIT = 'Tunit'
TEMP_UNIT_C = 1
TEMP_TARGET = 'Tset'
TEMP_STATE = 'word3'
TEMP_REACHED = 1
PUMP_STATE = 'filter'
PUMP_STATE_ON = 2
PUMP_STATE_OFF = 0
HEAT_STATE = 'heat'
HEAT_STATE_ON = 3
HEAT_STATE_OFF = 0
TIMER_DURN = 'word1'
TIMER_DELAY = 'word0'
TIMER_STATE = 'word2'
TIMER_ON = 88 # ?? TODO: check this value!
LOCK_STATE = 'bit6'  # according to https://github.com/cdpuk/ha-bestway/issues/41
LOCKED = 1  # TODO: check
EARTH_STATE = 'bit5'  # according to https://github.com/cdpuk/ha-bestway/issues/41
EARTHED = 1 # TODO: check

# -- ----------------------------------------------------------------------- --
# constants

COMMAND_DELAY = 15  # gap between sending commands (in seconds)

# -- ----------------------------------------------------------------------- --

class BestwayDeviceAirjet_V01(bestway.bestway_device.BestwayDevice):

    def __get_empty_control(self):
        return {'attrs': {}}

    def __add_control(self, controls, control, value):
        controls["attrs"][control] = value
        return controls

    def get_status(self, token):
        return BestwayStatusAirjet_V01(self._get_raw_status(token))

    def send_controls(self, token, command):
        pump = command.get_pump()
        heat = command.get_heat()
        temp = command.get_target_temp()
        bubbles = command.get_bubbles()
        delay = command.get_delay()
        duration = command.get_duration()

        controls = self.__get_empty_control()

        logging.info("Setting switch controls")
        switches_set = False
        if pump is not None:
            logging.info(f"pump: {'ON' if pump else 'OFF'}")
            self.__add_control(controls, PUMP_STATE, PUMP_STATE_ON if pump else PUMP_STATE_OFF)
            switches_set = True
        if heat is not None:
            logging.info(f"heat: {'ON' if heat else 'OFF'}")
            self.__add_control(controls, HEAT_STATE, HEAT_STATE_ON if heat else HEAT_STATE_OFF)
            switches_set = True
        if temp is not None:
            logging.info(f"set temperature to {temp}")
            self.__add_control(controls, TEMP_TARGET, temp)
            switches_set = True
        if bubbles is not None:
            logging.info(f"turn bubbles {'ON' if bubbles else 'OFF'}")
            self.__add_control(controls, BUBBLES, BUBBLES_ON if bubbles else BUBBLES_OFF)
            switches_set = True

        if switches_set:
            logging.info("passing switch controls to API")
            self._get_api().send_controls(token, self._get_device_id(), controls)
            controls = self.__get_empty_control()

        if delay is not None and duration is not None:
            if switches_set: time.sleep(COMMAND_DELAY)  # leave time for tub to stop
            logging.info(f"schedule heating in {delay} minutes for {duration} minutes")
            self.__add_control(controls, TIMER_DURN, duration)
            logging.info(f"sending duration: {controls}")
            self._get_api().send_controls(token, self._get_device_id(), controls)
            time.sleep(COMMAND_DELAY)

            controls = self.__get_empty_control()
            self.__add_control(controls, TIMER_DELAY, delay)
            logging.info(f"sending delay: {controls}")
            self._get_api().send_controls(token, self._get_device_id(), controls)
        elif delay is not None or duration is not None:
            raise bestway_exceptions.InvalidArgument("Must specify delay and timer together")


# -- ----------------------------------------------------------------------- --

class BestwayStatusAirjet_V01(bestway.bestway_device.BestwayStatus):

    def get_temp(self):
        raw_status = self._get_device_data()
        if TEMP_NOW in raw_status:
            return raw_status[TEMP_NOW]
        else:
            raise bestway_exceptions.UnsupportedDevice()

    def get_temp_unit(self):
        raw_status = self._get_device_data()
        if TEMP_UNIT in raw_status:
            if raw_status[TEMP_UNIT] == 1:
                return '°C'
            else:
                return '°F'
        else:
            raise bestway_exceptions.UnsupportedDevice()

    def get_target_temp(self):
        raw_status = self._get_device_data()
        if TEMP_TARGET in raw_status:
            return raw_status[TEMP_TARGET]
        else:
            raise bestway_exceptions.UnsupportedDevice()

    def get_pump_is_on(self):
        raw_status = self._get_device_data()
        if PUMP_STATE in raw_status:
            if raw_status[PUMP_STATE] == PUMP_STATE_ON:
                return True
            else:
                return False
        else:
            raise bestway_exceptions.UnsupportedDevice()

    def get_heat_is_on(self):
        raw_status = self._get_device_data()
        if HEAT_STATE in raw_status:
            if raw_status[HEAT_STATE] == HEAT_STATE_ON:
                return True
            else:
                return False
        else:
            raise bestway_exceptions.UnsupportedDevice()

    def get_timer_duration(self):
        raw_status = self._get_device_data()
        if TIMER_DURN in raw_status:
            return raw_status[TIMER_DURN]
        else:
            raise bestway_exceptions.UnsupportedDevice()

    def get_timer_delay(self):
        raw_status = self._get_device_data()
        if TIMER_DELAY in raw_status:
            return raw_status[TIMER_DELAY]
        else:
            raise bestway_exceptions.UnsupportedDevice()

# -- ----------------------------------------------------------------------- --
