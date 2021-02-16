
#Imports and global Variables

import Adafruit_DHT

import picamera
from time import sleep
import time

from mpyLib import *

import board


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

#Options for Menu to run every Sensor individualy


##Menu for User
print("Choose an option:")
print("Option 1: Thermometer & Humidity")
print("Option 2: Accelerometer")
print("Option 3: Camera")
print("Option 4: GPS")
print("Option 5: All the sensors")
print("Option 6: Exit")

val = input("Enter a number: ")


while True:
    

    if val == '1':
        #Temperatute and Humidity Sensor

        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

        if humidity is not None and temperature is not None:
                print ("Temp={0:0.1f}*C Humidity={1:0.1f}%".format(temperature, humidity))
        else:
                print("failed to retrieve data from sensor")
    elif val == '2':
        #Accel
        time.sleep(1) # delay necessary to allow mpu9250 to settle
        print("-------------------------------")
        print('recording data')
        
        try:
            ax,ay,az,wx,wy,wz = mpu6050_conv() # read and convert mpu6050 data
            #mx,my,mz = AK8963_conv() # read and convert AK8963 magnetometer data
        except:
            continue

        print('{}'.format('-'*30))
        print('accel [g]: x = {0:2.2f}, y = {1:2.2f}, z {2:2.2f}= '.format(ax,ay,az))
        print('gyro [dps]:  x = {0:2.2f}, y = {1:2.2f}, z = {2:2.2f}'.format(wx,wy,wz))
        #print('mag [uT]:   x = {0:2.2f}, y = {1:2.2f}, z = {2:2.2f}'.format(mx,my,mz))
        print('{}'.format('-'*30))
        print("-------------------------------")
    elif val == '3':
         print("About to take a video.")
         with picamera.PiCamera() as camera:
            res = input("Give the resolution of the video: ")
            res1 = input("Give the of the video: ")
            #1280,720
            camera.resolution= (int(res), int(res1))
            sec = input("How many seconds to record: ")
            camera.start_recording("/home/pi/Desktop/camera/newVideo1.h264")
            sleep(int(sec))
            camera.stop_recording()
         print("Video taken")

    elif val == '4':
        #GPS
        # Make sure to call gps.update() every loop iteration and at least twice
        # as fast as data comes from the GPS unit (usually every second).
        # This returns a bool that's true if it parsed new data (you can ignore it
        # though if you don't care and instead look at the has_fix property).
        gps.update()
        # Every second print out current location details if there's a fix.
        current = time.monotonic()
        if current - last_print >= 1.0:
            last_print = current
            if not gps.has_fix:
                # Try again if we don't have a fix yet.
                print("Waiting for fix...")
                continue
            # We have a fix! (gps.has_fix is true)
            # Print out details about the fix like location, date, etc.
            print("=" * 40)  # Print a separator line.
            print(
                "Fix timestamp: {}/{}/{} {:02}:{:02}:{:02}".format(
                    gps.timestamp_utc.tm_mon,  # Grab parts of the time from the
                    gps.timestamp_utc.tm_mday,  # struct_time object that holds
                    gps.timestamp_utc.tm_year,  # the fix time.  Note you might
                    gps.timestamp_utc.tm_hour,  # not get all data like year, day,
                    gps.timestamp_utc.tm_min,  # month!
                    gps.timestamp_utc.tm_sec,
                )
            )
            print("Latitude: {0:.6f} degrees".format(gps.latitude))
            print("Longitude: {0:.6f} degrees".format(gps.longitude))
            print("Fix quality: {}".format(gps.fix_quality))
            # Some attributes beyond latitude, longitude and timestamp are optional
            # and might not be present.  Check if they're None before trying to use!
            if gps.satellites is not None:
                print("# satellites: {}".format(gps.satellites))
            if gps.altitude_m is not None:
                print("Altitude: {} meters".format(gps.altitude_m))
            if gps.speed_knots is not None:
                print("Speed: {} knots".format(gps.speed_knots))
            if gps.track_angle_deg is not None:
                print("Track angle: {} degrees".format(gps.track_angle_deg))
            if gps.horizontal_dilution is not None:
                print("Horizontal dilution: {}".format(gps.horizontal_dilution))
            if gps.height_geoid is not None:
                print("Height geo ID: {} meters".format(gps.height_geoid))

    elif val == '5':
        # print("About to take a video with resolution 1280,720.\nIt will stop recording when the program ends.")
        # with picamera.PiCamera() as camera:
        #         camera.resolution= (1280, 720)
        #         camera.start_recording("/home/pi/Desktop/camera/newVideo1.h264")  
        #         sleep(6000)
        #         camera.stop_recording()
        #         print("Video taken")

        while True:

            print("-------------------------------")

            humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
            if humidity is not None and temperature is not None:
                print ("Temp={0:0.1f}*C Humidity={1:0.1f}%".format(temperature, humidity))
            else:
                print("failed to retrieve data from sensor")
     
            time.sleep(1) # delay necessary to allow mpu9250 to settle

            try:
                ax,ay,az,wx,wy,wz = mpu6050_conv() # read and convert mpu6050 data
                mx,my,mz = AK8963_conv() # read and convert AK8963 magnetometer data
            except:
                continue

            print('{}'.format('-'*30))
            print('accel [g]: x = {0:2.2f}, y = {1:2.2f}, z {2:2.2f}= '.format(ax,ay,az))
            print('gyro [dps]:  x = {0:2.2f}, y = {1:2.2f}, z = {2:2.2f}'.format(wx,wy,wz))
            print('mag [uT]:   x = {0:2.2f}, y = {1:2.2f}, z = {2:2.2f}'.format(mx,my,mz))
            print('{}'.format('-'*30))


            #Battery Consumption
            bus = smbus.SMBus(1)  # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)

            v_old = readVoltage(bus)
            v_current = v_old

            if (v_current > state_discharge[0]):
                capacity = 100
            elif ((v_current < state_discharge[0]) and (v_current >= state_discharge[1])):
                capacity = (state_discharge[0] - v_current) /((state_discharge[0] - state_discharge[1]) / 33) + 75
            elif ((v_current < state_discharge[1]) and (v_current >= state_discharge[2])):
                capacity = (state_discharge[1] - v_current) / ((state_discharge[1] - state_discharge[2]) / 33) + 50
            elif ((v_current < state_discharge[2]) and (v_current >= state_discharge[3])):
                capacity = (state_discharge[2] - v_current) / ((state_discharge[2] - state_discharge[3]) / 25) + 25
            elif ((v_current < state_discharge[3]) and (v_current >= state_discharge[4])):
                capacity = (state_discharge[3] - v_current) / ((state_discharge[3] - state_discharge[4]) / 25)
            else:
                capacity = 0

            print ("Voltage:%5.2fV" % readVoltage(bus))
            print ("Battery:%5i%%" % capacity)

            
            #GPS
            # Make sure to call gps.update() every loop iteration and at least twice
            # as fast as data comes from the GPS unit (usually every second).
            # This returns a bool that's true if it parsed new data (you can ignore it
            # though if you don't care and instead look at the has_fix property).
            gps.update()
            # Every second print out current location details if there's a fix.
            current = time.monotonic()
            if current - last_print >= 1.0:
                last_print = current
                if not gps.has_fix:
                    # Try again if we don't have a fix yet.
                    print("Waiting for fix...")
                else:
                    # We have a fix! (gps.has_fix is true)
                    # Print out details about the fix like location, date, etc.
                   
                    print(
                        "Fix timestamp: {}/{}/{} {:02}:{:02}:{:02}".format(
                            gps.timestamp_utc.tm_mon,  # Grab parts of the time from the
                            gps.timestamp_utc.tm_mday,  # struct_time object that holds
                            gps.timestamp_utc.tm_year,  # the fix time.  Note you might
                            gps.timestamp_utc.tm_hour,  # not get all data like year, day,
                            gps.timestamp_utc.tm_min,  # month!
                            gps.timestamp_utc.tm_sec,
                        )
                    )
                    print("Latitude: {0:.6f} degrees".format(gps.latitude))
                    print("Longitude: {0:.6f} degrees".format(gps.longitude))
                    print("Fix quality: {}".format(gps.fix_quality))
                    # Some attributes beyond latitude, longitude and timestamp are optional
                    # and might not be present.  Check if they're None before trying to use!
                    if gps.satellites is not None:
                        print("# satellites: {}".format(gps.satellites))
                    if gps.altitude_m is not None:
                        print("Altitude: {} meters".format(gps.altitude_m))
                    if gps.speed_knots is not None:
                        print("Speed: {} knots".format(gps.speed_knots))
                    if gps.track_angle_deg is not None:
                        print("Track angle: {} degrees".format(gps.track_angle_deg))
                    if gps.horizontal_dilution is not None:
                        print("Horizontal dilution: {}".format(gps.horizontal_dilution))
                    if gps.height_geoid is not None:
                        print("Height geo ID: {} meters".format(gps.height_geoid))

            #Write to a csv file all the data from sensors
            flag = 0
            with open('accelerometer_data.csv', mode='a') as csv_file:
                fieldnames = ['Date','Time','Temp','Hum','Ax', 'Ay', 'Az','Gx','Gy','Gz','Mx','My','Mz','Lat','Long','FixQua','Sate','Alti','Speed','TrAng','HD','HDID','BattPer']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                if flag==0:
                    writer.writeheader()
                    flag+=1
                else:
                    writer.writerow({'Date': str("{}/{}/{}".format(gps.timestamp_utc.tm_year,gps.timestamp_utc.tm_mon,gps.timestamp_utc.tm_mday)),'Time': str("{:02}:{:02}:{:02}".format(gps.timestamp_utc.tm_hour,gps.timestamp_utc.tm_min,gps.timestamp_utc.tm_sec)),'Temp': str("{0:0.1f}*C".format(temperature)),
                    'Hum': str("Humidity={1:0.1f}%".format(humidity)),'Ax': str(ax), 'Ay': str(ay), 'Az': str(az),'Gx': str(wx),'Gy': str(wy),'Gz': str(wz),'Mx': str(mx),'My': str(my),'Mz': str(mz),'Lat': str("{0:.6f}".format(gps.latitude)),'Long': str("{0:.6f}".format(gps.longitude)),
                    'FixQua': str(gps.fix_quality),'Sate': str(gps.satellites),'Sate': str(gps.satellites),'Alti': str(gps.altitude_m),'Speed': str(gps.speed_knots),'TrAng': str(gps.track_angle_deg),'HD': str(gps.horizontal_dilution),'HDID': str(gps.height_geoid),'BattPer': str("Battery:%5i%%" % capacity)})

            

            print()
            temp = input("Do you want to continue? ")
            print()
            if temp != "yes":
                exit(0)

            
    elif val == '6':
        exit(0)

    
    val = input("Enter a number: ")

    sleep(1)