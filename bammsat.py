#! /usr/bin/python
import serial
import time
import struct
serialport = serial.Serial("/dev/ttyS0", 115200, timeout=0.5)

# simulate subsystem
# read telemetry
# simulate power levels
def eps():
    voltage = 5.0
    power = 100    

def send_test_packet():
    packet = b"\x41\x42\x43\x45\x45\x46\x47\x48\x49\x4a\x4b\x4c\x4d\x4e\x4f\x50\x51\x52\x53\x54"
    eps_packet = [122,123,221,231,198,223]
    
    values = [5.1, 100.0, 12.2, 12.3]

    pack = bytearray()
    pack.extend(b'\x01\x30')
    pack.extend(b'\x01\x01')
    for value in values:
        ba = bytearray(struct.pack("f", value)) 
        pack.extend(ba)
    return pack

while(True):
	degrees = 24.3
	pascals = 101035
	hectopascals = pascals / 100
	humidity = 10
	#x = "%3.1f, %3.1f, %3.1f\r\n" % (degrees, hectopascals, humidity)
	x = send_test_packet()
        print(x)
        print (len(x))
	serialport.write(x)
	line = serialport.readline()
	print line
	time.sleep(11);
