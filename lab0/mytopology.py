"""Custom topology example

Two directly connected switches plus a host for each switch:

   host --- switch --- switch --- host

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo

class MyTopo( Topo ):
    "Simple topology example."

    def __init__( self ):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        h1 = self.addHost( 'h1' )
        h2 = self.addHost( 'h2' )
	h3 = self.addHost( 'h3' )
	h4 = self.addHost( 'h4' )
        s1 = self.addSwitch( 's1' )
        s2 = self.addSwitch( 's2' )

        # Add links
        self.addLink( h1, s1, bw=15, delay='10ms' )
	self.addLink( h2, s1, bw=15, delay='10ms' )
	self.addLink( h3, s2, bw=15, delay='10ms' )
	self.addLink( h4, s2, bw=15, delay='10ms' )
	self.addLink( s1, s2, bw=20, delay='45ms' )


topos = { 'mytopo': ( lambda: MyTopo() ) }
