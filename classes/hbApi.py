import requests
import jsonref
import json

class hbApi:
    apiJsonDef = None
    authorization = None

    def __init__(self,host,port=8581,secure=False):
        self.host = host
        self.port = port
        self.secure = secure
        self.typeMap = {"<class 'str'>":'string',
                        "<class 'int'>":'number',
                        "<class 'bool'>":'boolean'}

        try:
            # pathToJson = "http://" + self.host + ":" + str(self.port) +"/swagger/json"
            #r = requests.get(pathToJson)
            #self.apiJsonDef = jsonref.loads(r.text)
            
            with open("swagger.json", "r") as f:
                swaggerDef = json.loads(f.read())

            self.apiJsonDef = swaggerDef['swaggerDoc']
            
        except:
            print("Unable to open Homebridge UI API JSON definition")

    # apiRequest method to handle and validate all requests to an endpoint
    def apiRequest(self, path, method, requestBody={}, parameters={}):
        headers = {"accept":"*/*"}

        try:
            pathDef = self.apiJsonDef['paths'][path][method]
        except:
            print("Path and method not found")

        try:
            # process paramters
            if 'parameters' in pathDef:
                if len(pathDef['parameters']) > 0 and len(parameters) == 0:
                    raise Exception("Parameters are required for endpoint")

                for i in pathDef['parameters']:
                    for key in parameters.keys():
                        if i['name'] == key:
                            path = path.replace("{"+key+"}",parameters[key])
                
                if path.find("{") != -1:
                    raise Exception("Problem processing parameters")

            # process the body
            if 'requestBody' in pathDef:
                if pathDef['requestBody']['required'] == True and len(requestBody) == 0:
                    raise Exception("requestBody required for endpoint")
                
                for key in pathDef['requestBody']['content'].keys():
                    contentType = key
                
                # add the content type to the header
                headers['Content-Type'] = contentType
                
                schemaDef = pathDef['requestBody']['content'][contentType]['schema']
                
                #for i in schemaDef['required']:
                #    if i not in requestBody:
                #        raise Exception("Missing required property '"+ i +"' in the requestBody")

                #for key in requestBody.keys():
                #    if key not in schemaDef['properties']:
                #        raise Exception("'"+ key +"' is not an accepted property for this method")
                    
                    #turns out the schemaDef is not reliable for the required type
                    #if self.typeMap[str(type(requestBody[key]))] != schemaDef['properties'][key]['type']:
                        #raise Exception("Data type for '" + key + "' property is not correct: '"+ self.typeMap[str(type(requestBody[key]))] +"' provided, '" + schemaDef['properties'][key]['type'] +"' expected")

            # process security
            if 'security' in pathDef:
                if self.authorization == None:
                    raise Exception("Not authenticated")

                for i in pathDef['security']:
                    for key in i.keys():
                        if self.authorization['body']['token_type'].lower() == key:
                            headers['Authorization'] = self.authorization['body']['token_type'] + " " + self.authorization['body']['access_token']

        except Exception as inst:
            print(str(inst))

        except:
            print('Unkown error processing method')

        # compile all the details and then make the callout
        requestBodyString = json.dumps(requestBody)
        protocol = "https://"
        if (self.secure == False) protocol = "http://"
        endpoint = protocol + self.host + ":" + str(self.port) + path
        callout = None
        response = None

        try:
            methods = {"post": requests.post,"get": requests.get, "put": requests.put, "delete":requests.delete}
            callout = methods[method](url=endpoint, data=requestBodyString, headers=headers)
            
            response = {"status_code":callout.status_code,
                        "host":self.host,
                        "port":self.port,
                        "body":json.loads(callout.text)}

        except Exception as inst:
            print(inst)

        except:
            print("Unknown error with HTTP request")
        
        return response
    
    # authorization
    def authorize(self,username,password,otp=""):
        self.authorization = self.apiRequest("/api/auth/login","post",requestBody={"username":username,"password":password})
        
        if self.authorization['status_code'] != 201:
            print("Error with authorization: "+ json.dumps(self.authorization['body']))

    #helper method to find uniqueId for an accessory based on the serviceName
    def findAccessoriesByName(self, name):
        try: 
            accessoryQuery = self.apiRequest("/api/accessories","get")

            if accessoryQuery['status_code'] != 200:
                message = "Callout error trying to find accessory:"+ json.dumps(accessory['body'])
                raise Exception(message)
            
            else:
                results = []

                for i in accessoryQuery['body']:
                    if i['serviceName'] == name:
                        results.append(i)
                
                if len(results) > 0:
                    return results

        except Exception as inst:
            print(inst)

        except:
            print("Unkown error trying to find accessory")
    
        