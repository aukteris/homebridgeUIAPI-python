import requests
import json
import sys

command = int(sys.argv[1])

domain = "XXXXXX"
port = 8581
username = "XXXXXX"
password = "XXXXXX"

accessoryId = "XXXXXX"

class homebridgeApi:
    tokenFile = "token.txt"

    def __init__(self,username,password,domain="minihome.dankurtz.local",port=8581):
        self.username = username
        self.password = password
        self.domain = domain
        self.port = port
        self.baseUrl = "http://" + self.domain + ":" + str(self.port)

        try:
            openFile = open(self.tokenFile, "r")
            self.access_token = openFile.readline()
        except:
            self.access_token = "blank"

        tokenCheck = self.checkToken()

        if tokenCheck != 200:
            self.getAccessToken()
        

    # login to api to get bearer access token
    def getAccessToken(self):
        endpoint = self.baseUrl + "/api/auth/login"
        data = {'username':self.username,
                'password':self.password}

        r = requests.post(url=endpoint, data=data)
        response = json.loads(r.text)

        self.access_token = response['token_type'] + " " + response['access_token']

        write = open(self.tokenFile, "w")
        write.write(self.access_token)
        write.close()

    # check if current access token is valid
    def checkToken(self):

        endpoint = self.baseUrl + "/api/auth/check"
        headers = {'Authorization':self.access_token}

        r = requests.get(endpoint, headers=headers)

        return r.status_code

    def setAccessory(self, uniqueId, char, value):

        endpoint = self.baseUrl + "/api/accessories/" + uniqueId
        data = {'characteristicType':char,
                'value':value}
        headers = {'Authorization':self.access_token}
        print(data)
        print(headers)
        #r = requests.put(endpoint, data, headers=headers)


hb = homebridgeApi(username,password,domain=domain,port=port)
hb.setAccessory(accessoryId, "Brightness", command*100)
