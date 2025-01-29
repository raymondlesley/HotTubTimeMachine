"""
Bestway Device - abstraction of Bestway (Lay-z-Spa) device capabilities

This is a base class

devised by reverse-engineering the JSON data exchanged
"""

#import json
import logging

import bestway.bestwayapi

# =====================================
# constants
AIRJET = 'Airjet'
AIRJET_V01 = 'Airjet_V01'


# =====================================

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
            raise UnsupportedDevice()
        if 'dev_alias' in raw_device_data:
            self.__name = raw_device_data['dev_alias']
        else:
            raise UnsupportedDevice()

    def __repr__(self):
        return f"BestwayDevice: {self.__name} ({self.__type})"

    # internal getters

    def _get_api(self):
        return self.__api

    def _get_device_id(self):
        return self.__device_id

    def get_device_type(self):
        return self.__type

    def get_raw_status(self, token):
        raw_device_info = self._get_api()._get_device_info(token, self._get_device_id())
        if 'attr' in raw_device_info:
            return raw_device_info['attr']
        else:
            raise bestway_exceptions.UnsupportedDevice()

    # override methods
    def get_temp(self, raw_status):
        raise NotImplemented()

    def get_temp_unit(self, raw_status):
        raise NotImplemented()

    def get_pump_is_on(self, raw_status):
        raise NotImplemented()

    def get_heat_is_on(self, raw_status):
        raise NotImplemented()