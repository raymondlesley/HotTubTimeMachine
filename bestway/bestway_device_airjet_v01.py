"""
Bestway Device Airjet_V01 - implementation of JSON protocol for
                        Lay-z-Spa Airjet_V01 models
"""

import bestway.bestway_device
import bestway.bestway_exceptions as bestway_exceptions

# 'Airjet' JSON tags for device info:
TEMP_NOW = 'Tnow'
TEMP_UNIT = 'Tunit'
TEMP_UNIT_C = 1
TEMP_TARGET = 'Tset'
PUMP_STATE = 'filter'
PUMP_STATE_ON = 2
PUMP_STATE_OFF = 0
HEAT_STATE = 'heat'
HEAT_STATE_ON = 3
HEAT_STATE_OFF = 0
TIMER_DURN = 'word1'
TIMER_DELAY = 'word0'

# 'Airjet_V01' JSON tags for device control:
PUMP_CTRL_V01 = "filter"          # filter pump: 2=on, 0=off
PUMP_ON_V01   = 2
HEAT_CTRL_V01 = "heat"            # heater power: 3=on, 0=off
HEAT_ON_V01   = 3
TEMP_CTRL_V01 = "Tset"            # temperature setpoint (in current scale)
BUBL_CTRL_V01 = "wave"            # bubbles: 1=on, 0=off
LOCK_CTRL_V01 = "locked"          # ?? control panel locked: 1=locked, 0=unlocked
DELY_CTRL_V01 = "word0"   # delay before heating in minutes
TIME_CTRL_V01 = "word1"  # heating duration in minutes
TIMER_CTRL_V01  = "word2"   # ?? timer in operation
TIMER_ON_V01  = 88   # ?? timer in operation

class BestwayDeviceAirjet_V01(bestway.bestway_device.BestwayDevice):

    def get_status(self, token):
        return BestwayStatusAirjet_V01(self._get_raw_status(token))

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
