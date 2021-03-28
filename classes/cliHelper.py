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

        # process a direct API request
        if args.directApiRequest == True:
            try:
                if args.endpoint == None:
                    raise Exception("Endpoint required for API reqest")

                if args.method == None:
                    raise Exception("Method requested for API request")

                if args.sessionId == None:
                    raise Exception ("Session required for an API request")
                
                sessionStoreFile = self.sessionStoreDir + '/' + args.sessionId + '.json'

                if not os.path.exits(sessionStoreFile):
                    raise Exception("Session ID not found")

                else:
                    with open(sessionStoreFile, "r") as f:
                        sessionData = json.loads(f.read())

                    self.hb = hbApi.hbApi(sessionData['host'],sessionData['port'])
                    self.hb.authorization = sessionData

                    checkAuth = self.hb.apiRequest("api/auth/check","get")

                    if not checkAuth['status_code'] == 200:
                        raise Exception('Authorization is no longer valid')
                    else:
                        requestResult = self.hb.apiRequest(args.endpoint,args.method)


            except Exception as inst:
                print(inst)


        # process autorization request and maintain sessions per user/host
        if args.authorizationRequest == True:

            try:
                if args.host == None:
                    raise Exception("Host required for Authorization reqest")

                if not args.port == None:
                    port = args.port
                else:
                    port = 8581
                
                if args.username == None:
                    raise Exception("Username required for Authorization reqest")
                
                if args.password == None:
                    raise Exception("Password required for Authorization reqest")
                
                self.hb = hbApi.hbApi(args.host,port)

                authStoreFile = self.authStoreDir + '/' + args.username + '@' + args.host

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
                        self.hb.authorize(args.username,args.password)
                else:
                    self.hb.authorize(args.username,args.password)

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