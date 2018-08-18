#! /usr/bin/python
import serial
import time
import struct
import sys
import getopt
import threading
from random import random
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from Adafruit_BME280 import *

OPTIONS = {
    "hardware_sensors":False,
    "serial_port": None,
    "subsystem": None,
    "http_port":8000,
}

SHARED_DATA = {
    "run_thread":True,
    "command_queue":[] # <-append commands from start
}

# HTTP interface
class GETHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # dump information from the subsystem
        data = OPTIONS["subsystem"].dump_status()
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write("<html><head><title>Title goes here.</title></head>")
        self.wfile.write("<body><p>%s</p>" % data)
        self.wfile.write("</body></html>")
        self.wfile.close()

class SerialPortMockup(object):
    def __init__(self):
        pass

    def write(self, data):
        return None

    def readline(self):
        return "Test packet"

class Subsystem(object):
    def __init__(self):
        pass

    def process_inbound_packet(packet_data):
        pass

    def get_next_packet(self):
        return None

    def evolve(self):
        pass

    def dump_status(self):
        return "I am fine"

# simulate power subsystem
# can be fully passive, self-managed with only health reporting
class EPS(Subsystem):
    def __init__(self, scenario_data):
        self.state = scenario_data["state"]
        self.time_delay = scenario_data["packet_delay"]
        self.counter = 0
        if self.state=="nominal":
            self.voltages = [5.0,3.3,12.0,3.7] # bus voltages, solar panel, battery
            self.sensors = [0.0,0.0,0.0,0.0] # solar panel temperature, EPS & battery temperatures, battery wear
        if OPTIONS["hardware_sensors"]:
            self.sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)
        else:
            self.sensor = None

    def get_next_packet(self):
        # decide what packet to send
        if self.counter % 2 == 0:
            pack = bytearray()
            pack.extend(b'\x01\x01') # packet type 1
            pack.extend(b'\x01\x01')
            for value in self.voltages:
                ba = bytearray(struct.pack("f", value))
                pack.extend(ba)
            return pack
        else:
            pack = bytearray()
            pack.extend(b'\x01\x02') # packet type 2
            pack.extend(b'\x01\x01')
            for value in self.sensors:
                ba = bytearray(struct.pack("f", value))
                pack.extend(ba)
            return pack

    def process_inbound_packet(self, packet_data):
        # decode packet
        unpacked_packet = {}
        packet = bytearray()
        print packet_data
        if len(packet_data)==20:
            packet.extend(packet_data)
            unpacked_packet["subsystem_id"]=packet[0]
            unpacked_packet["type"] = packet[1]
            unpacked_packet["priority"] = packet[2]
            unpacked_packet["reserved"] = packet[3]
            unpacked_packet["data"] = packet[4:20].decode("ascii")
            print unpacked_packet

    def evolve(self):
        # move forward at given time step
        time.sleep(self.time_delay)
        self.counter = self.counter + 1
        if self.state == "nominal":
            # make voltage levels hover slightly above 5.0/12.0v
            offset = 0.2*random()-0.1*random()
            bus_5v = 5.0 + offset
            bus_3v = 3.3 + offset
            solar_12v = 12.0 + offset
            battery_3v = 3.7 + offset
            self.voltages = [bus_5v, bus_3v, solar_12v, battery_3v]
            # evolve the battery cycle, solar panel power etc
            # check counter value - change solar panel voltages
            if OPTIONS["hardware_sensors"]:
                degrees = self.sensor.read_temperature()
                # rest of the values might be not that useful
            	# pascals = self.sensor.read_pressure()
            	# hectopascals = pascals / 100
            	# humidity = sensor.read_humidity()
                self.sensors=[degrees,degrees,degrees,degrees]
        if self.state == "tumbling":
            pass # no stable power
        if self.state == "solar_panel_failure":
            pass
        if self.state == "bus_short":
            pass
        if self.state == "battery_failure":
            pass
        if self.state == "sensor_failure": # take that, OBC!
            pass
        # move forward at given speed

