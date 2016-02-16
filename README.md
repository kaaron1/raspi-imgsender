# raspi-imgsender
This is a very simple python app that will take a picture from the usb cam connected to the raspi and send it to a url.

# Overview
This app taks pictures using the usb cam and sends them to a url based on a given frequency. It is originally intended to send images to IBM Bluemix (http://bluemix.net). A config.ini file must be located in the same location as the raspi-imgsender.py file.

Note: Code is included to use Bluemix IOT Foundation. However, this is commented out by default. See To Use step #3 for details to use this feature.

# To Use
To use this app, follow these steps...
1. Modify the config.ini file.
2. Ensure you have the dependencies installed.
3. If you also want this pi to register with an IOT Foundation instance, uncomment each *#IOT#* marker. This will uncomment the needed code to pull in the iot calls.  
4. Start the program by running ```python raspi-imgsender.py.```



