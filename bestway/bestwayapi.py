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

# -- ----------------------------------------------------------------------- --
# CONSTANTS

ENCODING = "utf=8"
HEADERS = {
    "Content-type": "application/json; charset=UTF-8",
    "X-Gizwits-Application-Id": "98754e684ec045528b073876c34c7348",
}
GIZWITS_USER_TOKEN = "X-Gizwits-User-token"
TIMEOUT = 10

# -- ----------------------------------------------------------------------- --

class BestwayAPI:
    """Abstraction of the Bestway web API"""

    def __init__(self, baseURL):
        self.baseURL = baseURL
        logging.debug(f"initializing Bestway API with {baseURL}")

    def is_token_expired(self, token):
        return time.gmtime(token.expiry) < time.gmtime()

    def get_user_token(self, username, password) -> BestwayUserToken:
        """perform login, return token"""
        body = {"username": username, "password": password, "lang": "en"}
        logging.debug("logging in")
        r = self._post("/app/login", dict(HEADERS), body)
        logging.debug(f"login response: {r}")
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
        logging.debug(f"getting info for device {device_id}")
        return self._get(f"/app/devdata/{device_id}/latest", self._get_headers(token))

    def _get_device_raw(self, token, device_id):
        raw_devices = self._get_devices(token)
        for device in raw_devices:
            if 'did' in device:
                if device['did'] == device_id:
                    return device
        raise bestway_exceptions.UnsupportedDevice()

    def get_device(self, token, device_id):
        raw_device = self._get_device_raw(token, device_id)
        if raw_device:
            if 'product_name' in raw_device:
                device_type = raw_device['product_name']
            else:
                raise bestway_exceptions.UnsupportedDevice()
            if ('is_online' in raw_device) & (raw_device['is_online']) == False:
                raise bestway_exceptions.DeviceOffline()

            if device_type == bestway_device.AIRJET:
                return BestwayDeviceAirjet(self, device_id, raw_device)
            elif device_type == bestway_device.AIRJET_V01:
                return BestwayDeviceAirjet_V01(self, device_id, raw_device)
            else:
                raise bestway_exceptions.UnsupportedDevice()
        else:
            raise bestway_exceptions.UnknownDevice(device_id)

    def send_controls(self, token, device_id, controls):
        logging.debug(f"controls: {controls}")
        logging.debug("sending controls")
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
