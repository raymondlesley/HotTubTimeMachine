""" Bestway - absration of the Bestway Web API """
""" Tailored for Hot Tub control and monitoring """
""" See: https://github.com/cdpuk/ha-bestway/blob/main/custom_components/bestway/bestway.py"""

import urllib.request as request
import time
import json
import logging

from bestway_user_token import BestwayUserToken

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

    def isTokenExpired(self, token):
        return time.gmtime(token.expiry) < time.gmtime()

    def get_user_token(self, username, password):
        body = {"username": username, "password": password, "lang": "en"}
        body_data = json.dumps(body).encode(ENCODING)
        r = self._post("/app/login", dict(HEADERS), body_data)
        return BestwayUserToken.from_values(r.uid, r.token, r.expire_at)

    def get_devices(self, token):
        if self.isTokenExpired(token):
            raise InvalidToken()
        return self._get("/app/bindings", self._get_headers(token))

    def get_device_info(self, token, did):
        if self.isTokenExpired(token):
            raise InvalidToken()
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
