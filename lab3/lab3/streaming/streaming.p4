/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

#define ETHERTYPE_IPV4 0x800
#define IP_PROTOCOLS_UDP 17
#define RTP_PORT 5002



/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/


typedef bit<9>  egressSpec_t;
typedef bit<48> mac_addr_t;
typedef bit<32> ipv4_addr_t;

header ethernet_t {
	mac_addr_t dst;
	mac_addr_t src;
	bit<16>   ether_type;
}

header ipv4_t {
	bit<4>    version;
	bit<4>    ihl;
	bit<8>    diffserv;
	bit<16>   totalLen;
	bit<16>   identification;
	bit<3>    flags;
	bit<13>   fragOffset;
	bit<8>    ttl;
	bit<8>    protocol;
	bit<16>   hdrChecksum;
	ipv4_addr_t srcAddr;
	ipv4_addr_t dstAddr;
}

header udp_t {

 bit<16>  src;
 bit<16>  dst;
 bit<16>  len;
 bit<16>  checksum;
}


header rtp_t {
 bit<2>   version;
 bit<1>   padding;
 bit<1>   extension;
 bit<4>   CSRC_count;
 bit<1>   marker;
 bit<7>   payload_type;
 bit<16>  sequence_number;
 bit<32>  timestamp;
 bit<32>  SSRC;
}

struct headers {
	ethernet_t              ethernet;
	ipv4_t                  ipv4;
  udp_t                   udp;
  rtp_t                   rtp;
}

struct metadata {
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
		inout metadata meta,
		inout standard_metadata_t standard_metadata)
{
	state start {
		transition parse_ethernet;
	}

	state parse_ethernet {
		packet.extract(hdr.ethernet);
		transition select(hdr.ethernet.ether_type) {
			ETHERTYPE_IPV4: parse_ipv4;
			default: reject;
		}
	}


	state parse_ipv4 {
		packet.extract(hdr.ipv4);
		transition accept;
    		
		/*transition select(hdr.ipv4.protocol) {
        		IP_PROTOCOLS_UDP : parse_udp;
    			default: accept;
    		}*/
	}


  state parse_udp {
		packet.extract(hdr.udp);

    		transition select(hdr.udp.dst) {
			RTP_PORT: parse_rtp;
			default: accept;
		}
	}


  state parse_rtp {
		packet.extract(hdr.rtp);
		transition accept;
	}

}





/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/



control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {


	action ipv4_forward(mac_addr_t dstAddr, egressSpec_t port)
	{
		hdr.ethernet.dst = dstAddr;
		hdr.ethernet.src = hdr.ethernet.dst;
		standard_metadata.egress_spec = port;
		hdr.ipv4.ttl = hdr.ipv4.ttl - 1;

	}


	action drop()
	{
        	mark_to_drop(standard_metadata);
  }

  action multicast_forward()
  {

  }

	table ipv4_lpm {
		key = {
        		hdr.ipv4.dstAddr : lpm;
    		}
    		actions = {
        		ipv4_forward;
			drop;
    		}
    		size = 1024;
		//default_action = ipv4_forward();
	}


   // apply(ipv4_lpm);
    apply {
		ipv4_lpm.apply();
	}
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {  }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
     apply {
	update_checksum(
		hdr.ipv4.isValid(),
		{
			hdr.ipv4.version,
			hdr.ipv4.ihl,
			hdr.ipv4.diffserv,
			hdr.ipv4.totalLen,
			hdr.ipv4.identification,
			hdr.ipv4.flags,
			hdr.ipv4.fragOffset,
			hdr.ipv4.ttl,
			hdr.ipv4.protocol,
			hdr.ipv4.srcAddr,
			hdr.ipv4.dstAddr
		},
		hdr.ipv4.hdrChecksum,
		HashAlgorithm.csum16
	);

     }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply
    {
      packet.emit(hdr.ethernet);
      packet.emit(hdr.ipv4);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
