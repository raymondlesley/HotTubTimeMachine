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

# =====================================
# CONSTANTS

ENCODING = "utf=8"
HEADERS = {
    "Content-type": "application/json; charset=UTF-8",
    "X-Gizwits-Application-Id": "98754e684ec045528b073876c34c7348",
}
GIZWITS_USER_TOKEN = "X-Gizwits-User-token"
TIMEOUT = 10

PUMP_CTRL = "filter_power"    # filter pump: 1=on, 0=off
HEAT_CTRL = "heat_power"      # heater power: 1=on, 0=off
TEMP_CTRL = "temp_set"        # temperature setpoint (in current scale)
BUBL_CTRL = "wave_power"      # bubbles: 1=on, 0=off
LOCK_CTRL = "locked"          # control panel locked: 1=locked, 0=unlocked
DELY_CTRL = "heat_appm_min"   # delay before heating in minutes
TIME_CTRL = "heat_timer_min"  # heating duration in minutes

# =====================================
# Exceptions

class InvalidToken(Exception):
    def __init__(self):
        super().__init__('Token expired')

class InvalidArgument(Exception):
    def __init__(self, message):
        super().__init__(message)

# =====================================

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

    def get_devices(self, token):
        """ retrieve list of configured devices"""
        if self.is_token_expired(token):
            raise InvalidToken()
        devices = self._get("/app/bindings", self._get_headers(token))
        # remove unnecessary layer
        if devices['devices']:
            return devices['devices']
        else:
            return []

    def get_device_info(self, token, device_id):
        """retrieve current device status"""
        if self.is_token_expired(token):
            raise InvalidToken()
        logging.info(f"getting info for device {device_id}")
        return self._get(f"/app/devdata/{device_id}/latest", self._get_headers(token))

    def set_controls(self, token, device_id, pump=None, heat=None, temp=None, bubbles=None, delay=None, timer=None):
        """
        control Hot Tub:
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
            raise InvalidToken()

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
            raise InvalidArgument("Must specify delay and timer together")
        logging.debug(controls)

        logging.info("sending")
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
