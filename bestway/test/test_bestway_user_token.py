from unittest import TestCase
from bestway.bestway_user_token import BestwayUserToken

class TestBestwayUserToken(TestCase):
    def test_constructor(self):
        data = {"user_id": "uid", "user_token": "tkn", "expiry": 99}
        token = BestwayUserToken(data)
        self.assertTrue(token.user_id == "uid")
        self.assertTrue(token.user_token == "tkn")
        self.assertTrue(token.expiry == 99)


    def test_from_values(self):
        token = BestwayUserToken.from_values("uid", "tkn", 99)
        self.assertTrue(token.user_id == "uid")
        self.assertTrue(token.user_token == "tkn")
        self.assertTrue(token.expiry == 99)

    def test_get_data(self):
        data = {"user_id": "uid", "user_token": "tkn", "expiry": 99}
        token = BestwayUserToken.from_values("uid", "tkn", 99)
        self.assertTrue(data == token.getData())
