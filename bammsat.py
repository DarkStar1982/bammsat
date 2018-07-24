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
        packet = b"\x41\x42\x43\x45\x45\x46\x47\x48\x49\x4a\x4b\x4c\x4d\x4e\x4f\x50\x51\x52\x53\x54"
        eps_packet = [122,123,221,231,198,223]
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
	log_inbound_packet(packet_data)


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
