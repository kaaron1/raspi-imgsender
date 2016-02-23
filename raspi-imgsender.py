import os
import datetime
import time
from ConfigParser import SafeConfigParser
import sys
import uuid
import ibmiotf.device
import requests
import json
from requests_toolbelt.multipart import encoder

#Image related variables
deviceId = None
imgUploadServer = None
PIC_INTERVAL = None
imgResolution = "1280x720" #Image resolution
app_key = None

#Bluemix IoT related variables
organization = None
deviceType = None
deviceId = None
authMethod = None
authToken = None
apiKey = None

iot = None

def setConfigVariables():
    global imgUploadServer, PIC_INTERVAL, app_key, organization, deviceType, deviceId, authMethod, authToken, apiKey
    parser = SafeConfigParser()
    parser.read('config.ini')
    PIC_INTERVAL = parser.get('img_config', 'picinterval')
    imgUploadServer = parser.get('img_config','imgstoreurl')
    deviceId = parser.get('img_config','deviceid')
    app_key = parser.get('img_config', 'app_key')
	
	#load Bluemix config data
    organization = parser.get('bluemix_config','organization')
    deviceType = parser.get('bluemix_config', 'device_type')
    deviceId = parser.get('bluemix_config', 'device_id')
    authMethod = parser.get('bluemix_config', 'auth_method')
    authToken = parser.get('bluemix_config', 'auth_token')
    apiKey = parser.get('bluemix_config', 'api_key')


def imgStoreMonitor_callback(monitor):
    # Do something with this information
    #print 'bytes_read=' + len(monitor)
    pass


def storeImg (filename) :
    #store the image on a web server.
    global deviceId, imgUploadServer, app_key
    e = encoder.MultipartEncoder(
        fields={ 'file': (filename, open(filename, 'rb'), 'image/jpeg')}
    )
    m = encoder.MultipartEncoderMonitor(e, imgStoreMonitor_callback)
    reqParams = {'value':filename,'name':filename, 'filename':filename, 'st_filename':filename,'st_deviceid':deviceId, 'app_key':app_key}
    contentType = 'image/jpeg'
    contentDisposition = 'form-data'

    #send image as a post.
    r = requests.post(imgUploadServer, data=m, params=reqParams, headers={'Content-Type': m.content_type})
    if r.status_code != requests.codes.ok :
        print 'there was an error' + str(r.status_code)
        return None
    else :
        jsonData = json.loads(r.text)
        newURL = jsonData['attachment']['url']
        print 'Image sent. returned URL=' + newURL
        return newURL



def takePic() :
    global imgResolution
    #create new image name based on date
    filename = time.strftime("%Y%m%d-%H%M%S")
    filename = "img_" + filename + ".jpg"
    #-r option is for setting image resolution.
    os.system("fswebcam -r " + imgResolution + " " + filename)
    return filename

def myCommandCallback(cmd):
    print("Command received: %s" % cmd.data)
    if cmd.command == "takePicture":
      processPicture()

def processPicture():
    global iot
    #If using IOT, announce picture about to be taken
    data = { 'd' : {'status':'executing take picture cmd'}}
    #send data to IBM Bluemix IOT
    notifyIOT(data)

    # Wait for countdown
    time.sleep(5)

    filename = takePic()

    publicImgURL = storeImg(filename)

    #If using IOT, announce picture taken and analyzing
    data = { 'd' : {'status':'Pic taken and sent for analysis'}}
    #send data to IBM Bluemix IOT
    notifyIOT(data)



######### IoT Methods
def setupIOTConnection () :
    #get access to the global variables.
    global iot, organization, deviceType, deviceId, authMethod, authToken, apiKey
    
    # Initialize the device client for Bluemix IoT
    try:
        deviceOptions = {"org": organization,
        "type": deviceType,
        "id": deviceId,
        "auth-method": authMethod,
        "auth-token": authToken}
        iot = ibmiotf.device.Client(deviceOptions)
    except Exception as e:
        print("Caught exception connecting device: %s" % str(e))
        sys.exit()


def connectIOT():
    global iot
    # Connect to Bluemix IoT
    iot.connect()

def notifyIOT(data) :
    global iot
	
    def myOnPublishCallback() :
        print("Confirmed event %s received by IoTF\n" % data)

    #send data to IoT
    success = iot.publishEvent("status", "json", data, qos=0, on_publish=myOnPublishCallback)

    if not success:
        print("Not connected to IoTF")


setConfigVariables()
picInterval = int(PIC_INTERVAL)

# Initialize the device client for Bluemix IoT
setupIOTConnection()

# Connect to Bluemix IoT
connectIOT()

# Set callback for commands. This will pick up any commands that are sent to this device.
iot.commandCallback = myCommandCallback

#repeat until app is stopped (Ctrl-C)
while True:
    data = { 'd' : { 'status': 'Waiting for command'} }
    notifyIOT( data)
    time.sleep(10)

	
# Disconnect the device.
iot.disconnect()	
