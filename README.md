# raspi-imgsender
This is a very simple python app that will take a picture from the usb cam connected to the raspi and send it to a url.

# Overview
This app taks pictures using the usb cam and sends them to a url based on a given frequency. It is originally intended to send images to IBM Bluemix (http://bluemix.net). A config.ini file must be located in the same location as the raspi-imgsender.py file.

The app uses the Bluemix IOT Foundation service as a way to provide audio prompting during the pictre taking process.

#  Setup
Follow the instructions defined on http://www.raspberry.org to setup your Raspberry Pi. This project was setup and tested with Raspbian Jessie. 

After the SD card is setup, install these additional python modules...

* Install *Requests* from https://github.com/kennethreitz/requests.git. This is used to make the http requests. Steps...
    * ``git clone https://github.com/kennethreitz/requests.git``
    * ``cd requests``
    * ``sudo python setup.py install``

* Install *requests-toolbelt* from https://pypi.python.org/pypi/requests-toolbelt#downloads. Once downloaded and md5 verified, unzip and install it with these commands:
    * ``tar -zxvf requests-toolbelt-0.6.0.tar.gz``
    * ``cd requests-toolbelt-0.6.0``
    * ``sudo python setup.py install``

* If there is an error for wrong version of six, install six by:
    * ``wget https://pypi.python.org/packages/source/s/six/six-1.9.0.tar.gz#md5=476881ef4012262dfc8adc645ee786c4``
    * ``tar -zxvf six-1.9.0.tar.gz``
    * ``cd six-1.9.0/``
    * ``sudo python setup.py install``

* Modify the config.ini file by setting the values according to your Bluemix service.

The audio prompting is enabled by a flow using Node-Red. Create an app using the Bluemix Node-Red boilerplate, and then bind an instance of the IOT Foundation to the app, restaging when prompted. After the app starts running, import the TalkingPI.flow flow into Node-Red. The Cloudant NoSQL nodes presume that a database named speaker has been created.


# To Use

To use this app, run this command from your Raspberry Pi's console...

```python raspi-imgsender.py```

Watch the output. If there are errors, you will see them. If not, you will see output saying images are taken, uploaded, and the new url.

To stop the app, use ```Ctrl-C```

For audio prompting of the photo process, open the url: http://your-bluemix-nodered-app.mybluemix.net/audio to create a websocket that will receive the speech to text output. 

The dialog includes a name that is spoken after the picture is taken. To update the name that is provided, post using https://your-bluemix-nodered-app.mybluemix.net/demo and enter into the form the name to be spoken and a key (defaults to THIS_APP_KEY) . You can change the APP_KEY by editing the switch node after the http input /demo POST node.



