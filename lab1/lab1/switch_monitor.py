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

		self.datapaths = {}

		self.monitor_thread = hub.spawn(self._monitor)

	@set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
	def _state_change_handler(self, ev):
		datapath = ev.datapath
		state = ev.state

		if state == MAIN_DISPATCHER:
			if datapath.id not in self.datapaths:
				self.datapaths[datapath.id] = datapath
		else:
			if datapath.id == DEAD_DISPATCHER:
				del self.datapaths[datapath.id]

	def _monitor(self):

		while True:
			for dp in self.datapaths.values():
				self._request_stats(dp)
			hub.sleep(5)

	def _request_stats(self, datapath):
		self.logger.debug('send stats request: %016x', datapath.id)
		ofproto = datapath.ofproto
		parser = datapath.ofproto_parser

		request = parser.OFPFlowStatsRequest(datapath)
		datapath.send_msg(request)

		# Handle flow stats information from the datapaht
	@set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
	def _flow_stats_reply_handler(self, ev):

		body = ev.msg.body
		dpid = ev.msg.datapath.id

		# need to monitor datapath 1 and datapath 2
		for flow in body:
			#if dpid == 1:
				match = flow.match
				if flow.priority != 0 and (match['in_port'] == 1 and dpid == 1):
					self.logger.info('Incoming from h1 datapath         '
                     				'in-port  eth-dst           '
                     				'out-port packets')

                			self.logger.info('---------------- ---------------- '
                     				'-------- ----------------- '
                     				'-------- -------- ')
					self.logger.info('%016x %8x %17s %8x %8d',
                                	ev.msg.datapath.id,
                                	flow.match['in_port'],
                                	flow.match['eth_dst'],
                                	flow.instructions[0].actions[0].port,
                                	flow.packet_count)
				if flow.priority != 0 and (dpid == 2 and flow.instructions[0].actions[0].port == 3):
					self.logger.info('Outgoing to h3 datapath         '
                                                'in-port  eth-dst           '
                                                'out-port packets')

                                        self.logger.info('------------------ ---------------- '
                                                '-------- ----------------- '
                                                '-------- -------- ')
					self.logger.info('%016x %8x %17s %8x %8d',
                                        ev.msg.datapath.id,
                                        flow.match['in_port'],
                                        flow.match['eth_dst'],
                                        flow.instructions[0].actions[0].port,
                                        flow.packet_count)

