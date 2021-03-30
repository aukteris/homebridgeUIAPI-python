from classes import homebridgeUiApi

username = "headless"
password = "yellowPen10"
host = "homebridge.dankurtz.local"
port = 8581

hb = homebridgeUiApi.homebridgeApi(username,password,host=host,port=port)
print(hb.access_token)