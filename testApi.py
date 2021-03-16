import json

from classes import hbApi

configJson = "config.json"
with open(configJson, "r") as f:
    config = json.loads(f.read())

hb = hbApi.hbApi(configJson['host'])
hb.authorize(configJson['username'],configJson['password'])

check = hb.apiRequest("/api/auth/check", "get")