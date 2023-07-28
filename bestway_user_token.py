"""BestwayUserToken - abstraction of security token for Bestway web API"""

# for __repr__
import time

#@dataclass
class BestwayUserToken:
    """User authentication token, obtained (and ideally stored) following a successful login."""

    user_id: str
    user_token: str
    expiry: int

    def __init__(self, uid:str, token:str, expiry:int):
        self.user_id = uid
        self.user_token = token
        self.expiry = expiry

    def __init__(self, d:dict):
        self.user_id = d["user_id"]
        self.user_token = d["user_token"]
        self.expiry = d["expiry"]

    def __iter__(self):
        yield "user_id", self.user_id
        yield "user_token", self.user_token
        yield "expiry", self.expiry

    def __repr__(self):
        return f"{{\n"\
                f"  \"user_id\"=\"{self.user_id}\",\n"\
                f"  \"user_token\"=\"{self.user_token}\",\n"\
                f"  \"expiry\"=\"{time.asctime(time.gmtime(self.expiry))}\"\n"\
               f"}}"

    def getData(self):
        return self.__dict__
