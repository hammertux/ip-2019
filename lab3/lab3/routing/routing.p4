/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>
#define ETHERTYPE_IPV4 0x800



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

struct headers {
	ethernet_t              ethernet;
	ipv4_t                  ipv4;
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

	}


	action drop() 
	{
        	mark_to_drop(standard_metadata);
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
     apply {  }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {  }
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
