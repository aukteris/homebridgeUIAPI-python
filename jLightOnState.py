import requests
import json
import sys

from classes import homebridgeUiApi

command = int(sys.argv[1])

config = None

configJson = "config.json"
with open(configJson, "r") as f:
    config = json.loads(f.read())

hb = homebridgeUiApi.homebridgeApi(config['username'],config['password'],domain=config['host'],port=config['port'])
hb.setAccessory(config['accessoryId'], "Brightness", command*100)
