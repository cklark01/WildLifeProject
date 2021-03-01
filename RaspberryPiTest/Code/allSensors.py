#Imports and global Variables

import Adafruit_DHT

import picamera
from time import sleep
import time

from mpyLib import *

import board

import datetime
import time
import adafruit_gps
import csv
import serial

import struct
import smbus
import sys

uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=10)
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4

state_charge = (3.622, 3.832, 4.043, 4.182, 4.21)
state_discharge = (4.15, 3.74751, 3.501, 3.35, 2.756)
state_charging = False;
v_current = 0;
v_old = 0;
capacity = 0;



#Battery Methods
def readVoltage(bus):
    
	"This function returns as float the voltage from the Raspi UPS Hat via the provided SMBus object"
	address = 0x36
	read = bus.read_word_data(address, 2)
	swapped = struct.unpack("<H", struct.pack(">H", read))[0]
	voltage = swapped * 78.125 /1000000
	return voltage


def readCapacity(bus):
	"This function returns as a float the remaining capacity of the battery connected to the Raspi UPS Hat via the provided SMBus object"
	address = 0x36
	read = bus.read_word_data(address, 4)
	swapped = struct.unpack("<H", struct.pack(">H", read))[0]
	capacity = swapped/256
	return capacity

# Create a GPS module instance.
gps = adafruit_gps.GPS(uart, debug=False)  


# Turn on the basic GGA and RMC info (what you typically want)
gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
# Turn on just minimum info (RMC only, location):
# gps.send_command(b'PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
# Turn off everything:
# gps.send_command(b'PMTK314,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
# Turn on everything (not all of it is parsed!)
# gps.send_command(b'PMTK314,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0')

# Set update rate to once a second (1hz) which is what you typically want.
gps.send_command(b"PMTK220,1000")
# Or decrease to once every two seconds by doubling the millisecond value.
# Be sure to also increase your UART timeout above!
# gps.send_command(b'PMTK220,2000')
# You can also speed up the rate, but don't go too fast or else you can lose
# data during parsing.  This would be twice a second (2hz, 500ms delay):
# gps.send_command(b'PMTK220,500')

last_print = time.monotonic()
t0 = time.time()
while time.time()-t0<3600:
     bus = smbus.SMBus(1) 
     now = datetime.datetime.now()
     with open('TempAndHum_data.csv', mode='a') as csv_file:
                fieldnames = ['Date and Time','Temp','Hum','BattPer']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                if flag==0:
                    writer.writeheader()
                    flag+=1
                else:
                    writer.writerow({'Date and Time': now.strftime("%Y-%m-%d %H:%M:%S") ,'Temp': str("{0:0.1f}*C".format(temperature)),
                    'Hum': str("Humidity={1:0.1f}%".format(humidity)),'BattPer': str("Battery:%i%%" % readCapacity(bus))})
                    print("Done")
     time.sleep(1)