#simulate communication subsysem
class COM(object):
    def __init__(self, scenario_data):
        self.state = scenario_data["state"]
        self.time_delay = scenario_data["packet_delay"]
        self.counter = 0

    def get_next_packet(self):
        values = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
        pack = bytearray()
        pack.extend(b'\x04\x01')
        pack.extend(b'\x01\x01')
        for value in values:
            ba = bytearray(struct.pack("b", value))
            pack.extend(ba)
        return pack

    def process_inbound_packet(self, packet_data):
        # decode packet
        print packet_data
        unpacked_packet = {}
        packet = bytearray()
        if len(packet_data)==20:
            packet.extend(packet_data)
            unpacked_packet["subsystem_id"]=packet[0]
            unpacked_packet["type"] = packet[1]
            unpacked_packet["priority"] = packet[2]
            unpacked_packet["reserved"] = packet[3]
            unpacked_packet["data"] = packet[4:20].decode("ascii")
            print unpacked_packet

    def evolve(self):
        time.sleep(self.time_delay)
        self.counter = self.counter + 1

# simulate payload subsystem
class PLD(Subsystem):
    def __init__(self, scenario_data):
        self.state = scenario_data["state"]
        self.time_delay = scenario_data["packet_delay"]
        self.counter = 0

    def get_next_packet(self):
        values = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,1]
        pack = bytearray()
        pack.extend(b'\x03\x01')
        pack.extend(b'\x01\x01')
        for value in values:
            ba = bytearray(struct.pack("b", value))
            pack.extend(ba)
        return pack

    def process_inbound_packet(self, packet_data):
        # decode packet
        print packet_data
        unpacked_packet = {}
        packet = bytearray()
        if len(packet_data)==20:
            packet.extend(packet_data)
            unpacked_packet["subsystem_id"]=packet[0]
            unpacked_packet["type"] = packet[1]
            unpacked_packet["priority"] = packet[2]
            unpacked_packet["reserved"] = packet[3]
            unpacked_packet["data"] = packet[4:20].decode("ascii")
            print unpacked_packet

    def evolve(self):
        time.sleep(self.time_delay)
        self.counter = self.counter + 1

class ADC(Subsystem):
    def __init__(self, scenario_data):
        self.state = scenario_data["state"]
        self.time_delay = scenario_data["packet_delay"]
        self.counter = 0
        if OPTIONS["hardware_sensors"]:
            # connect to hardware IMU
            #change ACM number as found from ls /dev/tty/ACM
            self.adc_channel=serial.Serial("/dev/ttyACM0",115200)
            self.adc_channel.baudrate=115200

    def get_hardware_packet(self):
        read_ser=self.adc_channel.readline()
        clean = read_ser.replace(' ','').replace('\r\n','')
        parsed = clean[2:].split(',')
        packet_data = {
                "type": read_ser[0],
                "data": [float(x) for x in parsed]}
        return packet_data

    def get_next_packet(self):
        pack = bytearray()
        packet_types = {'G':0,'A':1,'M':2,'Y':3}
        if OPTIONS["hardware_sensors"]:
            packet = self.get_hardware_packet()
            values = packet["data"]
            values.append(0.0) # last field unused
            type = packet_types[packet["type"]]
        else:
            type = self.counter % 4
            values = [0.1,0.1,-0.2,0.0]
        if type == 0:
            # packet type 1 - angular rates in deg/s
            # ax, ay, az - in three axis
            pack.extend(b'\x02\x01')
        if type == 1:
            # packet type 2 - acceleration in g
            # gx, gy, gz - in three axis
            pack.extend(b'\x02\x02')
        if type == 2:
            # packet type 3 - magnetic field strength in gauss
            # mx, my, mz - in three axis
            pack.extend(b'\x02\x03')
        if type == 3:
            # packet type 3 - orientation angles
            # pitch, roll, heading
            pack.extend(b'\x02\x04')
        pack.extend(b'\x01\x01')
        for value in values:
            ba = bytearray(struct.pack("f", value))
            pack.extend(ba)
        return pack

    def process_inbound_packet(self, packet_data):
        # decode packet
        unpacked_packet = {}
        packet = bytearray()
        print packet_data
        if len(packet_data)==20:
            packet.extend(packet_data)
            unpacked_packet["subsystem_id"]=packet[0]
            unpacked_packet["type"] = packet[1]
            unpacked_packet["priority"] = packet[2]
            unpacked_packet["reserved"] = packet[3]
            unpacked_packet["data"] = packet[4:20].decode("ascii")
            print unpacked_packet

    def evolve(self):
        time.sleep(self.time_delay)
        self.counter = self.counter + 1

