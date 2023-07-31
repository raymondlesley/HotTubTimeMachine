from bestway.bestway_user_token import BestwayUserToken

class testbed:
    def do_stuff(self, token:BestwayUserToken):
        token.user_token = "corrupted"
