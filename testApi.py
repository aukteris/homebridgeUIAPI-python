import json

from classes import hbApi

configJson = "config.json"
with open(configJson, "r") as f:
    config = json.loads(f.read())

hb = hbApi.hbApi(config['host'])
hb.authorize(config['username'],config['password'])

accessoryResult = hb.findAccessories("Jonahs Room Light")
jonahsLight = accessoryResult[0]

print(json.dumps(jonahsLight))