"""
Bestway Device Airjet - implementation of JSON protocol for
                        Lay-z-Spa Airjet models
"""

import bestway.bestway_device
import bestway.bestway_exceptions as bestway_exceptions

# 'Airjet' JSON tags for device info:
TEMP_NOW = 'temp_now'
TEMP_UNIT = 'temp_set_unit'
TEMP_UNIT_C = '摄氏'
TEMP_TARGET = 'temp_set'
PUMP_STATE = 'filter_power'
PUMP_STATE_ON = 1
PUMP_STATE_OFF = 0
HEAT_STATE = 'heat_power'
HEAT_STATE_ON = 1
HEAT_STATE_OFF = 0
TIMER_DURN = 'heat_timer_min'
TIMER_DELAY = 'heat_appm_min'

# 'Airjet' JSON tags for device control:
PUMP_CTRL = "filter_power"    # filter pump: 1=on, 0=off
HEAT_CTRL = "heat_power"      # heater power: 1=on, 0=off
TEMP_CTRL = "temp_set"        # temperature setpoint (in current scale)
BUBL_CTRL = "wave_power"      # bubbles: 1=on, 0=off
LOCK_CTRL = "locked"          # control panel locked: 1=locked, 0=unlocked
DELY_CTRL = "heat_appm_min"   # delay before heating in minutes
TIME_CTRL = "heat_timer_min"  # heating duration in minutes

class BestwayDeviceAirjet(bestway.bestway_device.BestwayDevice):

    def get_status(self, token):
        return BestwayStatusAirjet(self._get_raw_status(token))


class BestwayStatusAirjet(bestway.bestway_device.BestwayStatus):
    def get_temp(self):
        raw_status = self._get_device_data()
        if TEMP_NOW in raw_status:
            return raw_status[TEMP_NOW]
        else:
            raise bestway_exceptions.UnsupportedDevice()

    def get_temp_unit(self, raw_status):
        raw_status = self._get_device_data()
        if TEMP_UNIT in raw_status:
            if raw_status[TEMP_UNIT] == TEMP_UNIT_C:
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

    def get_pump_is_on(self, raw_status):
        raw_status = self._get_device_data()
        if PUMP_STATE in raw_status:
            if raw_status[PUMP_STATE] == PUMP_STATE_ON:
                return True
            else:
                return False
        else:
            raise bestway_exceptions.UnsupportedDevice()

    def get_heat_is_on(self, raw_status):
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