# should be a file read
def load_subsystem_scenario(p_subsystem):
    if p_subsystem == "eps":
        scenario_data = {
            "packet_delay": 10,
            "subsystem": "eps",
            "state": "nominal",
            "serialmode": "real"
        }
    if p_subsystem == "com":
        scenario_data = {
            "packet_delay": 9,
            "subsystem": "com",
            "state": "nominal",
            "serialmode": "real"
        }
    if p_subsystem == "pld":
        scenario_data = {
            "packet_delay": 12,
            "subsystem": "pld",
            "state": "nominal",
            "serialmode": "real"
        }
    if p_subsystem == "adc":
        scenario_data = {
            "packet_delay": 10,
            "subsystem": "adc",
            "state": "nominal",
            "serialmode": "real"
        }
    return scenario_data

def run_simulation_thread():
    # run simulator
    while(SHARED_DATA["run_thread"]):
        p_outbound = OPTIONS["subsystem"].get_next_packet()
        if p_outbound is not None:
            OPTIONS["serial_port"].write(p_outbound)
        p_inbound = OPTIONS["serial_port"].readline()
        OPTIONS["subsystem"].process_inbound_packet(p_inbound)
        OPTIONS["subsystem"].evolve()

# create serial port connection, and subsystems to run
# (note that serial port connection can be also a simulated one)
# get outbound data, exchange communications packets
# process inbound data and move forward the subsystem state
def simulate(serial_mode, subsystem_mode, http_port, hardware_mode):
    # should be a file path
    data = load_subsystem_scenario(subsystem_mode)

    # set optional hardware and http server options
    OPTIONS["hardware_sensors"] = hardware_mode
    OPTIONS["http_port"] = http_port

    # creare serial port conection
    if serial_mode == "pi2compatible":
        OPTIONS["serial_port"] = serial.Serial("/dev/ttyAMA0", 115200, timeout=0.5)
    if serial_mode == "real":
        OPTIONS["serial_port"] = serial.Serial("/dev/ttyS0", 115200, timeout=0.5)
    if serial_mode == "virtual":
        OPTIONS["serial_port"] = SerialPortMockup()

    # create subsystem...
    if subsystem_mode == 'com':
        OPTIONS["subsystem"] = COM(data)
    if subsystem_mode == "eps":
        OPTIONS["subsystem"] = EPS(data)
    if subsystem_mode == "adc":
        OPTIONS["subsystem"] = ADC(data)
    if subsystem_mode == "pld":
        OPTIONS["subsystem"] = PLD(data)

    # ...and simulate it in a separate thread
    t = threading.Thread(target=run_simulation_thread)
    t.start()

    # create external HTTP interface on a main thread
    instance = ('0.0.0.0', OPTIONS["http_port"])
    http_server = HTTPServer(instance, GETHandler)
    try:
        http_server.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        SHARED_DATA["run_thread"] = False
        print "\r\nExiting all threads, please wait..."
        sys.exit(0)



def display_help():
    print ('General usage:')
    print ('\tbammsat.py -s <subsystem>, where <subsystem>')
    print ('\tcan be one of the following: "eps|com|pld|adc"\n')
    print ("\Read the code, it is pretty self-explanatory")
    print ("Helpful tips how to use BammSat software-in-the-loop simulator:")
    print ("\t1. -p option speficies the http port that COM subsystem will listen on")
    print ("\t2. If -v option is specified, the simulator will not attempt to")
    print ("\t   create an actual serial port connection, using the mock object instead")
    print ("\t3. If -c option is specified, the simulator will use Raspberry Pi 2")
    print ("\t   compatible serial port settings");
    print ("\t4. If -u option is specified, the simulator will attempt to use extra")
    print ("\t   hardware functionality, if available");

def main(argv):
    scenario_data = None
    serial_mode = "real"
    http_port = 8000
    hardware_sensors = False
    try:
        opts, args = getopt.getopt(argv,"huvcp:s:",["help","use_sensors","vse","pi2","port=","system="])
    except getopt.GetoptError:
        print ('bammsat.py --help')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h','--help'):
            display_help()
            sys.exit(0)
        elif opt in ('-s','--system'):
            subsystem = arg
        elif opt in ('-p', '--port'):
            http_port = int(arg)
        elif opt in ('-c', '--pi2'):
            serial_mode="pi2compatible"
        elif opt in ('-v', '--vse'):
            serial_mode="virtual"
        elif opt in ('-u', '--use_sensors'):
            hardware_sensors = True
    simulate(serial_mode, subsystem, http_port, hardware_sensors)

main(sys.argv[1:])
