from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ipv4


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
		self.add_flow(datapath, PRIORITY, match, actions)


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






