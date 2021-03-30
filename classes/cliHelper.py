import os
import json
import random
import string

from classes import hbApi

class cliExecutor:
    authStoreDir = '.authStore'
    sessionStoreDir = '.sessionStore'
    hb = None

    def __init__(self):
        if not os.path.exists(self.authStoreDir):
            os.makedirs(self.authStoreDir)
        
        if not os.path.exists(self.sessionStoreDir):
            os.makedirs(self.sessionStoreDir)
        
    def processArgs(self,args):

        # process autorization request and maintain sessions per user/host
        if args.authorizationRequest == True:

            try:
                if args.configFile == None:
                    config = {}
                    config['host'] = args.host
                    config['port'] = args.port
                    config['username'] = args.username
                    config['password'] = args.password
                else:
                    with open(args.configFile, "r") as f:
                        config = json.loads(f.read())


                
                if config['host'] == None:
                    raise Exception("Host required for Authorization reqest")

                if not config['port'] == None:
                    port = config['port']
                else:
                    port = 8581
                
                if config['username'] == None:
                    raise Exception("Username required for Authorization reqest")
                
                if config['password'] == None:
                    raise Exception("Password required for Authorization reqest")
                
                self.hb = hbApi.hbApi(config['host'],port)

                authStoreFile = self.authStoreDir + '/' + config['username'] + '@' + config['host']

                #check if we have authorization already
                if os.path.exists(authStoreFile):
                    with open(authStoreFile) as f:
                        sessionId = f.read()
                else:
                    sessionIdCharacters = string.digits + "-" + string.ascii_lowercase
                    sessionId = ''.join(random.choice(sessionIdCharacters) for i in range(20))

                sessionStoreFile = self.sessionStoreDir + '/' + sessionId + '.json'

                # check for the previous session for this host/user
                if os.path.exists(sessionStoreFile):
                    with open(sessionStoreFile) as f:
                        self.hb.authorization = json.loads(f.read())
                
                    checkAuth = self.hb.apiRequest("/api/auth/check","get")
                    if not checkAuth['status_code'] == 200:
                        self.hb.authorize(config['username'],config['password'])
                else:
                    self.hb.authorize(config['username'],config['password'])

                if not self.hb.authorization['status_code'] == 201:
                    raise Exception('Authorization failure')
                else: 
                    
                    sessionStoreFile = self.sessionStoreDir + '/' + sessionId + '.json'

                    f = open(authStoreFile, "w")
                    f.write(sessionId)
                    f.close()

                    f = open(sessionStoreFile, "w")
                    f.write(json.dumps(self.hb.authorization))
                    f.close()

                    print(sessionId)
            
                
            except Exception as inst:
                print(inst)
        
         # process a direct API request
        if args.directApiRequest == True:
            try:
                if args.endpoint == None:
                    raise Exception("Endpoint required for API reqest")

                if args.method == None:
                    raise Exception("Method requested for API request")

                if args.sessionId == None:
                    raise Exception("Session required for an API request")
                
                sessionStoreFile = self.sessionStoreDir + '/' + args.sessionId + '.json'
                
                if not os.path.exists(sessionStoreFile):
                    raise Exception("Session ID not found")

                else:
                    with open(sessionStoreFile, "r") as f:
                        sessionData = json.loads(f.read())
                    

                    self.hb = hbApi.hbApi(sessionData['host'],sessionData['port'])
                    self.hb.authorization = sessionData

                    checkAuth = self.hb.apiRequest("/api/auth/check","get")

                    if not checkAuth['status_code'] == 200:
                        raise Exception('Authorization is no longer valid')
                    else:
                        requestResult = self.hb.apiRequest(args.endpoint,args.method,requestBody=json.loads(args.requestBody),parameters=json.loads(args.parameters))
                        print(json.dumps(requestResult))

            except Exception as inst:
                print(inst)
        
        if args.setAccessoryCharacteristics == True:
            try:
                if args.name == None:
                    raise Exception("Accessory name required to set characteristics")
                
                if args.charSet == None:
                    raise Exception("Characteristics and values required to set characteristics")
                
                if args.sessionId == None:
                    raise Exception ("Session required to set characteristics")

                #create the characteristic data
                charData = {'characteristicType':args.charSet[0],
                            'value':args.charSet[1]}

                sessionStoreFile = self.sessionStoreDir + '/' + args.sessionId + '.json'
                
                if not os.path.exists(sessionStoreFile):
                    raise Exception("Session ID not found")

                else:
                    with open(sessionStoreFile, "r") as f:
                        sessionData = json.loads(f.read())

                    self.hb = hbApi.hbApi(sessionData['host'],sessionData['port'])
                    self.hb.authorization = sessionData

                    checkAuth = self.hb.apiRequest("/api/auth/check","get")

                    if not checkAuth['status_code'] == 200:
                        raise Exception('Authorization is no longer valid')
                    else:
                        findAccessories = self.hb.findAccessories(args.name)

                        if type(findAccessories) is not None and len(findAccessories) > 0:
                            parameters = {'uniqueId':findAccessories[0]['uniqueId']}

                            setResult = self.hb.apiRequest('/api/accessories/{uniqueId}', 'put', requestBody=charData, parameters=parameters)

                            if not setResult['status_code'] == 200:
                                print("HTTP Status " + str(setResult['status_code']) + " " + setResult['body']['error'] + ": " + setResult['body']['message'])
                            else:
                                print(setResult['status_code'])

            except Exception as inst:
                print(inst)