"""
Bestway Device - abstraction of Bestway (Lay-z-Spa) device capabilities

This is a base class
"""

import logging

import bestway.bestwayapi
import bestway.bestway_exceptions as bestway_exceptions

# -- ----------------------------------------------------------------------- --
# constants

AIRJET = 'Airjet'
AIRJET_V01 = 'Airjet_V01'

# -- ----------------------------------------------------------------------- --

class BestwayDevice:
    """ Abstract Bestway Device base class"""

    # constructor
    def __init__(self, api, device_id, raw_device_data):
        logging.debug(f"Constructing BestwayDevice({raw_device_data})")
        self.__api = api
        self.__device_id = device_id
        self.__device_data = raw_device_data
        if 'product_name' in raw_device_data:
            self.__type = raw_device_data['product_name']
        else:
            raise bestway_exceptions.UnsupportedDevice()
        if 'dev_alias' in raw_device_data:
            self.__name = raw_device_data['dev_alias']
        else:
            raise bestway_exceptions.UnsupportedDevice()

    def __repr__(self):
        return f"BestwayDevice: {self.__name} ({self.__type})"

    # internal getters

    def _get_api(self):
        return self.__api

    def _get_device_id(self):
        return self.__device_id

    def get_device_type(self):
        return self.__type

    def _get_raw_status(self, token):
        raw_device_info = self._get_api().get_device_raw_info(token, self._get_device_id())
        if 'attr' in raw_device_info:
            return raw_device_info['attr']
        else:
            raise bestway_exceptions.UnsupportedDevice()

    # override methods

    def get_status(self, token):
        raise NotImplemented()

    def send_controls(self, command):
        raise NotImplemented()


# -- ----------------------------------------------------------------------- --

class BestwayStatus:
    """ Abstract Bestway Device Status base class"""

    # constructor
    def __init__(self, raw_device_data):
        logging.debug(f"Constructing BestwayStatus({raw_device_data})")
        self.__device_data = raw_device_data

    def __repr__(self):
        return f"BestwayStatus: {self.__device_data})"

    def _get_device_data(self):
        return self.__device_data

    # override methods

    def get_temp(self):
        raise NotImplemented()

    def get_temp_unit(self):
        raise NotImplemented()

    def get_target_temp(self):
        raise NotImplemented()

    def get_pump_is_on(self):
        raise NotImplemented()

    def get_heat_is_on(self):
        raise NotImplemented()

    def get_bubble_level(self):
        raise NotImplemented()

    def get_timer_duration(self):
        raise NotImplemented()

    def get_timer_delay(self):
        raise NotImplemented()


# -- ----------------------------------------------------------------------- --

# BestwayCommand
# encapsulate a (set of) option(s)
# allows controls to be batched up and sent in one go

class BestwayCommand:

    def __init__(self):
        self.__pump = None
        self.__heat = None
        self.__temp = None
        self.__bubbles = None
        self.__delay = None
        self.__duration = None

    def set_pump(self, on):
        self.__pump = on

    def set_heat(self, on):
        self.__heat = on

    def set_bubbles(self, on):
        self.__bubbles = on

    def set_target_temp(self, temp):
        self__temp = temp

    def set_schedule(self, delay, duration):
        self.__delay = delay
        self.__duration = duration

    def get_pump(self):
        return self.__pump

    def get_heat(self):
        return self.__heat

    def get_target_temp(self):
        return self.__temp

    def get_bubbles(self):
        return self.__bubbles

    def get_delay(self):
        return self.__delay

    def get_duration(self):
        return self.__duration


# -- ----------------------------------------------------------------------- --
