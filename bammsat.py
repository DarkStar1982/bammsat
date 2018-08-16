#! /usr/bin/python
import serial
import time
import struct
import sys
import getopt
from random import random
from Adafruit_BME280 import *

OPTIONS = {
    "hardware_sensors":False
}

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
        packet_types = ['G':0,'A':1,'M':2,'Y':3]
        if OPTIONS["hardware_sensors"]:
            packet = self.get_hardware_packet()
            values = packet["data"]
            values.append(0.0) # last field unused
            type = packet_types[packet_data["type"]]
        else
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

class SubsystemSimulator(object):
    # create serial port connection, and subsystem to run
    # note that serial port connection can be also a simulated one
    def __init__(self, data):
        if data["serialmode"] == "pi2compatible":
            self.serialport = serial.Serial("/dev/ttyAMA0", 115200, timeout=0.5)
        elif data["serialmode"] == "real":
            self.serialport = serial.Serial("/dev/ttyS0", 115200, timeout=0.5)
        elif data["serialmode"] == "virtual":
            self.serialport = SerialPortMockup()
        if data["subsystem"] == "eps":
            self.subsystem = EPS(data)
        if data["subsystem"] == "com":
            self.subsystem = COM(data)
        if data["subsystem"] == "pld":
            self.subsystem = PLD(data)
        if data["subsystem"] == "adc":
            self.subsystem = ADC(data)

    # get outbound data, exchange communications packets
    # process inbound data and move forward the subsystem state
    def simulate(self):
        while(True):
            p_outbound = self.subsystem.get_next_packet()
            if p_outbound is not None:
                self.serialport.write(p_outbound)
            p_inbound = self.serialport.readline()
            self.subsystem.process_inbound_packet(p_inbound)
            self.subsystem.evolve()

    def log_outbound_packet(self, packet):
        print data

    def log_inbound_packet(self, packet):
        print data


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

def display_help():
    print ('General usage:')
    print ('\tbammsat.py -s <subsystem>, where <subsystem>')
    print ('\tcan be one of the following: "eps|com|pld|adc"\n')
    print ("Helpful tips how to use BammSat software-in-the-loop simulator:")
    print ("\t1. Read the code, it is pretty self-explanatory")
    print ("\t2. If -v option is specified, the simulator will not attempt to")
    print ("\t   create an actual serial port connection, using the mock object instead")
    print ("\t3. If -c option is specified, the simulator will use Raspberry Pi 2")
    print ("\t   compatible serial port settings");
    print ("\t3. If -u option is specified, the simulator will attempt to use extra")
    print ("\t   hardware functionality, if available");

def main(argv):
    scenario_data = None
    try:
        opts, args = getopt.getopt(argv,"huvcs:",["help","use_sensors","vse","pi2","system="])
    except getopt.GetoptError:
        print ('bammsat.py --help')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h','--help'):
            display_help()
            sys.exit(0)
        elif opt in ('-s','--system'):
            subsystem = arg
            scenario_data = load_subsystem_scenario(subsystem)
        elif opt in ('-u', '--use_sensors'):
            OPTIONS["hardware_sensors"] = True
        elif opt in ('-v', '--vse'):
            scenario_data["serialmode"]="virtual"
        elif opt in ('-c', '--pi2'):
            scenario_data["serialmode"]="pi2compatible"
    BAMMSatSimulator = SubsystemSimulator(scenario_data)
    BAMMSatSimulator.simulate()

main(sys.argv[1:])
