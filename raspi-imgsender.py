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
from alchemyapi import AlchemyAPI

#Bluemix IoT related variables
organization = None
deviceType = None
deviceId = None
authMethod = None
authToken = None
apiKey = None

#Image related variables
imgUploadServer = None
PIC_INTERVAL = None
imgResolution = "1280x720" #Image resolution

def setConfigVariables():
    global imgUploadServer, PIC_INTERVAL, organization, deviceType, deviceId, authMetho, authToken, apiKey
    parser = SafeConfigParser()
    parser.read('config.ini')
    PIC_INTERVAL = parser.get('img_config', 'picinterval')
    imgUploadServer = parser.get('img_config','imgstoreurl')

    #load Bluemix config data
    organization = parser.get('bluemix_config','organization')
    deviceType = parser.get('bluemix_config', 'device_type')
    deviceId = parser.get('bluemix_config', 'device_id')
    authMethod = parser.get('bluemix_config', 'auth_method')
    authToken = parser.get('bluemix_config', 'auth_token')
    apiKey = parser.get("bluemix_config', 'api_key')


def imgStoreMonitor_callback(monitor):
    # Do something with this information
    #print 'bytes_read=' + len(monitor)
    pass


def storeImg (filename) :
    #store the image on a web server.
    e = encoder.MultipartEncoder(
        fields={ 'file': (filename, open(filename, 'rb'), 'image/jpeg')}
    )
    m = encoder.MultipartEncoderMonitor(e, imgStoreMonitor_callback)
    reqParams = {'value':filename,'name':filename, 'filename':filename, 'st_filename':filename,'st_deviceid':deviceId}
    contentType = 'image/jpeg'
    contentDisposition = 'form-data'

    #send image as a post.
    r = requests.post(imgUploadServer, data=m, params=reqParams, headers={'Content-Type': m.content_type})
    #r = requests.post(imgUploadServer, params=reqParams, files={'file': ('file', open(filename, 'rb'), contentType, contentDisposition)})
    #r = requests.request('POST', imgUploadServer, data=reqData, files={filename: open(filename, 'rb')})
    if r.status_code != requests.codes.ok :
        print 'there was an error' + str(r.status_code)
        return None
    else :
        jsonData = json.loads(r.text)
        #print jsonData
        newURL = jsonData['attachements'][0]['url']
        #return the url
        #print 'image store results'
        #print newURL
        #the newURL is broken. Need to capture everything after the @
        mySplit = newURL.split("@")
	newURL = "https://" + mySplit[1]

        return newURL



def takePic() :
    global imgResolution
    #create new image name based on date
    filename = time.strftime("%Y%m%d-%H%M%S")
    filename = "img_" + filename + ".jpg"
    #-r option is for setting image resolution.
    os.system("fswebcam -r " + imgResolution + " " + filename)
    return filename



def analyzePic(url) :
    global apiKey
    #r = requests.get("http://ic16-srv-managed.mybluemix.net/imgprocess?img=" + url)
    #print(r)
    #exit()

    alchemyapi = AlchemyAPI()
    #response = alchemyapi.URLGetRankedImageKeywords(url, apikey, 'json', forceShowAll=1, knowledgeGraph=1)
    response = alchemyapi.imageTagging("url", url)

    if response['status'] == 'OK':
        print('## Response Object ##')
        print(json.dumps(response, indent=4))

        print('')
        print('## Keywords ##')
        for keyword in response['imageKeywords']:
            print(keyword['text'], ' : ', keyword['score'])
        print('')
        return response['status']
    else:
        print('Error in image ranked  call: ', response['statusInfo'])    




setConfigVariables()
picInterval = int(PIC_INTERVAL)

# Initialize the device client.
try:
    deviceOptions = {"org": organization,
    "type": deviceType,
    "id": deviceId,
    "auth-method": authMethod,
    "auth-token": authToken}
    deviceCli = ibmiotf.device.Client(deviceOptions)
except Exception as e:
    print("Caught exception connecting device: %s" % str(e))
    sys.exit()

# Connect to send img
deviceCli.connect()

while True:
    filename = takePic()

    publicImgURL = storeImg(filename)

    #Create json data containing img url.
    data = { 'd' : {'imgURL':publicImgURL, 'status':'Image Stored'}}

    def myOnPublishCallback():
        print("Confirmed event %s received by IoTF\n" % data)

    #send data to IoT
    success = deviceCli.publishEvent("status", "json", data, qos=0, on_publish=myOnPublishCallback)

    if not success:
        print("Not connected to IoTF")

    #analysis = analyzePic(publicImgURL)

    #data = { 'd' : {'img_analysis':analysis, 'status':'Img Analyzed'}}
    #success = deviceCli.publishEvent("status", "json", data, qos=0, on_publish=myOnPublishCallback)

    #if not success:
        #print("Not connected to IoTF")

    time.sleep(picInterval)
