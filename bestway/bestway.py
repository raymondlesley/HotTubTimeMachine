""" Bestway - absration of the Bestway Web API """
""" Tailored for Hot Tub control and monitoring """
""" See: https://github.com/cdpuk/ha-bestway/blob/main/custom_components/bestway/bestway.py"""

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
        body_data = json.dumps(body).encode(ENCODING)
        logging.info("logging in")
        r = self._post("/app/login", dict(HEADERS), body_data)
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

    def get_device_info(self, token, did):
        """retrieve current device status"""
        if self.is_token_expired(token):
            raise InvalidToken()
        logging.info(f"getting info for device {did}")
        return self._get(f"/app/devdata/{did}/latest", self._get_headers(token))

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
        req = request.Request(f"{self.baseURL}{path}", headers=headers, data=data)  # POST
        resp = request.urlopen(req)
        content = resp.read()
        result = json.loads(content)
        return result