""" Bestway - abstraction of the Bestway Web API """
""" Tailored for Hot Tub control and monitoring """
""" See: https://github.com/cdpuk/ha-bestway/blob/main/custom_components/bestway/"""
""" See: https://docs.gizwits.com/en-us/cloud/OpenAPI.html"""
""" See: https://docs.gizwits.com/en-us/UserManual/UseOpenAPI.html"""

import urllib.request as request
import time
import json
import logging

from bestway.bestway_user_token import BestwayUserToken
import bestway.bestway_exceptions as bestway_exceptions
import bestway.bestway_device as bestway_device
from bestway.bestway_device_airjet import BestwayDeviceAirjet
from bestway.bestway_device_airjet_v01 import BestwayDeviceAirjet_V01

# TODO: create BestwayControl classes
#       ... to replace set_xxxxxx_controls methods

# -- ----------------------------------------------------------------------- --
# CONSTANTS

ENCODING = "utf=8"
HEADERS = {
    "Content-type": "application/json; charset=UTF-8",
    "X-Gizwits-Application-Id": "98754e684ec045528b073876c34c7348",
}
GIZWITS_USER_TOKEN = "X-Gizwits-User-token"
TIMEOUT = 10

# 'Airjet' JSON tags for device control:
PUMP_CTRL = "filter_power"    # filter pump: 1=on, 0=off
HEAT_CTRL = "heat_power"      # heater power: 1=on, 0=off
TEMP_CTRL = "temp_set"        # temperature setpoint (in current scale)
BUBL_CTRL = "wave_power"      # bubbles: 1=on, 0=off
LOCK_CTRL = "locked"          # control panel locked: 1=locked, 0=unlocked
DELY_CTRL = "heat_appm_min"   # delay before heating in minutes
TIME_CTRL = "heat_timer_min"  # heating duration in minutes
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

# -- ----------------------------------------------------------------------- --

