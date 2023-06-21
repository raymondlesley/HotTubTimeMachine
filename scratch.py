# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


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


from configuration import Configuration

print("Configuration from dict...")
j = {"action": "print", "method": "onData", "data": "Madan Mohan"}
cfg = Configuration(j)
print (cfg.action, cfg.method, cfg.data)

print("... and from file...")
cfg = Configuration.fromFile("configuration.json")
print("username=\"%s\""%(cfg.username))

cfg.password = "*"
cfg.toFile("configuration.json")

print("test nonexistent file")
nocfg = Configuration.fromFile("doesnotexist")
print(nocfg.getConfiguration())

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

import time
t1 = time.gmtime(1667765155)
print(time.asctime(t1))
if t1 < time.gmtime():
    print("expired")
else:
    print("still valid")

from bestway import Bestway, BestwayUserToken
token = BestwayUserToken("", "", 0)
api = Bestway("https://")
if api.isTokenExpired(token):
    print("Token expired - need to renew")
else:
    print("Token OK")

cfg.token = token.getData()
cfg.toFile("configuration.json")
