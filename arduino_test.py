#!/usr/bin/python

import serial
import time
ser=serial.Serial("/dev/ttyACM0",115200)  #change ACM number as found from ls /dev/tty/ACM
ser.baudrate=115200

packet_titles = {
        "G": "Angular rate packet", 
        "A": "Accelerometer packet", 
        "M": "Magnetometer packet",
        "Y": "Pitch, roll, heading packet"
        }

def read_adc():
    read_ser=ser.readline()
    print packet_titles[read_ser[0]]
    clean = read_ser.replace(' ','').replace('\r\n','')
    parsed = clean[2:].split(',')
    packet_data = {
            "type": read_ser[0],
            "data": [float(x) for x in parsed]}
    return packet_data

def main():
    while True:
        print read_adc()

main()