class BestwayAPI:
    """Abstraction of the Bestway web API"""

    def __init__(self, baseURL):
        self.baseURL = baseURL
        logging.info(f"initializing Bestway API with {baseURL}")

    def is_token_expired(self, token):
        return time.gmtime(token.expiry) < time.gmtime()

    def get_user_token(self, username, password) -> BestwayUserToken:
        """perform login, return token"""
        body = {"username": username, "password": password, "lang": "en"}
        logging.info("logging in")
        r = self._post("/app/login", dict(HEADERS), body)
        logging.info(f"login response: {r}")
        return BestwayUserToken.from_values(r["uid"], r["token"], r["expire_at"])

    def check_login(self, token, username, password) -> BestwayUserToken:
        """check and refresh token, logging in with username and password if required"""
        if self.is_token_expired(token):
            logging.warning("token expired - logging in")
            token = self.get_user_token(username, password)
        return token

    def _get_devices(self, token):
        """ retrieve list of configured devices"""
        if self.is_token_expired(token):
            raise bestway_exceptions.InvalidToken()
        devices = self._get("/app/bindings", self._get_headers(token))
        # remove unnecessary layer
        if devices['devices']:
            return devices['devices']
        else:
            return []

    def get_device_raw_info(self, token, device_id):
        """retrieve current device status"""
        if self.is_token_expired(token):
            raise bestway_exceptions.InvalidToken()
        logging.info(f"getting info for device {device_id}")
        return self._get(f"/app/devdata/{device_id}/latest", self._get_headers(token))

    def _get_device_raw(self, token, device_id):
        raw_devices = self._get_devices(token)
        for device in raw_devices:
            if 'did' in device:
                if device['did'] == device_id:
                    return device
            else:
                raise bestway_exceptions.UnsupportedDevice()

    def get_device(self, token, device_id):
        raw_device = self._get_device_raw(token, device_id)
        if raw_device:
            if 'product_name' in raw_device:
                type = raw_device['product_name']
            else:
                raise bestway_exceptions.UnsupportedDevice()
            if type == bestway_device.AIRJET:
                return BestwayDeviceAirjet(self, device_id, raw_device)
            elif type == bestway_device.AIRJET_V01:
                return BestwayDeviceAirjet_V01(self, device_id, raw_device)
            else:
                raise bestway_exceptions.UnsupportedDevice()
        else:
            raise bestway_exceptions.UnknownDevice(device_id)

    def set_Airjet_controls(self, token, device_id, pump=None, heat=None, temp=None, bubbles=None, delay=None, timer=None):
        """
        control Hot Tub ('Airjet' devices):
        token = security token [see get_user_token()]
        device_id = id of Hot Tub [see get_devices()]
        pump = filter pump: True = on, False = off
        heat = heater: True = on, False = off
        bubbles: True = on, False = off
        temp = target temperature (in current scale)
        delay = timer before heating (in minutes)
        timer = time to heat for (in minutes)

        specify delay and timer together
        """
        if self.is_token_expired(token):
            raise bestway_exceptions.InvalidToken()

        controls = self._empty_control()

        logging.info("Setting controls")
        if pump is not None:
            logging.info(f"pump: {'ON' if pump else 'OFF'}")
            self._add_control(controls, PUMP_CTRL, 1 if pump else 0)
        if heat is not None:
            logging.info(f"heat: {'ON' if heat else 'OFF'}")
            self._add_control(controls, HEAT_CTRL, 1 if heat else 0)
        if temp is not None:
            logging.info(f"set temperature to {temp}")
            self._add_control(controls, TEMP_CTRL, temp)
        if bubbles is not None:
            logging.info(f"turn bubbles {'ON' if bubbles else 'OFF'}")
            self._add_control(controls, BUBL_CTRL, 1 if bubbles else 0)
        if delay is not None and timer is not None:
            logging.info(f"schedule heating in {delay} minutes for {timer} minutes")
            self._add_control(controls, DELY_CTRL, delay)
            self._add_control(controls, TIME_CTRL, timer)
        elif delay is not None or timer is not None:
            raise bestway_exceptions.InvalidArgument("Must specify delay and timer together")
        logging.debug(controls)

        logging.info("sending")
        self._post(f"/app/control/{device_id}", self._get_headers(token), controls)

    def set_Airjet_V01_controls(self, token, device_id, pump=None, heat=None, temp=None, bubbles=None, delay=None, timer=None):
        """
        control Hot Tub ('Airjet_V01' devices):
        token = security token [see get_user_token()]
        device_id = id of Hot Tub [see get_devices()]
        pump = filter pump: True = on, False = off
        heat = heater: True = on, False = off
        bubbles: True = on, False = off
        temp = target temperature (in current scale)
        delay = timer before heating (in minutes)
        timer = time to heat for (in minutes)

        specify delay and timer together
        """
        if self.is_token_expired(token):
            raise bestway_exceptions.InvalidToken()

        # For the Airjet_V01, trial and error suggests that the timer and delay
        # need to be send separately, with a delay between.
        # Here, we will send any "switch" options (pump, etc.,) first,
        # then - after a delay - send the timer and delay values

        controls = self._empty_control()
        switches_set = False

        logging.info("Setting controls")
        if pump is not None:
            logging.info(f"pump: {'ON' if pump else 'OFF'}")
            self._add_control(controls, PUMP_CTRL_V01, PUMP_ON_V01 if pump else 0)
            switches_set = True
        if heat is not None:
            logging.info(f"heat: {'ON' if heat else 'OFF'}")
            self._add_control(controls, HEAT_CTRL_V01, HEAT_ON_V01 if heat else 0)
            switches_set = True
        if temp is not None:
            logging.info(f"set temperature to {temp}")
            self._add_control(controls, TEMP_CTRL_V01, temp)
            switches_set = True
        if bubbles is not None:
            # TODO: check values for high/low power
            logging.info(f"turn bubbles {'ON' if bubbles else 'OFF'}")
            self._add_control(controls, BUBL_CTRL_V01, 1 if bubbles else 0)
            switches_set = True

        # send these, then pause for effect before scheduling heat
        if switches_set:
            logging.info("sending switches")
            logging.debug(controls)
            self._post(f"/app/control/{device_id}", self._get_headers(token), controls)
            controls = self._empty_control()
            time.sleep(8)

        if delay is not None and timer is not None:
            logging.info(f"schedule heating in {delay} minutes for {timer} minutes")
            #self._add_control(controls, DELY_CTRL_V01, delay)
            self._add_control(controls, TIME_CTRL_V01, timer)
            # self._add_control(controls, TIMER_CTRL_V01, TIMER_ON_V01)
        elif delay is not None or timer is not None:
            raise bestway_exceptions.InvalidArgument("Must specify delay and timer together")

        logging.info("sending timer")
        logging.debug(controls)
        self._post(f"/app/control/{device_id}", self._get_headers(token), controls)
        controls = self._empty_control()
        time.sleep(8)

        self._add_control(controls, DELY_CTRL_V01, delay)
        logging.info("sending delay")
        logging.debug(controls)
        self._post(f"/app/control/{device_id}", self._get_headers(token), controls)

    def _get_headers(self, user_token):
        d = dict(HEADERS)
        if user_token: d[GIZWITS_USER_TOKEN] = user_token.user_token
        return d

    def _empty_control(self):
        return {"attrs": {}}

    def _add_control(self, controls, control, value):
        controls["attrs"][control] = value
        return controls

    def _get(self, path, headers):
        req = request.Request(f"{self.baseURL}{path}", headers=headers)  # GET
        resp = request.urlopen(req)
        content = resp.read()
        result = json.loads(content)
        return result

    def _post(self, path, headers, data):
        body_data = json.dumps(data).encode(ENCODING)
        req = request.Request(f"{self.baseURL}{path}", headers=headers, data=body_data)  # POST
        resp = request.urlopen(req)
        content = resp.read()
        result = json.loads(content)
        return result

# -- ----------------------------------------------------------------------- --
