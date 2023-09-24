#!/usr/bin/env python

"""
Changed a lot of a Script originall created by Ralf Zimmermann (mail@ralfzimmermann.de) in 2020.
The orginal code and its documentation can be found on: https://github.com/RalfZim/venus.dbus-fronius-smartmeter
Used https://github.com/victronenergy/velib_python/blob/master/dbusdummyservice.py as basis for this service.
Changed by morres83
"""

"""
/data/Pathtothisscript/vedbus.py
/data/Pathtothisscript/ve_utils.py
pip install paho-mqtt
"""
from gi.repository import GLib
import platform
import logging
import sys
import json
import os
import dbus
from datetime import datetime as dt         # for UTC time stamps for logging
import time    
import paho.mqtt.client as mqtt
try:
  import thread   # for daemon = True  / Python 2.x
except:
  import _thread as thread   # for daemon = True  / Python 3.x

# our own packages
sys.path.append('/opt/victronenergy/dbus-systemcalc-py/ext/velib_python')
from vedbus import VeDbusService #, VeDbusItemImport

path_UpdateIndex = '/UpdateIndex'

# MQTT Setup
broker_address = "localhost"
MQTTNAME = "venusInverterMQTT"
pvInverterMQTTPath = "sun2000/data"

# Variblen setzen
mqttConnected = 0
AcEnergyForward, AcPower = 0, 0
AcL1Current, AcL1EnergyForward, AcL1Power, AcL1Voltage = 0, 0, 0, 0
AcL2Current, AcL2EnergyForward, AcL2Power, AcL2Voltage = 0, 0, 0, 0
AcL3Current, AcL3EnergyForward, AcL3Power, AcL3Voltage = 0, 0, 0, 0
AcMaxPower = 0
ErrorCode = 0
Position, StatusCode = 0, 0
lastMessage = time.time()

# Global dbus object
dbusObj = None

def checkLastMessage():
    if (time.time() - lastMessage > 60):
        #ogging.info(f'{dt.now()} Timeout on MQTT message. Setting failsafe...')
        setFailsafeSettings()
    return True    

def setFailsafeSettings():
    global AcPower
    global AcL1Current, AcL1EnergyForward, AcL1Power, AcL1Voltage
    global AcL2Current, AcL2EnergyForward, AcL2Power, AcL2Voltage
    global AcL3Current, AcL3EnergyForward, AcL3Power, AcL3Voltage
    global AcMaxPower
    AcPower = 0
    AcL1Current, AcL1EnergyForward, AcL1Power, AcL1Voltage = 0, 0, 0, 0
    AcL2Current, AcL2EnergyForward, AcL2Power, AcL2Voltage = 0, 0, 0, 0
    AcL3Current, AcL3EnergyForward, AcL3Power, AcL3Voltage = 0, 0, 0, 0
    AcMaxPower = 0

def on_disconnect(client, userdata, rc):
    global mqttConnected
    print("Client Got Disconnected")
    if rc != 0:
        print('Unexpected MQTT disconnection. Will auto-reconnect')

    else:
        print('rc value:' + str(rc))

    try:
        print("Trying to Reconnect")
        client.connect(broker_address)
        mqttConnected = 1
    except Exception as e:
        logging.exception("Fehler beim reconnecten mit Broker")
        print("Error in Retrying to Connect with Broker")
        mqttConnected = 0
        print(e)

def on_connect(client, userdata, flags, rc):
        global mqttConnected
        if rc == 0:
            print("Connected to MQTT Broker!")
            mqttConnected = 1
            client.subscribe(pvInverterMQTTPath)
        else:
            print("Failed to connect, return code %d\n", rc)

def on_message(client, userdata, msg): #anpassen

    try:
        global AcEnergyForward, AcPower
        global AcL1Current, AcL1EnergyForward, AcL1Power, AcL1Voltage
        global AcL2Current, AcL2EnergyForward, AcL2Power, AcL2Voltage
        global AcL3Current, AcL3EnergyForward, AcL3Power, AcL3Voltage
        global AcMaxPower
        global ErrorCode
        global Position, StatusCode
        global lastMessage
        if msg.topic == pvInverterMQTTPath:   # JSON String vom Broker
            if msg.payload != '{"value": null}' and msg.payload != b'{"value": null}':
                jsonpayload = json.loads(msg.payload)

                AcEnergyForward = float(jsonpayload.get("AcEnergyForward") or 0)
                AcPower = float(jsonpayload.get("AcPower") or 0)

                AcL1Current = float(jsonpayload.get("AcL1Current") or 0)
                AcL1EnergyForward = float(jsonpayload.get("AcL1EnergyForward") or 0)
                AcL1Power = float(jsonpayload.get("AcL1Power") or 0)
                AcL1Voltage = float(jsonpayload.get("AcL1Voltage") or 0)

                AcL2Current = float(jsonpayload.get("AcL2Current") or 0)
                AcL2EnergyForward = float(jsonpayload.get("AcL2EnergyForward") or 0)
                AcL2Power = float(jsonpayload.get("AcL2Power") or 0)
                AcL2Voltage = float(jsonpayload.get("AcL2Voltage") or 0)

                AcL3Current = float(jsonpayload.get("AcL3Current") or 0)
                AcL3EnergyForward = float(jsonpayload.get("AcL3EnergyForward") or 0)
                AcL3Power = float(jsonpayload.get("AcL3Power") or 0)
                AcL3Voltage = float(jsonpayload.get("AcL3Voltage") or 0)
                
                AcMaxPower = float(jsonpayload.get("AcMaxPower") or 0)
                ErrorCode = int(jsonpayload.get("ErrorCode") or 0)
                Position = int(jsonpayload.get("Position") or 0)
                StatusCode = int(jsonpayload.get("StatusCode") or 10)
                if StatusCode == 10: setFailsafeSettings()

                #if (int(jsonpayload.get("InternalFailure")) == 0): internalFailure = 0
                #else: setFailsafeSettings()
                lastMessage = time.time()

                dbusObj._update()
            else:
                print("Answer from MQTT was null and was ignored")
    except KeyError:
        logging.exception("Not all mandatory variables in JSON string")

    except Exception as e:
        logging.exception("Exception in onmessage function")
        print(e)
        print("Exception in onmessage function")


