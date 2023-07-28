# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from configuration import Configuration
import datetime
import time
from testbed import testbed

'''
def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

import json
j = json.loads("{}")
print(j)


print("Configuration from dict...")
j = {"action": "print", "method": "onData", "data": "Madan Mohan"}
cfg = Configuration(j)
print (cfg.action, cfg.method, cfg.data)
'''

print("Configuration from file...")
cfg = Configuration.fromFile("configuration.json")
print("username=\"%s\""%(cfg.username))
print(cfg)

print("Store configuration to file")
cfg.datetime = datetime.datetime.now().isoformat()
cfg.toFile("configuration.json")

print("test nonexistent file")
nocfg = Configuration.fromFile("doesnotexist")
print(nocfg)

'''
import urllib.request
with urllib.request.urlopen('http://python.org/') as response:
     html = response.read()
     print(html[:100])

#from urllib import request, parse
data = urllib.parse.urlencode(cfg.getConfiguration()).encode()
req =  urllib.request.Request("https://postman-echo.com/post", data=data) # this will make the method "POST"
resp = urllib.request.urlopen(req)
content = resp.read()
result = json.loads(content)
print(result)

t1 = time.gmtime(1667765155)
print("Token expires:", time.asctime(t1))
if t1 < time.gmtime():
    print("expired")
else:
    print("still valid")
'''

from bestway import Bestway
from bestway_user_token import BestwayUserToken

print("Test token from dict")
token = BestwayUserToken(cfg.token)
print(token)

print("Test dict from token")
d = dict(token)
print(d)

print("Check token validity")
try:
    token = BestwayUserToken(cfg.token)
except:
    token = BestwayUserToken("", "", 0)
print("init Bestway API")
api = Bestway("https://euapi.gizwits.com")
if api.isTokenExpired(token):
    print("Token expired - renewing...")
    token = api.getUserToken(cfg.username, cfg.password)
    print(token)
else:
    print("Token OK - expires", time.asctime(time.gmtime(token.expiry)))

"""
print("Check token passing")
invalid_token = BestwayUserToken({"user_id": "uid", "user_token": "blah", "expiry": 0})
print(f"before: {invalid_token}")
mangler = testbed()
mangler.do_stuff(invalid_token)
print(f"after: {invalid_token}")
"""

print("Store valid token")
cfg.token = dict(token)
cfg.toFile("configuration.json")
