from unittest import TestCase
from bestway.bestway_user_token import BestwayUserToken
from bestway.bestwayapi import BestwayAPI


class TestBestwayAPI(TestCase):
    def test_is_token_expired(self):
        api = BestwayAPI("/")
        token = BestwayUserToken.from_values("uid", "tkn", 99)
        self.assertTrue(api.is_token_expired(token))
        token = BestwayUserToken.from_values("uid", "tkn", 9999999999)
        self.assertFalse(api.is_token_expired(token))
