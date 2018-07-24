#! /usr/bin/python
import serial
import time
import struct
serialport = serial.Serial("/dev/ttyS0", 115200, timeout=0.5)

class Subsystem(object):
    def __init__(self):
        pass

    def send_outbound_packet(self):
        pass

    def process_inbound_packet(packet_data):
        pass

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
	packet = bytearray()
	packet.extend(packet_data)
	for item in packet:
		print str(item)
	#log_inbound_packet(packet_data)


def create_subsystem(data):
    subsystem = None
    if data["subsystem"] == "eps":
        subsystem = EPS()
    return subsystem 

def simulate_subsystem(data):
    subsystem = create_subsystem(data)
    while(True):
        #generate outbound data
	p_outbound = subsystem.send_outbound_packet()
	
        #exchange communications packets
        serialport.write(p_outbound)
	p_inbound = serialport.readline()
        
        #process inbound data
        subsystem.process_inbound_packet(p_inbound)
	time.sleep(data["packet_delay"]);

def load_scenario():
    scenario_data = {
        "packet_delay": 11,
        "subsystem": "eps"
    }
    return scenario_data

def display_help():
    pass


def log_outbound_packet(data):
    print data

def log_inbound_packet(data):
    print data

def main():
    scenario_data = load_scenario()
    simulate_subsystem(scenario_data)

main()