class DbusMQTTInverter(object):
    
    def __init__(self, servicename='com.victronenergy.pvinverter.virtual_mqtt'):
        self._dbusservice = VeDbusService(servicename)
        self._dbusConn = dbus.SessionBus()  if 'DBUS_SESSION_BUS_ADDRESS' in os.environ else dbus.SystemBus()
        
        # Create the mandatory objects
        self._dbusservice.add_mandatory_paths(processname = __file__, processversion = '0.0', connection = 'Virtual',
			deviceinstance = 41, productid = 0, productname = 'SUN2000-6KTL', firmwareversion = 0.1, 
            hardwareversion = '0.0', connected = 1)

        self._dbusservice.add_path('/UpdateIndex', 0)
        self._dbusservice.add_path('/Position', 0)
        self._dbusservice.add_path('/Serial', 0)
        self._dbusservice.add_path('/StatusCode', 0)

        #formatting
        _kwh = lambda p, v: (str(round(v, 2)) + 'kWh')
        _a = lambda p, v: (str(round(v, 1)) + 'A')
        _w = lambda p, v: (str(round(v, 1)) + 'W')
        _v = lambda p, v: (str(round(v, 1)) + 'V')

         # Create AC paths        
        self._dbusservice.add_path('/Ac/Energy/Forward', None, writeable=True, gettextcallback=_kwh)
        self._dbusservice.add_path('/Ac/Power', None, writeable=True, gettextcallback=_w)

        self._dbusservice.add_path('/Ac/L1/Voltage', None, writeable=True, gettextcallback=_v)
        self._dbusservice.add_path('/Ac/L2/Voltage', None, writeable=True, gettextcallback=_v)
        self._dbusservice.add_path('/Ac/L3/Voltage', None, writeable=True, gettextcallback=_v)
        self._dbusservice.add_path('/Ac/L1/Current', None, writeable=True, gettextcallback=_a)
        self._dbusservice.add_path('/Ac/L2/Current', None, writeable=True, gettextcallback=_a)
        self._dbusservice.add_path('/Ac/L3/Current', None, writeable=True, gettextcallback=_a)
        self._dbusservice.add_path('/Ac/L1/Power', None, writeable=True, gettextcallback=_w)
        self._dbusservice.add_path('/Ac/L2/Power', None, writeable=True, gettextcallback=_w)
        self._dbusservice.add_path('/Ac/L3/Power', None, writeable=True, gettextcallback=_w)
        #self._dbusservice.add_path('/Ac/L1/Energy/Forward', None, writeable=True, gettextcallback=_kwh)
        #self._dbusservice.add_path('/Ac/L2/Energy/Forward', None, writeable=True, gettextcallback=_kwh)
        #self._dbusservice.add_path('/Ac/L3/Energy/Forward', None, writeable=True, gettextcallback=_kwh)
        self._dbusservice.add_path('/Ac/MaxPower', None, writeable=True, gettextcallback=_w)

        self._dbusservice.add_path('/ErrorCode', None, writeable=True)

    def _update(self):  

        with self._dbusservice as bus:
            bus["/Ac/Energy/Forward"] = AcEnergyForward
            bus["/Ac/Power"] = AcPower

            bus["/Ac/L1/Current"] = AcL1Current
            #bus["/Ac/L1/Energy/Forward"] = AcL1EnergyForward
            bus["/Ac/L1/Power"] = AcL1Power
            bus["/Ac/L1/Voltage"] = AcL1Voltage
            bus["/Ac/L2/Current"] = AcL2Current
            #bus["/Ac/L2/Energy/Forward"] = AcL2EnergyForward
            bus["/Ac/L2/Power"] = AcL2Power
            bus["/Ac/L2/Voltage"] = AcL2Voltage
            bus["/Ac/L3/Current"] = AcL3Current
            #bus["/Ac/L3/Energy/Forward"] = AcL3EnergyForward
            bus["/Ac/L3/Power"] = AcL3Power
            bus["/Ac/L3/Voltage"] = AcL3Voltage
            
            bus["/Ac/MaxPower"] = AcMaxPower
            bus["/ErrorCode"] = ErrorCode
            bus["/Position"] = Position
            bus["/StatusCode"] = StatusCode

            index = bus[path_UpdateIndex] + 1  # increment index
            if index > 255:   # maximum value of the index
                index = 0       # overflow from 255 to 0
            bus[path_UpdateIndex] = index
            
def main():
    global dbusObj;
    logging.basicConfig(filename = 'dbusmqttinverter.log', level=logging.INFO)

    from dbus.mainloop.glib import DBusGMainLoop
    # Have a mainloop, so we can send/receive asynchronous calls to and from dbus
    DBusGMainLoop(set_as_default=True)
    dbusObj = DbusMQTTInverter()

    logging.info(f'{dt.now()} Connected to dbus')

    # Configuration MQTT
    client = mqtt.Client(MQTTNAME) # create new instance
    client.on_disconnect = on_disconnect
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker_address)  # connect to broker

    client.loop_start()

    GLib.timeout_add_seconds(60, checkLastMessage)

    mainloop = GLib.MainLoop()
    mainloop.run()

if __name__ == "__main__":
    main()