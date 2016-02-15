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
#IOT#import ic16_demo_iot as iot

#Image related variables
deviceId = None
imgUploadServer = None
PIC_INTERVAL = None
imgResolution = "1280x720" #Image resolution

def setConfigVariables():
    global imgUploadServer, PIC_INTERVAL
    parser = SafeConfigParser()
    parser.read('config.ini')
    PIC_INTERVAL = parser.get('img_config', 'picinterval')
    imgUploadServer = parser.get('img_config','imgstoreurl')
    deviceId = parser.get('img_config','deviceid')


def imgStoreMonitor_callback(monitor):
    # Do something with this information
    #print 'bytes_read=' + len(monitor)
    pass


def storeImg (filename) :
    #store the image on a web server.
    global deviceId, imgUploadServer
    e = encoder.MultipartEncoder(
        fields={ 'file': (filename, open(filename, 'rb'), 'image/jpeg')}
    )
    m = encoder.MultipartEncoderMonitor(e, imgStoreMonitor_callback)
    reqParams = {'value':filename,'name':filename, 'filename':filename, 'st_filename':filename,'st_deviceid':deviceId}
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


setConfigVariables()
picInterval = int(PIC_INTERVAL)

# Initialize the device client for Bluemix IoT
#IOT#iot.setupIOTConnection()

# Connect to Bluemix IoT
#IOT#iot.connectIOT()

#repeat until app is stopped (Ctrl-C)
while True:
    filename = takePic()

    publicImgURL = storeImg(filename)

    #IOT#If using IOT, format the data and send.
    #Create json data containing img url.
    #IOT#data = { 'd' : {'imgURL':publicImgURL, 'status':'Image Stored'}}
    #send data to IBM Bluemix IOT
    #IOT#iot.notifyIOT(data)

    time.sleep(picInterval)

