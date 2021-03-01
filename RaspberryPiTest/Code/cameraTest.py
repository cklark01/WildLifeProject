import picamera
from time import sleep
import time
import csv
import datetime
import struct
import smbus
import sys
import board

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

print("About to take a video.")
bus = smbus.SMBus(1) 
now = datetime.datetime.now()
with open('Video_BatteryConsumption.csv', mode='a') as csv_file:
    fieldnames = ['Date and Time','BattPer']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow({'Date and Time': now.strftime("%Y-%m-%d %H:%M:%S") ,'BattPer': str("Battery:%i%%" % readCapacity(bus))})
with picamera.PiCamera() as camera:
            camera.resolution= (1280, 720)
            camera.start_recording("/home/pi/Desktop/Test/Camera/testVideo1.h264")
            sleep(3600)
            camera.stop_recording()
print("Video taken")
with open('Video_BatteryConsumption.csv', mode='a') as csv_file:
    fieldnames = ['Date and Time','BattPer']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writerow({'Date and Time': now.strftime("%Y-%m-%d %H:%M:%S") ,'BattPer': str("Battery:%i%%" % readCapacity(bus))})