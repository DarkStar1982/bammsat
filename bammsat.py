#! /usr/bin/python
import serial
import time
serialport = serial.Serial("/dev/ttyS0", 115200, timeout=0.5)

while(True):
	degrees = 24.3
	pascals = 101035
	hectopascals = pascals / 100
	humidity = 10

	x = "%3.1f, %3.1f, %3.1f\r\n" % (degrees, hectopascals, humidity)
	print (x)
	serialport.write(x)
        line = serialport.readline()
        print line
        time.sleep(11);
