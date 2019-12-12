#!/usr/bin/python
from scapy.all import sniff, sendp
from scapy.all import Packet
from scapy.all import ShortField, IntField, LongField, BitField
from scapy.all import RTP

import sys
import struct
import pdb

count = 0

def handle_pkt(pkt_in):
    pkt = str(pkt_in)
    # if len(pkt) < 12: return
    if pkt_in[0]["UDP"]:
        pkt_in[0]["UDP"].payload = RTP(pkt_in[0]["Raw"].load)   
        #pkt_in[0]["RTP"].show()
        #print(pkt_in[0]["RTP"].sourcesync)

	global count
	count = count + 1

	if count % 100 == 0:
		print(count)
        #sys.stdout.flush()

    # if msg_type < 4:
    # print pkt_in.show()
    

def main():
    sniff(filter="udp and port 5004",
            iface = "eth0",
          prn = lambda x: handle_pkt(x))

if __name__ == '__main__':
    main()
