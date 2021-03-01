import struct
import smbus
import sys
import time
import datetime
import csv

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


time.sleep(1)
t0 = time.time()
flag = False
while time.time()-t0<3600:
     bus = smbus.SMBus(1) 
     now = datetime.datetime.now()
     
     with open('RaspberryPi_data.csv', mode='a') as csv_file:
                fieldnames = ['Date and Time','BattPer']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                if flag == False:
                    writer.writeheader()
                    writer.writerow({'Date and Time': now.strftime("%Y-%m-%d %H:%M:%S") ,'BattPer': str("Battery:%i%%" % readCapacity(bus))})
                    flag = True
                else:
                    writer.writerow({'Date and Time': now.strftime("%Y-%m-%d %H:%M:%S") ,'BattPer': str("Battery:%i%%" % readCapacity(bus))})
                    print("Done")

     time.sleep(300)