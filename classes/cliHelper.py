import os
import json
import random
import string

from ..classes import hbApi

class cliExecutor:
    authStoreDir = '.authStore'
    sessionStoreDir = '.sessionStore'
    hb = None

    def __init__(self):
        if not os.path.exists(self.authStoreDir):
            os.makedirs(self.authStoreDir)
        
        if not os.path.exists(self.sessionStoreDir):
            os.makedirs(self.sessionStoreDir)
    
    # entry point from the main class which calls the actions
    def processArgs(self,args):
        actionMethod = getattr(self, args.action, lambda: "Invalid Action")
        actionMethod(args)
    
    # process autorization request and maintain sessions per user/host
    def authorize(self,args):
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
            
                if not self.checkAuth():
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

                result = {'sessionId':sessionId}

                print(json.dumps(result))
                return result
            
        except Exception as inst:
            print(inst)
        
        except:
            print("Unknown error processing authorization")

    # process a direct API request
    def request(self,args):
        try:
            if not self.loadSession(args.sessionId):
                raise Exception('Session load failed')
            else:
                requestResult = self.hb.apiRequest(args.endpoint,args.method,requestBody=json.loads(args.requestBody),parameters=json.loads(args.parameters))
                
                if not requestResult['status_code'] == 200:
                    raise Exception("HTTP Status " + str(requestResult['status_code']) + " " + requestResult['body']['error'] + ": " + requestResult['body']['message'])
                else:
                    print(json.dumps(requestResult))

        except Exception as inst:
            print(inst)

    # set the characteristics of an accessory
    def setaccessorychar(self,args):
        try:

            #create the characteristic data
            formattedCharVal = int(args.charSet[1]) if args.charSet[1].isnumeric() else args.charSet[1]

            charData = {'characteristicType':args.charSet[0],
                        'value':formattedCharVal}

            if not self.loadSession(args.sessionId):
                raise Exception('Session load failed')
            else:
                findAccessories = self.hb.findAccessoriesByName(args.name)

                if type(findAccessories) is not None:
                    breakout = False

                    for f in findAccessories:
                        for c in f['serviceCharacteristics']:
                            if c['type'] == args.charSet[0]:
                                parameters = {'uniqueId':f['uniqueId']}

                                setResult = self.hb.apiRequest('/api/accessories/{uniqueId}', 'put', requestBody=charData, parameters=parameters)

                                if not setResult['status_code'] == 200:
                                    print("HTTP Status " + str(setResult['status_code']) + " " + setResult['body']['error'] + ": " + setResult['body']['message'])
                                else:
                                    print(json.dumps(setResult))
                                    return setResult

                                breakout = True
                                break

                        if breakout == True:
                            break
                else:
                    raise Exception("No accessories found")

        except Exception as inst:
            print(inst)

    def accessorycharvalues(self,args):
        try:
            if not self.loadSession(args.sessionId):
                raise Exception('Session load failed')
            else:
                findAccessories = self.hb.findAccessoriesByName(args.name)

                results = {}

                if type(findAccessories) is not None:
                    values = []
                    for i in findAccessories:
                        for c in i['serviceCharacteristics']:
                            for x in args.charSet:
                                if x == c['type']:
                                    results[c['type']] = c['value']

                    print(json.dumps(results))
        
        except Exception as inst:
            print(inst)

    def listaccessorychars(self,args):
        try:
            if not self.loadSession(args.sessionId):
                raise Exception('Session load failed')
            else:
                findAccessories = self.hb.findAccessoriesByName(args.name)

                if type(findAccessories) is not None:
                    print("\tCharacteristic\tValue\tRead\tWrite\n")
                    for i in findAccessories:
                        print(i['serviceName'])

                        for c in i['serviceCharacteristics']:
                            print("\t" + c['type'] + "\t" + str(c['value']) + "\t" + str(c['canRead']) + "\t" + str(c['canWrite']))

                else:
                    raise Exception("No accessories found")

        except Exception as inst:
            print(inst)

    # helper method to confirm the authorization is still valid
    def checkAuth(self):
        authCheck = self.hb.apiRequest("/api/auth/check","get")

        if authCheck['status_code'] == 200:
            return True
        else:
            return False
    
    # helper method to load a previous session from a given session ID
    def loadSession(self, sessionId):
        sessionStoreFile = self.sessionStoreDir + '/' + sessionId + '.json'
        
        if not os.path.exists(sessionStoreFile):
            print("Session ID not found")
            return False
        else:
            
            with open(sessionStoreFile, "r") as f:
                sessionData = json.loads(f.read())
            
            self.hb = hbApi.hbApi(sessionData['host'],sessionData['port'])
            self.hb.authorization = sessionData
            
            if self.checkAuth():
                return True
            else:
                print("Authorization is no londer valid")
                return False