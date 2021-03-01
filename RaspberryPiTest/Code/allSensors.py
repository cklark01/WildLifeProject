#Imports and global Variables

import Adafruit_DHT

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
gps.send_command(b"PMTK220,1000")
last_print = time.monotonic()

t0 = time.time()
firstTime = True;
# Run program for one hour
while time.time()-t0<3600:
     #Get Time, Battery and Accelerometer Values
     bus = smbus.SMBus(1) 
     now = datetime.datetime.now()
     ax,ay,az= mpu6050_conv()
     with open('AllSensors_data.csv', mode='a') as csv_file:
                fieldnames = ['Date and Time','Temp','Hum','Ax', 'Ay', 'Az','Lat','Long','FixQua','Sate','Alti','Speed','TrAng','HD','HDID','BattPer']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                if firstTime == True:
                    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
                    gps.update()
                    writer.writeheader()
                    writer.writerow({'Date and Time': now.strftime("%Y-%m-%d %H:%M:%S") ,'Temp': str("{0:0.1f}*C".format(temperature)),
                    'Hum': str("{:.1f}%".format(humidity)),'Ax': str(ax), 'Ay': str(ay), 'Az': str(az),
                    'Lat': str("{0:.6f}".format(gps.latitude)),'Long': str("{0:.6f}".format(gps.longitude)),
                    'FixQua': str(gps.fix_quality),'Sate': str(gps.satellites),'Sate': str(gps.satellites),'Alti': str(gps.altitude_m),
                    'Speed': str(gps.speed_knots),'TrAng': str(gps.track_angle_deg),'HD': str(gps.horizontal_dilution),'HDID': str(gps.height_geoid),'BattPer': str("%i%%" % readCapacity(bus))})
                    firstTime = False
                else:
                    if time.time()-t0 % 300 == 0:
                        # Check GPS and Humidity every 5 min = 300 sec
                        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
                        gps.update()
                        writer.writerow({'Date and Time': now.strftime("%Y-%m-%d %H:%M:%S") ,'Temp': str("{0:0.1f}*C".format(temperature)),
                        'Hum': str("{:.1f}%".format(humidity)),'Ax': str(ax), 'Ay': str(ay), 'Az': str(az),
                        'Lat': str("{0:.6f}".format(gps.latitude)),'Long': str("{0:.6f}".format(gps.longitude)),
                        'FixQua': str(gps.fix_quality),'Sate': str(gps.satellites),'Sate': str(gps.satellites),'Alti': str(gps.altitude_m),
                        'Speed': str(gps.speed_knots),'TrAng': str(gps.track_angle_deg),'HD': str(gps.horizontal_dilution),'HDID': str(gps.height_geoid),'BattPer': str("%i%%" % readCapacity(bus))})
                    else:
                        # Check Accelerometer 10 time per second
                        writer.writerow({'Date and Time': now.strftime("%Y-%m-%d %H:%M:%S") ,'Ax': str(ax), 'Ay': str(ay), 'Az': str(az),'BattPer': str("%i%%" % readCapacity(bus))})
    
                    print("Done")
     time.sleep(0.1)