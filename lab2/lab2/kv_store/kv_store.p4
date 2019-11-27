#include <core.p4>
#include <v1model.p4>

#define ETHERTYPE_IPV4 0x800
#define KV_STORE_SIZE 1000
#define DEFAULT_PREAMBLE 1

#define TYPE_GET_REQ 0
#define TYPE_PUT_REQ 1
#define TYPE_GET_ANS 2
#define TYPE_PUT_ANS 3

typedef bit<64> preamble_t;
typedef bit<8> type_t;
typedef bit<32> key_t;
typedef bit<32> value_t;
typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header pckt_t {
	preamble_t preamble;
	type_t type;
	key_t key;
	value_t value;
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
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

struct metadata {
}

struct headers {
	pckt_t pckt;
	ethernet_t eth;
	ipv4_t ipv4;
}

/*************************************************************************
 ***********************  P A R S E R  ***********************************
 *************************************************************************/

register <value_t>(KV_STORE_SIZE) kv_regs;

parser my_parser(packet_in pckt,
		out headers hdr,
		inout metadata meta,
		inout standard_metadata_t std_meta)
{
	state start {
		transition parse_pckt;
	}

	/* state parse_eth {
		pckt.extract(hdr.eth);
		
		transition select(hdr.eth.etherType)
		{
			ETHERTYPE_IPV4: parse_ipv4;
			default: accept;
		}
	}

	state parse_ipv4 {
		pckt.extract(hdr.ipv4);
		
		transition accept;		
	} */

	state parse_pckt
	{
		pckt.extract(hdr.pckt);
		transition select(hdr.pckt.preamble)
		{
			DEFAULT_PREAMBLE: accept; 
			default: reject;
		}
	}


}


/*************************************************************************
 **************  I N G R E S S   P R O C E S S I N G   *******************
 *************************************************************************/

control my_ingress(inout headers hdr,
		   inout metadata meta,
		   inout standard_metadata_t std_meta)
{
	value_t tmp;
	/*switch(hdr.pckt.type)
	{
		TYPE_GET_REQ: get_val(hdr.pckt.key, tmp);
		TYPE_PUT_REQ: put_val(hdr.pckt.key, hdr.pckt.value);
		
	}*/
	
	action get_val(in key_t key, out value_t val)
	{
		kv_regs.read(val, key);
	}

	action put_val(in key_t key, in value_t val)
	{
		kv_regs.write(key, val);
	}


	apply
	{
		if (hdr.pckt.type == TYPE_GET_REQ)
		{
			get_val(hdr.pckt.key, tmp);
		}
		else
		{
			put_val(hdr.pckt.key, hdr.pckt.value);
		}

	}
}

/*************************************************************************
 **************  E G R E S S   P R O C E S S I N G   *********************
 *************************************************************************/

control my_egress(inout headers hdr,
		  inout metadata meta,
		  inout standard_metadata_t std_meta)
{
	apply {  }
}



control my_deparser(packet_out pckt, in headers hdr)
{
	apply{}
}




/*************************************************************************
 ************   C H E C K S U M    V E R I F I C A T I O N   *************
 *************************************************************************/
control my_verify_checksum(inout headers hdr,
                         inout metadata meta) {
    apply { }
}



/*************************************************************************
 *************   C H E C K S U M    C O M P U T A T I O N   **************
 *************************************************************************/

control my_compute_checksum(inout headers hdr, inout metadata meta) {
    apply { }
}


V1Switch(
my_parser(),
my_verify_checksum(),
my_ingress(),
my_egress(),
my_compute_checksum(),
my_deparser()
) main;
