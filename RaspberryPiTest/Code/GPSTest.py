import adafruit_gps

import serial


import time
import csv
import datetime
import struct
import smbus
import sys

import board



uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=10)
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

flag = 0

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




# Every second print out current location details if there's a fix.





time.sleep(1)
while time.time()-t0<3600:
     bus = smbus.SMBus(1) 
     now = datetime.datetime.now()
     gps.update()
     with open('GPS_data.csv', mode='a') as csv_file:
                fieldnames = ['Date and Time','Lat','Long','FixQua','Sate','Alti','Speed','TrAng','HD','HDID','BattPer']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                if flag==0:
                    writer.writeheader()
                    flag+=1
                else:
                    writer.writerow({'Date and Time': now.strftime("%Y-%m-%d %H:%M:%S") ,'Lat': str("{0:.6f}".format(gps.latitude)),'Long': str("{0:.6f}".format(gps.longitude)),
                    'FixQua': str(gps.fix_quality),'Sate': str(gps.satellites),'Sate': str(gps.satellites),'Alti': str(gps.altitude_m),'Speed': str(gps.speed_knots),'TrAng': str(gps.track_angle_deg),'HD': str(gps.horizontal_dilution),'HDID': str(gps.height_geoid),'BattPer': str("Battery:%i%%" % readCapacity(bus))})
                    print("Done")

     time.sleep(300)









