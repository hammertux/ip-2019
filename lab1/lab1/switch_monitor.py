from operator import attrgetter

from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub

# This is the learning switch you have already created
# Now you extend the learning switch with monitoring capability
from learning_switch import LearningSwitch13


# The switch monitor function extends the learning switch
class SwitchMonitor13(LearningSwitch13):
	def __init__(self, *args, **kwargs):
		super(SwitchMonitor13, self).__init__(*args, **kwargs)

       	# Maintain a table for all the datapaths in the network
		self.datapaths = {}

        	# Start a new thread for monitoring
        	# The new thread excutes the function _monitor
		self.monitor_thread = hub.spawn(self._monitor)

    	# Handle state change event
    	# Register/Deregister a datapath
	@set_ev_cls(ofp_event.EventOFPStateChange,
                [MAIN_DISPATCHER, DEAD_DISPATCHER])
	def _state_change_handler(self, ev):
		datapath = ev.datapath
		state = ev.state

		if state == MAIN_DISPATCHER:
			if datapath.id not in self.datapaths:
				self.datapaths[datapath.id] = datapath
		else:
			if datapath.id == DEAD_DISPATCHER:
				del self.datapaths[datapath.id]
    
    
    
    # Request statistics information from all datapaths every 5s
	def _monitor(self):

		while True:
			for dp in self.datapaths.values():
				self._request_stats(dp)
					hub.sleep(5)

    	# Request statistics information from a datapath
	def _request_stats(self, datapath):
		self.logger.debug('send stats request: %016x', datapath.id)
		ofproto = datapath.ofproto
		parser = datapath.ofproto_parser

		request = parser.EventOFPFlowStatsRequest(datapath)
		datapath.send_msg(request)

		#request = parser.EventOFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
		#datapath.send_msg(request)

		# Handle flow stats information from the datapaht
	@set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
	def _flow_stats_reply_handler(self, ev):

		body = ev.msg.body
		dpid = ev.msg.datapath.id

        	# --------------------------------------------------------
        	# Your code starts here
        	# Monitor the specified ports on two switches:
        	# dpid=1 and dpid=2
        	# --------------------------------------------------------
		for flow in body:
			if dpid == 1 || dpid == 2:
				self.logger.info(dpid + ' -- ' + flow.match["in_port"])












