#! /usr/bin/python
import serial
import time
import struct
import sys
import getopt
from random import random


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


class ADC(Subsystem):
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
            self.sensors = [0.0,0.0,0.0,0.0] # solar panel current, temperatures, battery wear

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
        a = sys.stdin.readline()
        # create packet from command input or send the hearbeat packet if no input
        if a == '\n':
            values = [0.0, 0.0, 0.0, 0.0]
            pack = bytearray()
            pack.extend(b'\x04\x01')
            pack.extend(b'\x01\x01')
            for value in values:
                ba = bytearray(struct.pack("f", value))
                pack.extend(ba)
            return pack
        else:
            return None

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
    def __init__(self):
        pass

    def get_next_packet(self):
        values = [5.1, 4.98, 12.2, 12.3]
        pack = bytearray()
        pack.extend(b'\x03\x01')
        pack.extend(b'\x01\x01')
        for value in values:
            ba = bytearray(struct.pack("f", value))
            pack.extend(ba)
        return pack

    def process_inbound_packet(self, packet_data):
        # decode packet
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

class SubsystemSimulator(object):
    # create serial port connection, and subsystem to run
    # note that serial port connection can be also a simulated one
    def __init__(self, data):
        if data["serialmode"] == "real":
            self.serialport = serial.Serial("/dev/ttyS0", 115200, timeout=0.5)
        elif data["serialmode"] == "virtual":
            self.serialport = SerialPortMockup()
        if data["subsystem"] == "eps":
            self.subsystem = EPS(data)
        if data["subsystem"] == "com":
            self.subsystem = COM()
        if data["subsystem"] == "pld":
            self.subsystem = PLD()
        if data["subsystem"] == "adc":
            self.subsystem = ADC()

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
            "serialmode": "real"
        }
    if p_subsystem == "pld":
        scenario_data = {
            "packet_delay": 12,
            "subsystem": "pld",
            "serialmode": "real"
        }
    if p_subsystem == "adc":
        scenario_data = {
            "packet_delay": 10,
            "subsystem": "adc",
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

def main(argv):
    scenario_data = None
    try:
        opts, args = getopt.getopt(argv,"hvs:",["help","vse","system="])
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
        elif opt in ('-v', '--vse'):
            scenario_data["serialmode"]="virtual"
    BAMMSatSimulator = SubsystemSimulator(scenario_data)
    BAMMSatSimulator.simulate()

main(sys.argv[1:])
