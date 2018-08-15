#! /usr/bin/python
from Adafruit_BME280 import *
import time
sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)

while(True):
	degrees = sensor.read_temperature()
	pascals = sensor.read_pressure()
	hectopascals = pascals / 100
	humidity = sensor.read_humidity()

	t = "Temperature: %3.2f C" % degrees
	p = "Pressure: %3.2f milliBar" % hectopascals
	h = "Humhumidity: %3.2f%%" % humidity
	print (t)
	print (p)
	print (h)
	time.sleep(11);
