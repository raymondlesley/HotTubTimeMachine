""" Bestway - absration of the Bestway Web API """
""" Tailored for Hot Tub control and monitoring """
""" See: https://github.com/cdpuk/ha-bestway/blob/main/custom_components/bestway/bestway.py"""

HEADERS = {
    "Content-type": "application/json; charset=UTF-8",
    "X-Gizwits-Application-Id": "98754e684ec045528b073876c34c7348",
}
TIMEOUT = 10

#@dataclass
class BestwayUserToken:
    """User authentication token, obtained (and ideally stored) following a successful login."""

    user_id: str
    user_token: str
    expiry: int

    def __init__(self, uid, token, expiry):
        self.user_id = uid
        self.user_token = token
        self.expiry = expiry

    def getData(self):
        return self.__dict__


import urllib
import time

class Bestway:
    def __init__(self, baseURL):
        self.baseURL = baseURL

    def isTokenExpired(self, token):
        return time.gmtime(token.expiry) < time.gmtime()

    def getUserToken(self, username, password):
        body = {"username": username, "password": password, "lang": "en"}
        r = self._POST("/app/login")
        return BestwayUserToken(response.uid, r.token, r.expire_at)

    def _POST(self, path, data):
        req = urllib.request.Request(f"{self.baseURL}{path}", headers=HEADERS, data=data)  # POST
        resp = urllib.request.urlopen(req)
        content = resp.read()
        result = json.loads(content)
        return result
