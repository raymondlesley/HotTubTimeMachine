"""
Bestway Device Airjet - implementation of JSON protocol for
                        Lay-z-Spa Airjet models
"""

import bestway.bestway_device
import bestway.bestway_exceptions as bestway_exceptions

# -- ----------------------------------------------------------------------- --
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
BUBBLES = "wave_power"
BUBBLES_ON = 1
BUBBLES_OFF = 0
TIMER_DURN = 'heat_timer_min'
TIMER_DELAY = 'heat_appm_min'

# -- ----------------------------------------------------------------------- --

class BestwayDeviceAirjet(bestway.bestway_device.BestwayDevice):

    def __get_empty_control(self):
        return {'attrs': {}}

    def __add_control(self, controls, control, value):
        controls["attrs"][control] = value
        return controls

    def get_status(self, token):
        return BestwayStatusAirjet(self._get_raw_status(token))

    def send_controls(self, token, command):
        pump = command.get_pump()
        heat = command.get_heat()
        temp = command.get_temp()
        bubbles = command.get_bubbles()
        delay = command.get_delay()
        duration = command.get_duration()

        controls = self.__get_empty_control()

        logging.info("Setting controls")
        if pump is not None:
            logging.info(f"pump: {'ON' if pump else 'OFF'}")
            self.__add_control(controls, PUMP_STATE, PUMP_STATE_ON if pump else PUMP_STATE_OFF)
        if heat is not None:
            logging.info(f"heat: {'ON' if heat else 'OFF'}")
            self.__add_control(controls, HEAT_STATE, HEAT_STATE_ON if heat else HEAT_STATE_OFF)
        if temp is not None:
            logging.info(f"set temperature to {temp}")
            self.__add_control(controls, TEMP_TARGET, temp)
        if bubbles is not None:
            logging.info(f"turn bubbles {'ON' if bubbles else 'OFF'}")
            self.__add_control(controls, BUBBLES, BUBBLES_ON if bubbles else BUBBLES_OFF)
        if delay is not None and duration is not None:
            logging.info(f"schedule heating in {delay} minutes for {timer} minutes")
            self.__add_control(controls, TIMER_DELAY, delay)
            self.__add_control(controls, TIMER_DURN, duration)
        elif delay is not None or timer is not None:
            raise bestway_exceptions.InvalidArgument("Must specify delay and timer together")
        logging.debug(f"controls: {controls}")

        logging.info("passing controls to API")
        self._get_api().send_controls(token, self._get_device_id(), controls)


# -- ----------------------------------------------------------------------- --

class BestwayStatusAirjet(bestway.bestway_device.BestwayStatus):

    def get_temp(self):
        raw_status = self._get_device_data()
        if TEMP_NOW in raw_status:
            return raw_status[TEMP_NOW]
        else:
            raise bestway_exceptions.UnsupportedDevice()

    def get_temp_unit(self):
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

    def get_bubble_level(self):
        raw_status = self._get_device_data()
        raise NotImplemented()

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
