# OctoPrint-OctoPlug

OctoPlug is a plugin for OctoPrint, which switches on an Edimax SmartPlug at a certain layer while printing. It also stops it when the printer finished printing.

I use this to trigger my additional active cooling fan, which is not directly connected to the board of my printer (mightyboard in my case). Like that, I do not need to make any modifications to my printer but still have an automatic active cooling.

This plugin has only been testet with the Edimax SP1101W SmartPlug 
(http://www.edimax.com/edimax/merchandise/merchandise_detail/data/edimax/au/home_automation_smart_plug/sp-1101w/)

I currently do not own one of the newer generations, so I cannot test them.

#Credits
This Plugin uses a slightly edited version of the Ediplug-py Project by wendlers.

You can find his repository right here: https://github.com/wendlers/ediplug-py

# Installing
Open a browser to octoprint (http://ipaddress/) and login

Choose "Settings" from the top bar

Click "Plugin Manager" on the left side

Click the "Get More..." button

Find OctoPlug in the list and click "Install" or enter this GitUrl to "... from URL"

Restart octoprint

Refresh your browser

# Settings
After installing OctoPlug, you will have to set some settings that match your Edimax Plug.
You have to find out which IP Adress it is using in your local network.
I just opened my FritzBox Webinterface, which shows all connected devices.

The default Port is 10000, however you can change it if you want to forward it on a different port outside of your LAN.
The default user is "admin" and the default password should be "1234". You can find it on the back of your Edimax.
Finally hit save. Open up settings again and press "Test Configuration". If you did everything right, the plug should turn on for 3 seconds and turn off again.

#Features
The Plugin also hooks to the GCode command M106 and M106 S0, which are the button "Fan on" and "Fan off" in your printers control tab. 
