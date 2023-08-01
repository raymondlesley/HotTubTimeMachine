""" Bestway - absration of the Bestway Web API """
""" Tailored for Hot Tub control and monitoring """
""" See: https://github.com/cdpuk/ha-bestway/blob/main/custom_components/bestway/"""

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

# =====================================
# Exceptions

class InvalidToken(Exception):
    def __init__(self):
        super().__init__('Token expired')

# =====================================

class Bestway:
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
        return BestwayUserToken.from_values(r.uid, r.token, r.expire_at)

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

    def set_filter(self, token, device_id, on):
        """set filter (pump) power state: True=on, False=off"""
        if self.is_token_expired(token):
            raise InvalidToken()
        logging.info(f"setting filter power {'ON' if on else 'OFF'}")
        body = {"attrs": {"filter_power": 1 if on else 0}}
        self._post(f"/app/control/{device_id}", self._get_headers(token), body)

    def _get_headers(self, user_token):
        d = dict(HEADERS)
        if user_token: d[GIZWITS_USER_TOKEN] = user_token.user_token
        return d

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
