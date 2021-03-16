import requests
import jsonref
import json

class hbApi:
    apiJsonDef = None
    authorization = None

    def __init__(self,host,port=8581):
        self.host = host
        self.port = port
        self.typeMap = {"<class 'str'>":'string',
                        "<class 'int'>":'number',
                        "<class 'bool'>":'boolean'}

        try:
            pathToJson = "http://" + self.host + ":" + str(self.port) +"/swagger/json"
            
            r = requests.get(pathToJson)
            self.apiJsonDef = jsonref.loads(r.text)
            
        except:
            print("Unable to open Homebridge UI API JSON definition")

    def authorize(self,username,password,otp=""):
        self.authorization = self.apiRequest("/api/auth/login","post",requestBody={"username":username,"password":password})
        
        if self.authorization['status_code'] != 201:
            print("Error with authorization: "+ json.dumps(self.authorization['body']))
            

    def apiRequest(self, path, method, requestBody={}, parameters={}):
        headers = {"accept":"*/*"}

        try:
            pathDef = self.apiJsonDef['paths'][path][method]
        except:
            print("Path and method not found")

        try:
            # process paramters
            if 'parameters' in pathDef:
                pass

            # process the body
            if 'requestBody' in pathDef:
                if pathDef['requestBody']['required'] == True and len(requestBody) == 0:
                    raise Exception("requestBody required for endpoint")
                
                for key in pathDef['requestBody']['content'].keys():
                    contentType = key
                
                # add the content type to the header
                headers['Content-Type'] = contentType
                
                schemaDef = pathDef['requestBody']['content'][contentType]['schema']
                
                for i in schemaDef['required']:
                    if i not in requestBody:
                        raise Exception("Missing required property '"+ i +"' in the requestBody")

                for key in requestBody.keys():
                    if key not in schemaDef['properties']:
                        raise Exception("'"+ key +"' is not an accepted property for this method")
                    
                    if self.typeMap[str(type(requestBody[key]))] != schemaDef['properties'][key]['type']:
                        raise Exception("Data type for '" + key + "' property is not correct: '"+ self.typeMap[typeCompare] +"' provided, '" + schemaDef['properties'][key]['type'] +"' expected")

            # process security
            if 'security' in pathDef:
                if self.authorization == None:
                    raise Exception("Not authenticated")

                for i in pathDef['security']:
                    for key in i.keys():
                        if self.authorization['body']['token_type'].lower() == key:
                            headers['Authorization'] = self.authorization['body']['token_type'] + " " + self.authorization['body']['access_token']


        except Exception as inst:
            print(inst)

        except:
            print('Unkown error processing method')

        requestBodyString = json.dumps(requestBody)
        endpoint = "http://" + self.host + ":" + str(self.port) + path
        callout = None
        response = None

        try:
            methods = {"post": requests.post,"get": requests.get, "put": requests.put, "delete":requests.delete}
            callout = methods[method](url=endpoint, data=requestBodyString, headers=headers)
            
            response = {"status_code":callout.status_code,
                        "body":jsonref.loads(callout.text)}

        except Exception as inst:
            print(inst)

        except:
            print("Unknown error with HTTP request")
        
        return response
            
    
        