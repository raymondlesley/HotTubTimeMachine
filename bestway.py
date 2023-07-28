""" Bestway - absration of the Bestway Web API """
""" Tailored for Hot Tub control and monitoring """
""" See: https://github.com/cdpuk/ha-bestway/blob/main/custom_components/bestway/bestway.py"""

import urllib
import time
import json

# =====================================
# CONSTANTS

ENCODING = "utf=8"
HEADERS = {
    "Content-type": "application/json; charset=UTF-8",
    "X-Gizwits-Application-Id": "98754e684ec045528b073876c34c7348",
}
TIMEOUT = 10

# =====================================

class Bestway:
    """Abstraction of the Bestway web API"""

    def __init__(self, baseURL):
        self.baseURL = baseURL

    def isTokenExpired(self, token):
        return time.gmtime(token.expiry) < time.gmtime()

    def getUserToken(self, username, password):
        body = {"username": username, "password": password, "lang": "en"}
        body_data = json.dumps(body).encode(ENCODING)
        r = self._POST("/app/login", body_data)
        return BestwayUserToken(response.uid, r.token, r.expire_at)

    def _POST(self, path, data):
        req = urllib.request.Request(f"{self.baseURL}{path}", headers=HEADERS, data=data)  # POST
        resp = urllib.request.urlopen(req)
        content = resp.read()
        result = json.loads(content)
        return result
