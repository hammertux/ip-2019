from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ipv4
from ryu.lib.packet import arp
from ryu.lib.packet import ether_types


class LearningSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(LearningSwitch13, self).__init__(*args, **kwargs)

        # Initialize mac address table
        self.mac_to_port = {}

    # Handle the event that switches report to the controller
    # their feature configurations
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Install the table-miss flow entry
        # If a packet cannot be forwarded by matching any of the
        # entries in the flow-table, this rule allows the packet
        # to be forwarded to the controller.
        # Note that the priority is the lowest, i.e., 0.

	PRIORITY = 0 # priority const value
	match = parser.OFPMatch() # Installs a flow

	actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
	self.record_flow(datapath, PRIORITY, match, actions)


    def record_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    # Handle the packet_in event
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Get Datapath ID to identify OpenFlow switches
        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        # --------------------------------------------------------
        # Your code starts here: You should first implement the
        # learning switch logic. The learning switch logic
        # consists of two components:
        # * Learn destination MAC and update switch flow table
        # * Send a packet_out message for the received packet_in
        # Once the learning switch is running, implement an IP
        # packet blocker on specified switches to certain
        # destinations.
        # --------------------------------------------------------
        # learn a mac address to avoid FLOOD next time.

        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
	dst = eth.dst
        src = eth.src

	# seen in https://github.com/osrg/ryu/blob/v4.4/ryu/app/simple_switch_13.py
        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return

	# check if ARP protocol, in this case learn, forward and don't install flow
	arppkt = pkt.get_protocol(arp.arp)
	if arppkt:
		if dst in self.mac_to_port[dpid]:
            		out_port = self.mac_to_port[dpid][dst]
        	else:
            		out_port = ofproto.OFPP_FLOOD
		actions = [parser.OFPActionOutput(out_port)]
		data = None
        	if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            		data = msg.data

        	out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        	datapath.send_msg(out)
		return


        # implement ip-level filter
	ip = pkt.get_protocols(ipv4.ipv4)
        if len(ip):
	    # print(ip)
            ip = ip[0]
            if ip.dst == '10.0.0.4':
                print("dropping packet to h4")
                return

        dst = eth.dst
        src = eth.src

        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]


	# at this point only the packets that are not directed towards h4 are present, can install flow
	if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.record_flow(datapath, 1, match, actions, msg.buffer_id)
                return
            else:
                self.record_flow(datapath, 1, match, actions)


	# send the packet
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)
