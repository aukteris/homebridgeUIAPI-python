# Command Line Utility for Homebridge UI API

This is a CLI utility which uses the API for Homebridge UI to enable configuration of advanced automation. It allows interation with accessories added to Homebridge UI to enable advanced automation. My specific use cases include Siri Shortcuts which have the "Run Script over SSH" command (including Home automations), or using cron jobs. 

## Usage

The CLI accepts multiple actions. Expected use is to first authorize with credentials against a host to obtain a sessionId. You would then use the sessionId to execute additional actions. 

usage: hbCli.py [-h] {authorize,request,setaccessorychar,accessorycharvalues,listaccessorychars} ...

optional arguments:
  -h, --help            show this help message and exit

actions:
  {authorize,request,setaccessorychar,accessorycharvalues,listaccessorychars}
    authorize           Authorize the API for requests to a particular host
    request             Direct reqeust against the API
    setaccessorychar    Set characteristics of an accessory
    accessorycharvalues
                        Get the current value of a characteristic on an accessory
    listaccessorychars  Get all characteristics from an accessory and their values

### Authorize - Authorize the API for requests to a particular host

usage: hbCli.py authorize [-h] [-H HOST] [-P PORT] [-U USERNAME] [-C PASSWORD] [-F CONFIGFILE]

optional arguments:
  -h, --help            show this help message and exit
  -H HOST, --host HOST  Host for authorization or api request
  -P PORT, --port PORT  Port for authorization
  -U USERNAME, --user USERNAME
                        Usernamne for authorization
  -C PASSWORD, --pass PASSWORD
                        Password for authorization
  -F CONFIGFILE, --config CONFIGFILE
                        Configuration file to be used for request

### Request - Direct reqeust against the API


