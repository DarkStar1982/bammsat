#! /usr/bin/python
import serial
import time
import struct
import sys
import getopt
serialport = serial.Serial("/dev/ttyS0", 115200, timeout=0.5)

class Subsystem(object):
    def __init__(self):
        pass

    def send_outbound_packet(self):
        pass

    def process_inbound_packet(packet_data):
        pass

#simulate communication subsysem
class COM(object):
    def __init__(self):
        pass

    def send_outbound_packet(self):
        return None

    def process_inbound_packet(self, packet_data):
        # decode packet
        print "Received data"
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

# simulate power subsystem
class EPS(Subsystem):
    def __init__(self):
        pass
    
    def send_outbound_packet(self):
        values = [5.1, 4.98, 12.2, 12.3]
        pack = bytearray()
        pack.extend(b'\x01\x01')
        pack.extend(b'\x01\x01')
        for value in values:
            ba = bytearray(struct.pack("f", value)) 
            pack.extend(ba)
        log_outbound_packet(pack)
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
	#log_inbound_packet(packet_data)


def create_subsystem(data):
    subsystem = None
    if data["subsystem"] == "eps":
        subsystem = EPS()
    if data["subsystem"] == "com":
        subsystem = COM()
    return subsystem 

def simulate_subsystem(data):
    subsystem = create_subsystem(data)
    while(True):
        #generate outbound data
	p_outbound = subsystem.send_outbound_packet()
        if p_outbound is not None:	
            #exchange communications packets
            serialport.write(p_outbound)
	p_inbound = serialport.readline()
        
        #process inbound data
        subsystem.process_inbound_packet(p_inbound)
	time.sleep(data["packet_delay"]);

def load_eps_scenario():
    scenario_data = {
        "packet_delay": 11,
        "subsystem": "eps"
    }
    return scenario_data

def load_com_scenario():
    scenario_data = {
        "packet_delay": 11,
        "subsystem": "com"
    }
    return scenario_data

def display_help():
    pass

def log_outbound_packet(data):
    print data

def log_inbound_packet(data):
    print data

def main(argv):
    try:
        opts, args = getopt.getopt(argv,"hec",["help","eps","com"])
    except getopt.GetoptError:
        print ('bammsat.py -help')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h','--help'):
            print ("Help hints go here")
        if opt in ('-e','--eps'):
            scenario_data = load_eps_scenario()
            simulate_subsystem(scenario_data)
        if opt in ('-c', '--com'):
            scenario_data = load_com_scenario()
            simulate_subsystem(scenario_data)

main(sys.argv[1:])
