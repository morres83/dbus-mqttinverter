# dbus-mqttinverter

## Purpose
With the scripts in this repo it should be easy possible to install, uninstall, restart a service that creates a PV inverter based on MQTT data.
Idea is inspired on @fabian-lauer project linked below.



## Inspiration
This project is based on:
- https://github.com/fabian-lauer/dbus-shelly-3em-smartmeter
- https://shelly-api-docs.shelly.cloud/gen1/#shelly1-shelly1pm
- https://github.com/victronenergy/venus/wiki/dbus#pv-inverters
- https://github.com/vikt0rm/dbus-shelly-1pm-pvinverter

### Pictures
![Tile Overview](img/venus-os-tile-overview.PNG)
![Remote Console - Overview](img/venus-os-remote-console-overview.PNG) 
![SmartMeter - Values](img/venus-os-shelly1pm-pvinverter.PNG)
![SmartMeter - Device Details](img/venus-os-shelly1pm-pvinverter-devicedetails.PNG)


## Install & Configuration
### Get the code
Just grap a copy of the main branche and copy them to a folder under `/data/` e.g. `/data/dbus-mqttinverter`.
After that call the install.sh script.

The following script should do everything for you:
```
wget https://github.com/morres83/dbus-mqttinverter/archive/refs/heads/main.zip
unzip main.zip "dbus-mqttinverter/*" -d /data
mv /data/dbus-mqttinverter /data/dbus-mqttinverter
chmod a+x /data/dbus-mqttinverter/install.sh
/data/dbus-mqttinverter/install.sh
rm main.zip
```
⚠️ Check configuration after that - because service is already installed an running and with wrong connection data (host, username, pwd) you will spam the log-file


## Used documentation
- https://github.com/victronenergy/venus/wiki/dbus#pv-inverters   DBus paths for Victron namespace
- https://github.com/victronenergy/venus/wiki/dbus-api   DBus API from Victron
- https://www.victronenergy.com/live/ccgx:root_access   How to get root access on GX device/Venus OS
- https://shelly-api-docs.shelly.cloud/gen1/#shelly1-shelly1pm Shelly API documentation

## Discussions on the web
This module/repository has been posted on the following threads:
- https://community.victronenergy.com/questions/127339/shelly-1pm-as-pv-inverter-in-venusos.html
